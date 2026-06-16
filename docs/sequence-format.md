# Sequence / program grammar

A **sequence** is an ordered playlist that the viewer at
[`viewers/sequence.html`](../viewers/sequence.html) plays back as a
performance: title cards that hold for a beat, then a cropped YouTube
clip, then another card, and so on. It is the same shape recursive.eco's
`view.html` plays, so a grammar authored here also plays there (and vice
versa) — but see **Importability** below for why the example file is
*named* so the recursive.eco GitHub importer ignores it.

This is a sibling of [`performance-grammar.md`](performance-grammar.md)
(the caption/overlay reading mode driven by a single global clock). The
difference:

| | `sequence` (this doc) | `performance` overlay mode |
|---|---|---|
| Model | discrete item playlist | one global clock |
| Media | many YouTube clips + cards | one image track (+ optional single audio) |
| Player | `viewers/sequence.html` | `viewers/perform.html` |
| Advances when | card_hold elapses / clip hits `end_sec` | global clock reaches each `start_sec` |

## Shape

A grammar object with an ordered `items[]`. Each item is one of two kinds.

### Card item — a held title screen

```jsonc
{
  "name": "Bandolim",            // shown large, centred; \n makes line breaks
  "category": "card",            // OR: simply having metadata.card_bg
  "sort_order": 0,               // playback order
  "metadata": {
    "card_bg": "#1e1b4b",        // any CSS background: a hex, OR
                                 //   "url('https://…/thumb.jpg') center/cover"
    "card_subtitle": "Live: DG", // optional small line under the title
    "card_hold_sec": 8           // dwell before auto-advancing (default 8)
  }
}
```

### Segment item — a cropped YouTube clip

```jsonc
{
  "name": "Ao vivo · Bandolim",
  "category": "segment",         // OR: metadata.item_type === "video"
  "sort_order": 1,
  "metadata": {
    "youtube_video_id": "T3AoGeR4Kwo"   // 11-char id (or metadata.video_url)
  },
  "performance": {
    "start_sec": 1,              // seek here on load
    "end_sec": 56,               // advance to the next item at this time
    "video_visible": true        // false → audio only, behind a cover image
  }
}
```

When `video_visible` is `false` the player shows a cover
(`performance.cover_image_url`, else the video's `hqdefault` thumbnail)
over the still-audible clip — useful for "play this recording while a
plate is on screen".

## Playback rules (what the viewer does)

- Items play in `sort_order`.
- **Card** → render the title screen, fill a progress sliver over
  `card_hold_sec`, then advance. The last item never auto-advances.
- **Segment** → load the YouTube IFrame player at `start_sec`, poll
  `getCurrentTime()` every 250 ms, and advance when it reaches `end_sec`
  (or when the clip naturally ENDs).
- **Auto** (on by default) chains items into a continuous performance.
  Turn it off to step manually with ⏮ / ⏭ (or ← / → / Space / Home).

Load any sequence with `?src=<url>` — for example
`viewers/sequence.html?src=../recording/examples/passarinho-sequence.json`
(the default).

## Importability — why the example lives in `recording/examples/`

recursive.eco's GitHub-app importer scans a repo for grammar files to
pull into its library. We do **not** want these performance examples
treated as importable tarot decks. Two guards keep them out:

1. They live under `recording/examples/`, **not** under `tarot/<slug>/`
   (the only path this repo's own tooling — `check_all.py`,
   `build_meta_grammar.py`, `refresh_collection.py` — and the importer
   treat as the grammar library).
2. They are **not** named `grammar.json`.

So `recording/examples/passarinho-sequence.json` is plain data the
`sequence.html` viewer fetches at runtime — a worked example for future
performance workflows — and it will not appear as a deck anywhere.
