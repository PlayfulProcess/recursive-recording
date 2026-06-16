# Alice's Adventures in Wonderland — performance

The flagship recursive-recording production. Lewis Carroll's *Alice's Adventures in Wonderland*
as a narrated, illustrated karaoke performance — all public domain.

## Files
| File | What |
|------|------|
| `alice-performance.json` | **Full-prose flagship.** 187 page-items, 170 with real per-word LibriVox timings. Plays in `viewers/perform.html`. |
| `grammar.json` | Kids' **ALL-CAPS** demo (6 passages, *Down the Rabbit-Hole*), assembled by `pipeline/assemble_performance.py` with kid-paced *estimated* timings. |
| `illustration-map.json` / `illustration-qa.md` | The illustration QA worksheet (see → match → reorder → regenerate). |

Play the flagship: `viewers/perform.html?src=../productions/alice-in-wonderland/alice-performance.json`

## Provenance & licensing
- **Text** — Lewis Carroll, 1865. **Public domain.** (Project Gutenberg #11.)
- **Narration** — a LibriVox solo reading. **Public domain** (LibriVox recordings are released
  into the public domain). The merged MP3 is referenced by `metadata.audio`.
- **Word timings** — derived by forced alignment of the page text against the narration
  (Whisper word timestamps), then per-chapter alignment. The repeated spoken chapter-title
  boilerplate is skipped via `metadata.crop_ranges`.
- **Illustrations** — plates from the 1864–1933 illustrated editions (Carroll's manuscript,
  Tenniel 1865, the Nursery Alice, Rackham 1907, Walker, Le Fanu, Theaker, Woodward, Hudson,
  Rountree, Gutmann) and period photographs — **all public domain**. Any AI-generated or
  regenerated image is labeled in the item metadata, with the original kept.
- This production's authored data (the grammar, the QA worksheet) is **CC-BY-SA-4.0**; the
  third-party PD assets it references carry their own public-domain status.

The companion *editions & illustrators history* site (genealogy + dossiers) lives in the
separate `alice-in-wonderland` repo; this is the *performance*.
