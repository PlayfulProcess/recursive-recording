# -*- coding: utf-8 -*-
"""
Align the Whisper word stream (of Book-3 parts 08+09) to the 23 Brookes More
passages via difflib — finding the Narcissus span inside the larger audio — then
clip just that span and emit clip-relative per-word timings.

In:  /tmp/ovid/whisper.json (Whisper verbose_json, words[] with abs times in big.mp3)
     productions/ovid-narcissus/data/text.json (the 23 passages)
     /tmp/ovid/big.mp3 (full-quality concat)
Out: /tmp/ovid/alignment.json (S, E, total, per-passage {start_sec,end_sec,words[]} clip-relative)
     /tmp/ovid/narration.mp3 (the clipped Narcissus narration)
"""
import json, re, os, subprocess
from difflib import SequenceMatcher
from collections import defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = "C:/Users/ferna/AppData/Local/Temp/ovid"   # Git Bash /tmp/ovid in native-Windows form
W = json.load(open(TMP + "/whisper.json", encoding="utf-8"))
T = json.load(open(os.path.join(HERE, "data", "text.json"), encoding="utf-8"))
words = W["words"]

def norm(s):
    return re.sub(r"[^a-z0-9']", "", s.lower()).strip("'")

wn = [norm(w["word"]) for w in words]
ptok, pref = [], []
for p in T["passages"]:
    for t in re.findall(r"[A-Za-z0-9']+", p["text"]):
        n = norm(t)
        if n:
            ptok.append(n); pref.append(p["idx"])

sm = SequenceMatcher(a=wn, b=ptok, autojunk=False)
wpass = [None] * len(words)
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        for k in range(i2 - i1):
            wpass[i1 + k] = pref[j1 + k]

per = defaultdict(list)
for wi, pi in enumerate(wpass):
    if pi is not None:
        per[pi].append(words[wi])

allw = [w for pi in per for w in per[pi]]
if not allw:
    raise SystemExit("NO MATCH — Narcissus span not found in the audio transcript")
S = min(w["start"] for w in allw)
E = max(w["end"] for w in allw)

passages = []
for p in T["passages"]:
    ws = sorted(per.get(p["idx"], []), key=lambda x: x["start"])
    if ws:
        passages.append({"idx": p["idx"],
            "start_sec": round(ws[0]["start"] - S, 3), "end_sec": round(ws[-1]["end"] - S, 3),
            "words": [{"w": w["word"], "start": round(w["start"] - S, 3), "end": round(w["end"] - S, 3)} for w in ws]})
    else:
        passages.append({"idx": p["idx"], "start_sec": None, "end_sec": None, "words": []})

json.dump({"S": round(S, 3), "E": round(E, 3), "total": round(E - S, 3),
           "matched_words": len(allw), "whisper_words": len(words), "passages": passages},
          open(TMP + "/alignment.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# clip just the Narcissus span (small pre-roll so the first word isn't clipped)
pad = 0.25
subprocess.run(["ffmpeg", "-y", "-ss", str(max(0, S - pad)), "-to", str(E + pad),
                "-i", TMP + "/big.mp3", "-c:a", "libmp3lame", "-q:a", "4", TMP + "/narration.mp3"],
               check=True, stderr=subprocess.DEVNULL)

unmatched = [p["idx"] for p in passages if p["start_sec"] is None]
print("S=%.1fs E=%.1fs  span=%.1fs (%.1f min)  matched %d/%d words" %
      (S, E, E - S, (E - S) / 60, len(allw), len(words)))
print("passages with no words:", unmatched if unmatched else "none")
print("first passage:", passages[0]["start_sec"], "->", passages[0]["end_sec"],
      "|", " ".join(w["w"] for w in passages[0]["words"][:8]))
print("wrote /tmp/ovid/alignment.json + narration.mp3")
