# -*- coding: utf-8 -*-
"""
Align each base-grammar PAGE to a contiguous range of LibriVox word timings.

Both inputs are the SAME book text in the SAME order, so we align per chapter
(bounded drift) with difflib. Output: per page -> {start_sec, end_sec, words:[{w,start,end}]}
with ABSOLUTE times into wonderland-complete.mp3. Pages with no audio (cover,
opening poem, THE END) are emitted with words:[] and no start/end.
"""
import json, re, os, sys
from difflib import SequenceMatcher
from collections import defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAMMAR = os.path.join(HERE, "data", "base-grammar.json")
MANIFEST = r"C:\Users\ferna\OneDrive\Documentos\GitHub\recursive-kids-stories-club\books\alice-in-wonderland\audio\karaoke-manifest.json"
OUT = os.path.join(HERE, "data", "align-pagewords.json")

CURLY = {"‘":"'","’":"'","“":'"',"”":'"',"—":" ","–":" ","…":" "}
def clean(s):
    for k,v in CURLY.items(): s = s.replace(k,v)
    return s
def norm_tokens(text):
    """Return list of (normalized_token, char_ok) — normalized = lowercase a-z0-9' """
    text = clean(text).lower()
    raw = re.findall(r"[a-z0-9']+", text)
    out = [t.strip("'") for t in raw]
    return [t for t in out if t]

