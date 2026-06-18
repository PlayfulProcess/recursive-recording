# Future plans — recording recursive.eco performances

**Status: documentation only. Nothing here is built yet.** This is a captured idea, not a commitment.

## The idea

Take the stories I've created with AI on **recursive.eco**, feature them as **`sequence`** grammars,
render them as a **timed performance with TTS narration** (karaoke-style highlighting), and then
**record that performance to video and post it to YouTube** — eventually *directly from the app*.

For now: just the plan.

## The stories to feature first

| Story | View link (kiosk) |
|---|---|
| Please Do What I Need, Not What I Want | https://recursive.eco/view/b4f6ab05-ef26-46f2-8ca6-52919abb3e2f?kiosk=true |
| Shiryo and the Little Kitten: A Lesson in Asking | https://recursive.eco/view/efa4e06f-89fb-4fb1-8a1d-42c5760a0ea3?kiosk=true |
| The Nest Knows Best: Bunny Coping Tricks | https://recursive.eco/view/260f6eb6-3fe7-4904-bb41-0caef7401392?kiosk=true |

## Why sequences fit

A `sequence` grammar is already an ordered list of items (image + text, in order) — exactly the
structure a playback/recording engine needs: render item N, hold for its duration, advance to N+1.
The Alice audiobook had to bolt this on via a CSV + a custom HTML player; in recursive.eco the
ordering/playback model is native data in the DB. Feature something as a sequence and the
playback skeleton is already there.

## Two ways to "record in the app"

1. **In-browser capture (literally inside the app).** The performance viewer plays the sequence on
   screen and the page records it via the browser `MediaRecorder` + canvas/screen-capture APIs,
   producing a downloadable video client-side. A "Record" button.
   - Pro: no separate infrastructure; the user owns the file.
   - Con: quality/timing depend on the user's machine; audio sync is fiddlier.

2. **Headless capture of the viewer URL (the "recording stack").** A Playwright/Chrome harness
   loads the *same* performance-viewer URL for a sequence, plays it deterministically at a fixed
   resolution (e.g. 1920×1080), and captures to MP4.
   - Pro: clean, repeatable, CI-able, best quality.
   - Con: separate infrastructure to build (this repo's eventual job). It just points at a URL, so
     a recursive.eco sequence URL works as well as the static Alice book did.

## Prerequisites (the real work, when we do it)

- **Autoplay / timeline mode** in the performance viewer — timed auto-advance, not just manual
  click-through. If the viewer is currently manual, this is the first piece.
- **Audio + timing model on items** — per-item TTS narration (or one merged track) plus word/line
  timestamps from forced alignment, for the karaoke highlight. The Alice book does this with
  `k-word` spans + a merged LibriVox track; recursive.eco items today carry `image_url` but no audio
  field, so that's the main data-model gap.
- **Isolated rendering** so the recording shows only the current item ("crop things not pertaining
  to the page").
- **YouTube posting** — start manual (download MP4, upload), later automate via the YouTube Data API
  with the account's credentials.

## Precedent / reference

- Alice in Wonderland audiobook: `playfulprocess/recursive-kids-stories-club`, branch `audiobook`.
  CSV-driven per-page illustrations (`books/alice-in-wonderland/illustrations.csv`), LibriVox audio
  with chapter offsets, karaoke word spans, served via GitHub Pages (audiobooks.recursive.eco).
- recursive.eco image-gen for fixing/illustrating items: grammar MCP `generate_item_image`
  (Gemini Imagen, ~$0.15/image) → stored on the same R2 CDN the book uses.

## Open questions

- TTS engine + voice (cloud TTS vs LibriVox-style human reads; the author dislikes flat TTS narration).
- Does the performance viewer support (or need) a music track per sequence (cf. the Suno poem music
  that wasn't wiring up in the Alice book)?
- Build the recorder once against the performance-viewer URL so *any* sequence becomes recordable.

## Playing the opening song in page order (without breaking karaoke)

Question: can the recording read/play in page order — title → author → LibriVox credit → the
Suno song for the opening poem → narration — or does that derail the TTS timestamps/karaoke?

Answer: it's fine, **as long as the recording is a sequence of independent segments**, each with
its own local timing — not one global narration track.

- The narration karaoke uses ONE merged LibriVox MP3 with **absolute** word offsets. Splicing the
  ~3-min Suno song into the middle of that single track would shift every later word timestamp by
  the song's length → everything after misaligns. Don't do that.
- Instead, build the recording as ordered segments, each carrying its own audio + its own
  segment-relative timing: [title/author] → [LibriVox credit] → [Suno song] → [Ch.1 narration] …
  Inserting the song shifts nothing, because narration timestamps are relative to the narration
  segment, not a global clock. This is already how the book is built: the poem song is a SEPARATE
  audio element with its own line-level highlighting (`.poem-line`/`.poem-stanza`), independent of
  the LibriVox word timestamps.
- Caveat: do NOT attempt word-level forced alignment on the SUNG track — singing stretches/repeats
  words and has instrumental bars; WhisperX is for clean speech. Keep the song at line/stanza-level
  highlighting on a hand-tuned timeline (what the poem player already does), and reserve word-level
  karaoke for the spoken narration.
