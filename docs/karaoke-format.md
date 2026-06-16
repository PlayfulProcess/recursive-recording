# Karaoke ALL-CAPS reading format

The reading style a young reader can follow (built to my daughter's preference: ALL CAPS).

## Rules
- **ALL CAPS**, large, high contrast.
- **One short line at a time** — ≤ ~7 words (`build_karaoke.py` enforces this, breaking at
  sentence then clause boundaries).
- The **current line** is bright; lines already read dim to "spoken"; the **current word** is
  highlighted as the voice speaks it.
- One **illustration per passage**, shown above the words.
- Gentle, slow narration (kid-paced ≈ 0.85× rate); low background music optional.

## Data shape (`karaoke/alice-passages.json`)
```json
{
  "passages": [{
    "id": "p03-the-little-door",
    "title": "The Little Door",
    "lines": ["ALICE CAME TO A LONG HALL.", "THEN SHE FOUND A TINY DOOR.", "..."],
    "illustration": {
      "alt": "…", "status": "original|reordered|regenerated",
      "prompt": "image-gen prompt that honors the text (sizes!)",
      "image_url": "…(set by the illustration step)…",
      "svg": "…offline placeholder plate…"
    }
  }]
}
```

## How the reader syncs words (`alice-karaoke.html`)
- Speaks each line via the Web Speech API; `SpeechSynthesisUtterance.onboundary` gives a
  `charIndex` per word → the matching `<span>` lights up.
- **Fallback:** if `boundary` events don't fire (some browsers/voices), a timer sweeps words at
  an estimated rate so the highlight still tracks. With no voices at all, it's a silent
  read-along.
- Loads data from `alice-passages.js` (a `window.ALICE_PASSAGES = …` wrapper) so it runs from
  `file://` without a server. Regenerate that wrapper with `build_karaoke.py`.
