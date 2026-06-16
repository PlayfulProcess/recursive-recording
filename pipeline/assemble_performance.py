# -*- coding: utf-8 -*-
"""assemble_performance.py — turn karaoke passages into a recursive.eco `sequence` grammar
where each passage is an item carrying a `performance` object with per-LINE timed text
overlays (the karaoke highlight track) + the illustration.

This is the bridge to recursive.eco: the output JSON can be created via the
recursive-eco MCP (`create_grammar` + `add_items`) or committed as a static grammar.
Timings here are ESTIMATED (a kid-paced reading rate); when a real voice-over audio file
exists, replace estimated start/end with the true clip boundaries.

  python3 pipeline/assemble_performance.py        # writes productions/alice-in-wonderland/grammar.json
"""
import json, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JSON = os.path.join(ROOT, "karaoke", "alice-passages.json")
OUT  = os.path.join(ROOT, "productions", "alice-in-wonderland", "grammar.json")

SEC_PER_WORD = 0.62      # kid-paced narration
LINE_GAP_SEC = 0.45      # pause between lines
PASSAGE_GAP  = 1.2       # pause between passages (page turn)

def line_timings(lines, t0=0.0):
    """Return (overlays, end_time): one text overlay per line with start/end seconds."""
    overlays, t = [], t0
    for li, line in enumerate(lines):
        dur = max(1.2, len(line.split()) * SEC_PER_WORD)
        overlays.append({
            "kind": "text",
            "content": line,                       # already ALL-CAPS in the source
            "start_sec": round(t, 2),
            "end_sec": round(t + dur, 2),
            "x_pct": 8, "y_pct": 64, "width_pct": 84,
        })
        t += dur + LINE_GAP_SEC
    return overlays, t

def build():
    data = json.load(open(JSON, encoding="utf-8"))
    items = []
    for i, p in enumerate(data["passages"]):
        overlays, end = line_timings(p["lines"])
        ill = p.get("illustration", {})
        items.append({
            "id": p["id"],
            "name": p.get("title", p["id"]),
            "sort_order": i,
            "category": "passage",
            "image_url": ill.get("image_url"),           # filled by the illustration step
            "keywords": ["alice", "karaoke", "chapter-1"],
            "sections": {
                "Text": " ".join(p["lines"]),
                "Narration": " ".join(l.capitalize() for l in p["lines"]),
                "Illustration prompt": ill.get("prompt", ""),
            },
            "metadata": {
                "passage_index": i,
                "reading_style": "karaoke-allcaps",
                "illustration_status": ill.get("status", "original"),
                "_svg_placeholder": bool(ill.get("svg")),
            },
            "performance": {
                "start_sec": 0,
                "end_sec": round(end, 2),
                "video_visible": False,                  # audio + image + text overlays
                "volume": 1.0,
                "cover_image_url": ill.get("image_url"),
                "background_audio": {"note": "low gentle music — set youtube_video_id/volume when chosen"},
                "overlays": overlays,
            },
        })
    grammar = {
        "name": data.get("title", "Alice — Karaoke Reader"),
        "description": "A karaoke-style ALL-CAPS narrated reading of Alice in Wonderland (Ch. I). "
                       "Each passage = one performance clip: illustration + voice-over + per-line "
                       "highlighted text. " + data.get("source", ""),
        "grammar_type": "sequence",
        "default_preview": "performance",
        "tags": ["alice", "kids", "karaoke", "reading", "public-domain"],
        "is_published": False,
        "items": items,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(grammar, open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    total = sum(it["performance"]["end_sec"] + PASSAGE_GAP for it in items)
    print(f"wrote {os.path.relpath(OUT, ROOT)} — {len(items)} passages, ~{total/60:.1f} min estimated")

if __name__ == "__main__":
    build()
