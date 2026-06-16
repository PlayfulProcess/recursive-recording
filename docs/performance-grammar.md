# Performance grammar — the output shape

A recording = one **`sequence` grammar**, `default_preview: "performance"`. Each **item is one
passage/step**; recursive.eco already renders `performance` objects (timestamped clip + overlays
+ audio), so the recording is just data the existing viewer plays. Built by
`pipeline/assemble_performance.py`.

## Item shape
```jsonc
{
  "id": "p03-the-little-door",
  "name": "The Little Door",
  "image_url": "…the (repaired) illustration…",
  "sections": { "Text": "…", "Narration": "…", "Illustration prompt": "…" },
  "metadata": { "passage_index": 2, "reading_style": "karaoke-allcaps",
                "illustration_status": "regenerated" },
  "performance": {
    "start_sec": 0, "end_sec": 14.2,
    "video_visible": false,          // audio + image + text overlays (a reading, not a video)
    "volume": 1.0,
    "cover_image_url": "…",
    "background_audio": { "youtube_video_id": "…", "volume": 0.3 },
    "overlays": [                     // ONE per karaoke line, timed
      { "kind": "text", "content": "ALICE CAME TO A LONG HALL.",
        "start_sec": 0.0, "end_sec": 2.0, "x_pct": 8, "y_pct": 64, "width_pct": 84 },
      { "kind": "text", "content": "THEN SHE FOUND A TINY DOOR.",
        "start_sec": 2.45, "end_sec": 4.7, "x_pct": 8, "y_pct": 64, "width_pct": 84 }
    ]
  }
}
```

## Timing
`assemble_performance.py` estimates line timings from a kid-paced word rate. **When real
voice-over audio exists, replace the estimates with the true clip boundaries** (and, ideally,
per-word marks from the TTS engine for exact karaoke sync).

## Two modes
- **Reading (Alice):** `video_visible:false`; the "clip" is the narration audio over the
  illustration; overlays are the karaoke lines.
- **Screencast (Vibe Coding 101):** `video_visible:true`; the clip is the recorded terminal;
  overlays caption the step. Same grammar, same viewer.

## Publishing
Create via recursive-eco MCP `create_grammar(grammar_type:"sequence")` → `add_items(...)`, or
commit the `grammar.json` statically. The field conventions (singular `start_sec`/`end_sec`,
`youtube_video_id`) follow recursive-tarot's `GRAMMAR_FORMAT.md` "Performance object".
