# -*- coding: utf-8 -*-
"""
Build alice-production.json = the karaoke PERFORMANCE grammar:
base-grammar pages (text + illustration) + per-page LibriVox word timings
(align-pagewords.json) + the merged-audio URL. Viewer-compatible schema
(same shape view.html / viewer.html render).
"""
import json, os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = json.load(open(os.path.join(HERE,"data","base-grammar.json"), encoding="utf-8"))
A = json.load(open(os.path.join(HERE,"data","align-pagewords.json"), encoding="utf-8"))
AUDIO = "https://pub-71ebbc217e6247ecacb85126a6616699.r2.dev/grammar-illustrations/alice-in-wonderland/audio/librivox/wonderland-complete.mp3"

# Crop ranges = the repeated chapter boilerplate, detected by align_pagewords.py
# (leading/trailing unmatched runs per chapter). Merge runs separated by a short
# gap so each chapter join becomes ONE clean playback seek (body -> body).
MERGE_GAP = 8.0
def merged_crops():
    raw = sorted([[c[0], c[1]] for c in A.get("_crops", [])])
    out = []
    for s, e in raw:
        if out and s - out[-1][1] <= MERGE_GAP:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out

crops = merged_crops()
def in_crop(t):
    for s,e in crops:
        if s - 0.01 <= t < e - 0.001:
            return True
    return False

items = []
matched = 0
cropped_words = 0
for i, it in enumerate(G["items"]):
    al = A.get(str(i), {})
    item = {
        "id": it.get("id"),
        "name": it.get("name"),
        "number": it.get("number"),
        "symbol": it.get("symbol",""),
        "category": it.get("category",""),
        "keywords": it.get("keywords",[]),
        "image_url": it.get("image_url",""),
        "sections": it.get("sections") or {},
        "section_labels": it.get("section_labels") or {},
        "composite_of": it.get("composite_of"),
        "sort_order": i,
    }
    words = al.get("words") or []
    if words:
        kept = [w for w in words if not in_crop(w["start"])]
        cropped_words += len(words) - len(kept)
        if kept:
            item["performance"] = {
                "start_sec": kept[0]["start"],
                "end_sec": kept[-1]["end"],
                "audio_visible": False,
                "words": kept,
            }
            matched += 1
    items.append(item)

out = {
    "id": "alice-karaoke-performance",
    "name": "Alice's Adventures in Wonderland — Karaoke Performance",
    "description": ("A page-by-page karaoke performance of Lewis Carroll's *Alice's "
        "Adventures in Wonderland*. Public-domain LibriVox narration drives word-by-word "
        "highlighting over the illustrations; each page shows a plate from the 1864–1933 "
        "illustrated editions. Open in viewer.html for the synced reading."),
    "grammar_type": "sequence",
    "audio_url": AUDIO,
    "audio_duration_s": 9758.32,
    "audio_source": "LibriVox solo reader (public domain)",
    "crop_ranges": crops,
    "item_count": len(items),
    "items": items,
}
path = os.path.join(HERE,"data","alice-production.json")
json.dump(out, open(path,"w",encoding="utf-8"), ensure_ascii=False)
sz = os.path.getsize(path)
print("wrote", path, "(%.0f KB)" % (sz/1024))
print("items:", len(items), "| with karaoke timings:", matched, "| silent (cover/poem/end/text-only-no-window):", len(items)-matched)
print("\nchapter boilerplate crops (skipped in playback + karaoke):", len(crops), "| words cropped:", cropped_words)
for s,e in crops:
    print("  %7.1f -> %7.1f s  (%.1fs removed)" % (s, e, e-s))
# audio scenes ordered
scenes = sorted([(it["performance"]["start_sec"], it["performance"]["end_sec"], it["name"])
                 for it in items if it.get("performance")], key=lambda x:x[0])
print("audio scenes:", len(scenes), "first start %.1fs"%scenes[0][0], "last end %.1fs"%scenes[-1][1])
# check for big gaps/overlaps between consecutive scenes
gaps=[]
for a,b in zip(scenes, scenes[1:]):
    g = b[0]-a[1]
    if abs(g) > 3: gaps.append((round(a[1],1), round(b[0],1), round(g,1), b[2][:30]))
print("scene boundaries with >3s gap/overlap:", len(gaps))
for x in gaps[:8]: print("   end %.1f -> next start %.1f  (gap %+.1fs)  %s"%x)
