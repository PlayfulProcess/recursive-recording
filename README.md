# recursive-recording

Turn a **source** — a public-domain book, a course, a deck — into a **narrated, illustrated
performance** that plays in any browser. The output is **data, not a video file**: a `sequence`
grammar whose items each carry a `performance` object (an image + timed text + a narration
track). **The viewer is the player.** No build step, no backend, no account.

> Part of the [recursive.eco](https://recursive.eco) ecosystem. This repo is the **open
> software + open format + public-domain data**. The recursive.eco web app itself stays private
> — the same way a lab can open its *software* without opening its *models*. Everything here is
> meant to be forked, hosted on GitHub Pages, and contributed to.

## Try it now (no install)
Serve the folder and open a viewer:
```bash
python3 -m http.server 8000
# then open:
#   http://localhost:8000/viewers/perform.html   ← Alice, full-prose karaoke (real LibriVox audio)
#   http://localhost:8000/viewers/sequence.html  ← a card/clip playlist (Passarinho demo)
```
Or open **`karaoke/alice-karaoke.html`** directly (no server needed) for the kids' **ALL-CAPS,
one-line-at-a-time** read-along driven by the browser's own speech synthesis.

Load any grammar with `?src=`:
`viewers/perform.html?src=../productions/alice-in-wonderland/alice-performance.json`

## How it works
A recording is a `sequence` grammar (`default_preview: "performance"`). Each **item is one
passage**: an `image_url` + a `performance` object with `start_sec`/`end_sec` and either timed
caption `overlays[]` or per-word `words[]`. A single global clock (driven by `metadata.audio`)
swaps the illustration and lights up the words. The *same grammar* plays here and in
recursive.eco — it's just data.

- **Format spec:** [`GRAMMAR_FORMAT.md`](GRAMMAR_FORMAT.md)
- **The shapes:** [`docs/performance-grammar.md`](docs/performance-grammar.md) ·
  [`docs/sequence-format.md`](docs/sequence-format.md) ·
  [`docs/karaoke-format.md`](docs/karaoke-format.md)

## Two reading modes
- **Full-prose karaoke** (the Alice flagship): the complete public-domain text, word-by-word
  highlight synced to a real LibriVox narration track. → `viewers/perform.html`
- **Kids' ALL-CAPS** (≤7 words/line, current word lit): built for a young reader. →
  `karaoke/alice-karaoke.html`

## Layout
```
viewers/        perform.html (global-clock karaoke) · sequence.html (card/clip playlist)
pipeline/       build_karaoke.py · assemble_performance.py · illustration_qa.py · narration_script.py
karaoke/        alice-passages.json (canonical PD content) + the Web-Speech reader
productions/    alice-in-wonderland/ — the flagship (full-prose + kids demo + illustration QA)
docs/           the format docs
examples/       a sequence-grammar example
GRAMMAR_FORMAT.md
```

## Run the pipeline
```bash
python3 pipeline/build_karaoke.py --demo       # prose → ALL-CAPS ≤7-word lines; regen the JS data
python3 pipeline/assemble_performance.py       # passages → a sequence+performance grammar
python3 pipeline/illustration_qa.py            # vision worksheet: see → match → reorder → regenerate
```

## Contributing
Add a public-domain source as a new `productions/<slug>/` grammar, or improve the viewers /
pipeline. The **format is the contract** — if your grammar conforms to `GRAMMAR_FORMAT.md`, it
plays everywhere. House rules:
- **Public-domain or properly-licensed content only.** Never republish in-copyright text or art.
- **Disclose AI.** AI-generated narration or illustrations must be labeled in the item metadata;
  when an image is regenerated, log the reason and keep the original.
- **No secrets, ever** — no keys, tokens, or `.env` files.

## Licensing — software vs. content
This repo is dual-licensed, deliberately:

| What | License |
|------|---------|
| **Code** — `viewers/`, `pipeline/`, any HTML/JS/Python | **AGPL-3.0** — see [`LICENSE`](LICENSE) |
| **Content** — grammars, `docs/`, passages, data, illustrations *authored here* | **CC-BY-SA-4.0** — see [`LICENSE-CONTENT.txt`](LICENSE-CONTENT.txt) |

AGPL keeps improvements to the *players and pipeline* open even when run as a network service.
CC-BY-SA keeps the *performances* shareable and remixable, attribution preserved. Third-party
public-domain assets referenced by the grammars (e.g. LibriVox recordings, scanned editions)
carry their own public-domain status — see each production's README for provenance.

Built with [Claude](https://claude.com/claude-code) for recursive.eco (PlayfulProcess).
