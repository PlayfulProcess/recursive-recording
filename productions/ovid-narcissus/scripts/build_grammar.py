# -*- coding: utf-8 -*-
"""
Assemble the playable Narcissus performance grammar (perform2 shape) from the
verbatim text + the Whisper alignment + the R2 audio clip + the 2 PD plates.

Plates: only two are URL-confirmed for v1 (Tempesta 1606 + Baur 1703), so Tempesta
is the through-image (carried forward) and Baur takes the closing transformation —
scene-precise timing comes when the Solis/Salomon plates are sourced.
"""
import json, os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP  = "C:/Users/ferna/AppData/Local/Temp/ovid"
PAD  = 0.25   # align_clip padded the clip by 0.25s at the head; shift word times to match

T = json.load(open(os.path.join(HERE, "data", "text.json"), encoding="utf-8"))
A = json.load(open(os.path.join(TMP, "alignment.json"), encoding="utf-8"))
aln = {p["idx"]: p for p in A["passages"]}

R2 = "https://pub-71ebbc217e6247ecacb85126a6616699.r2.dev/"
AUDIO    = R2 + "grammar-illustrations/ovid-narcissus/audio/narration.mp3"
TEMPESTA = R2 + "grammars/1781831662497-ueml0dsr95s.jpg"   # uploaded via MCP set_item_image
BAUR     = R2 + "grammars/1781831683019-frifggw2yi4.jpg"
plates = {0: (TEMPESTA, "Antonio Tempesta, 1606 (Met, Open Access)"),
          22: (BAUR,    "Johann Wilhelm Baur, 1703 (UVM Ovid Project)")}

items, lastimg, lastcredit, withperf = [], "", "", 0
for p in T["passages"]:
    i = p["idx"]; al = aln.get(i, {})
    if i in plates:
        lastimg, lastcredit = plates[i]
    it = {
        "id": "narc-%02d" % i, "name": p["beat"], "number": i + 1, "symbol": p["book_line"],
        "category": "content", "keywords": ["Narcissus", "Echo"], "image_url": lastimg,
        "sections": {"Narration": p["text"],
                     "Reference": "Metamorphoses " + p["book_line"] + " — Brookes More (1922)"},
        "metadata": {"credit": lastcredit, "page_number": i + 1}, "sort_order": i,
    }
    if al.get("words"):
        it["performance"] = {
            "start_sec": round(al["start_sec"] + PAD, 3), "end_sec": round(al["end_sec"] + PAD, 3),
            "video_visible": False, "reading_style": "full-prose-karaoke",
            "words": [{"w": w["w"], "start": round(w["start"] + PAD, 3), "end": round(w["end"] + PAD, 3)}
                      for w in al["words"]],
        }
        withperf += 1
    items.append(it)

grammar = {
    "id": "ovid-echo-narcissus",
    "name": "Echo & Narcissus — Ovid (Brookes More)",
    "description": ("Ovid's *Metamorphoses* III.339–510 — the mirror myth — in the public-domain "
        "Brookes More (1922) verse, read by a LibriVox narrator, with word-by-word karaoke and engravings "
        "from the 1606–1703 illustrated editions. A recursive-recording performance."),
    "grammar_type": "sequence", "default_preview": "performance", "is_published": False,
    "tags": ["ovid", "metamorphoses", "narcissus", "public-domain", "performance"],
    "metadata": {"audio": AUDIO, "total_sec": round(A["total"] + 2 * PAD, 2), "crop_ranges": [],
                 "audio_source": "LibriVox (public domain) · Brookes More (1922) translation",
                 "reading_style": "full-prose-karaoke"},
    "item_count": len(items), "items": items,
}
out = os.path.join(HERE, "ovid-narcissus-performance.json")
json.dump(grammar, open(out, "w", encoding="utf-8"), ensure_ascii=False)
print("wrote", out)
print("items: %d | with karaoke: %d | total_sec: %.1f | audio: %s"
      % (len(items), withperf, grammar["metadata"]["total_sec"], bool(grammar["metadata"]["audio"])))
print("plates: Tempesta(through) -> Baur@22 | first word @ %.2fs" % items[0]["performance"]["words"][0]["start"])