def main():
    g = json.load(open(GRAMMAR, encoding="utf-8"))
    items = g["items"]
    man = json.load(open(MANIFEST, encoding="utf-8"))
    chapters = man["chapters"]  # {"1": {words:[{word,start,end}]}, ...}

    # page index -> chapter number
    def page_chapter(it):
        m = re.search(r"Ch(?:apter)?\.?\s*(\d+)", it.get("name") or "")
        return int(m.group(1)) if m else None

    by_chapter = defaultdict(list)   # ch -> [(page_idx, item)]
    for i, it in enumerate(items):
        ch = page_chapter(it)
        if ch is not None and str(ch) in chapters:
            by_chapter[ch].append((i, it))

    result = {}   # page_idx(str) -> {start,end,words,nwords,matched}
    # default: every page no-audio
    for i, it in enumerate(items):
        result[str(i)] = {"start_sec": None, "end_sec": None, "words": [], "matched": 0,
                          "page_tokens": len(norm_tokens((it.get("sections") or {}).get("Page Text","")))}

    # Crop ranges = the spoken boilerplate the LibriVox reader repeats at every
    # chapter join ("...End of chapter N. Alice's Adventures in Wonderland by
    # Lewis Carroll. Chapter N+1, <Title>..."). It is exactly the text that
    # matches NO real page body. That boilerplate sits at each chapter's LEADING
    # edge (book title + "Chapter N" + chapter title) and TRAILING edge ("End of
    # chapter N..." + reader credit). Songs / minor mismatches are INTERIOR and
    # are never cropped. We align only against true body pages (content/text-only)
    # so the divider's "ALICE'S ADVENTURES IN WONDERLAND" text can't absorb the
    # spoken book-title boilerplate.
    CONTENT_CATS = {"content", "text-only"}
    crops_all = []
    report = []
    for ch, pages in sorted(by_chapter.items()):
        mwords = chapters[str(ch)]["words"]
        mtok = [norm_tokens(w["word"]) for w in mwords]   # each manifest word -> list (usually 1) tokens
        # flatten manifest tokens with backref to word index
        flat_m, m_ref = [], []
        for wi, toks in enumerate(mtok):
            for t in toks:
                flat_m.append(t); m_ref.append(wi)

        # page token stream for this chapter (real body pages only), tagged by page_idx
        body_pages = [(pi, it) for (pi, it) in pages if it.get("category") in CONTENT_CATS]
        flat_p, p_ref = [], []
        for (pi, it) in body_pages:
            for t in norm_tokens((it.get("sections") or {}).get("Page Text","")):
                flat_p.append(t); p_ref.append(pi)

        if not flat_p or not flat_m:
            continue

        sm = SequenceMatcher(a=flat_m, b=flat_p, autojunk=False)
        # manifest-token index -> page_idx (None until assigned)
        mtoken_page = [None]*len(flat_m)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                for k in range(i2-i1):
                    mtoken_page[i1+k] = p_ref[j1+k]
            # for replace/delete we leave None -> carry-forward below
        # carry-forward / back-fill the Nones so every manifest token gets a page
        last = None
        for k in range(len(mtoken_page)):
            if mtoken_page[k] is None: mtoken_page[k] = last
            else: last = mtoken_page[k]
        if not body_pages:
            continue
        # back-fill leading Nones with first known
        firstknown = next((p for p in mtoken_page if p is not None), body_pages[0][0])
        mtoken_page = [p if p is not None else firstknown for p in mtoken_page]

        # manifest WORD -> page = page of its first token
        word_page = {}
        for ti, wi in enumerate(m_ref):
            if wi not in word_page:
                word_page[wi] = mtoken_page[ti]

        # group words by page
        per_page = defaultdict(list)
        for wi, w in enumerate(mwords):
            pg = word_page.get(wi)
            if pg is None: continue
            per_page[pg].append(w)

        for pg, ws in per_page.items():
            ws = sorted(ws, key=lambda x: x["start"])
            words = [{"w": w["word"], "start": round(w["start"],3), "end": round(w["end"],3)} for w in ws]
            result[str(pg)] = {
                "start_sec": round(ws[0]["start"],3),
                "end_sec": round(ws[-1]["end"],3),
                "words": words,
                "matched": len(words),
                "page_tokens": result[str(pg)]["page_tokens"],
            }
        # ---- crop detection: LEADING + TRAILING unmatched runs only ----
        # (chapter intro/title before the body, outro/credit after it). Interior
        # unmatched runs — songs like "Beautiful Soup", minor mishears — are kept.
        word_matched = [False]*len(mwords)
        for tag,i1,i2,j1,j2 in sm.get_opcodes():
            if tag == "equal":
                for k in range(i1,i2):
                    word_matched[m_ref[k]] = True
        N = len(mwords)
        fm = next((i for i in range(N) if word_matched[i]), None)        # first matched (body) word
        lm = next((i for i in range(N-1,-1,-1) if word_matched[i]), None) # last matched (body) word
        if fm is None:
            continue
        if fm >= 2:   # leading boilerplate: book title + "Chapter N" + chapter title
            crops_all.append([round(mwords[0]["start"],3), round(mwords[fm]["start"],3),
                              " ".join(w["word"] for w in mwords[:fm])[:70]])
        if lm is not None and lm <= N-3:  # trailing boilerplate: "End of chapter N..." + reader credit
            crops_all.append([round(mwords[lm+1]["start"],3), round(mwords[N-1]["end"],3),
                              " ".join(w["word"] for w in mwords[lm+1:])[:70]])

        # chapter report: matched ratio
        op = sm.get_opcodes()
        eq = sum((i2-i1) for tag,i1,i2,j1,j2 in op if tag=="equal")
        report.append((ch, len(flat_p), len(flat_m), eq, round(100*eq/max(1,len(flat_p)),1)))

    crops_all.sort()
    result["_crops"] = crops_all
    json.dump(result, open(OUT,"w",encoding="utf-8"), ensure_ascii=False)
    print("wrote", OUT)
    print("\n=== %d crop runs (leading/trailing chapter boilerplate) ===" % len(crops_all))
    for cs,ce,txt in crops_all:
        print("  %8.1f -> %8.1f s (%4.1fs)  %s" % (cs, ce, ce-cs, txt))
    print("\nch | page_toks | mani_toks | equal | %page matched")
    for r in report:
        print("%2d | %9d | %9d | %5d | %5.1f%%" % r)
    # sanity: show a few pages
    print("\n=== sample page windows ===")
    for pi in [5,6,40,90,150]:
        r = result[str(pi)]; nm = (items[pi].get("name") or "")[:38]
        kt = " ".join(w["w"] for w in r["words"][:12])
        print("p%-3d %-38s %6.1f-%6.1fs  %3d words: %s" % (
            pi, nm, r["start_sec"] or -1, r["end_sec"] or -1, r["matched"], kt))

if __name__ == "__main__":
    main()
