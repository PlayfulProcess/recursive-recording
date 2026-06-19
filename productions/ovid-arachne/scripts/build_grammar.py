# -*- coding: utf-8 -*-
"""Assemble the Arachne performance grammar (perform2 shape). One confirmed plate
(Baur 1703, the transformation) → through-image. Editorial principle: the text is
kept verbatim (don't erase Ovid), the plate shows the metamorphosis NOT the suicide
(don't depict/propagate), and a grammar-level content_note names it (don't erase)."""
import json, os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP  = "C:/Users/ferna/AppData/Local/Temp/ovid"
PAD  = 0.25
T = json.load(open(os.path.join(HERE, "data", "text.json"), encoding="utf-8"))
A = json.load(open(os.path.join(TMP, "alignment.json"), encoding="utf-8"))
aln = {p["idx"]: p for p in A["passages"]}

R2 = "https://pub-71ebbc217e6247ecacb85126a6616699.r2.dev/"
AUDIO  = R2 + "grammar-illustrations/ovid-arachne/audio/narration.mp3"
BAUR   = R2 + "grammar-illustrations/ovid-arachne/baur-1703/arachne-pl55.jpg"
CREDIT = "Johann Wilhelm Baur, 1703 (UVM Ovid Project)"

items, withperf = [], 0
for p in T["passages"]:
    i = p["idx"]; al = aln.get(i, {})
    it = {
        "id": "arac-%02d" % i, "name": p["beat"], "number": i + 1, "symbol": p["book_line"],
        "category": "content", "keywords": ["Arachne", "Minerva", "weaving"], "image_url": BAUR,
        "sections": {"Narration": p["text"],
                     "Reference": "Metamorphoses " + p["book_line"] + " — Brookes More (1922)"},
        "metadata": {"credit": CREDIT, "page_number": i + 1}, "sort_order": i,
    }
    # name the self-harm beats in the data (don't erase) — viewer may surface later
    if i in (11, 12, 13):
        it["metadata"]["content_flag"] = "self-harm"
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
    "id": "ovid-arachne",
    "name": "Arachne & Minerva — Ovid (Brookes More)",
    "description": ("Ovid's *Metamorphoses* VI.1–145 — the mortal weaver who out-weaves a goddess — in "
        "the public-domain Brookes More (1922) verse, LibriVox narration, word-by-word karaoke, with "
        "Baur's 1703 engraving of the transformation. A recursive-recording performance."),
    "grammar_type": "sequence", "default_preview": "performance", "is_published": False,
    "tags": ["ovid", "metamorphoses", "arachne", "public-domain", "performance"],
    "metadata": {"audio": AUDIO, "total_sec": round(A["total"] + 2 * PAD, 2), "crop_ranges": [],
                 "audio_source": "LibriVox (public domain) · Brookes More (1922) translation",
                 "reading_style": "full-prose-karaoke",
                 "content_note": ("Ovid's account includes Arachne's self-harm (she hangs herself before "
                     "Minerva transforms her into a spider). The text is kept verbatim as public-domain "
                     "Ovid; the illustration depicts the transformation, not the act. Named here, not erased.")},
    "item_count": len(items), "items": items,
}
out = os.path.join(HERE, "ovid-arachne-performance.json")
json.dump(grammar, open(out, "w", encoding="utf-8"), ensure_ascii=False)
print("wrote", out)
print("items: %d | with karaoke: %d | total_sec: %.1f | first word @ %.2fs"
      % (len(items), withperf, grammar["metadata"]["total_sec"], items[0]["performance"]["words"][0]["start"]))
