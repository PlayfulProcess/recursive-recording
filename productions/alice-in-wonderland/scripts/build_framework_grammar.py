# -*- coding: utf-8 -*-
"""
Reshape alice-production.json -> data/alice-performance.json in the recursive-tarot
recording-framework conventions (recording/docs/performance-grammar.md + sequence-format.md):

  grammar_type: "sequence", default_preview: "performance"
  metadata.audio       -> single narration track (drives perform.html's global clock)
  metadata.total_sec   -> total timeline length
  metadata.crop_ranges -> [[s,e],...] boilerplate to skip (chapter-title reading)
  items[].performance  -> { start_sec, end_sec, video_visible:false, words:[{w,start,end}] }

Full-prose per-word karaoke: each item keeps its real LibriVox word timings in
performance.words (the framework's perform.html, enhanced, highlights word-by-word).
Output is plain DATA — no recording needed; perform.html / recursive.eco are the player.
"""
import json, os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = json.load(open(os.path.join(HERE, "data", "alice-production.json"), encoding="utf-8"))
OUT  = os.path.join(HERE, "data", "alice-performance.json")

items = []
for it in SRC["items"]:
    o = {
        "id": it.get("id"),
        "name": it.get("name"),
        "sort_order": it.get("sort_order"),
        "category": it.get("category", ""),
        "image_url": it.get("image_url") or None,
        "keywords": it.get("keywords", []),
        "sections": it.get("sections") or {},
        "metadata": {"page_number": it.get("number"), "symbol": it.get("symbol", "")},
    }
    pf = it.get("performance")
    if pf and pf.get("words"):
        o["performance"] = {
            "start_sec": pf["start_sec"],
            "end_sec": pf["end_sec"],
            "video_visible": False,          # a reading: audio + image + word overlays
            "reading_style": "full-prose-karaoke",
            "words": pf["words"],            # real LibriVox per-word timings
        }
    items.append(o)

grammar = {
    "name": SRC.get("name", "Alice's Adventures in Wonderland — Performance"),
    "description": SRC.get("description", ""),
    "grammar_type": "sequence",
    "default_preview": "performance",
    "is_published": False,
    "tags": ["alice", "carroll", "karaoke", "public-domain", "librivox"],
    "metadata": {
        "audio": SRC.get("audio_url"),
        "total_sec": SRC.get("audio_duration_s"),
        "crop_ranges": SRC.get("crop_ranges", []),
        "audio_source": SRC.get("audio_source", "LibriVox (public domain)"),
        "reading_style": "full-prose-karaoke",
    },
    "item_count": len(items),
    "items": items,
}

json.dump(grammar, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
sz = os.path.getsize(OUT)
with_perf = sum(1 for i in items if i.get("performance"))
print("wrote %s (%.0f KB)" % (OUT, sz/1024))
print("items: %d | with karaoke timings: %d | audio: %s | total_sec: %.0f | crops: %d"
      % (len(items), with_perf, bool(grammar['metadata']['audio']),
         grammar['metadata']['total_sec'], len(grammar['metadata']['crop_ranges'])))
