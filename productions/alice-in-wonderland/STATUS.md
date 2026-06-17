# Alice — status (autonomous session, Jun 16 2026)

## Two playable performances (serve the repo, then open)
`python -m http.server 8792` from the repo root, then:
- **Multi-edition illustration stream** (newest): `viewers/perform.html?src=../productions/alice-in-wonderland/alice-illustration-stream.json`
- **Full-prose page reader**: `viewers/perform.html` (default → `alice-performance.json`)

Controls: space play/pause · ←/→ passage · **AA / c** = ALL-CAPS karaoke · click scrub to seek.

## Done
- **Multi-edition stream** — 106 plate events across 11 editions + Carroll's manuscript drawings.
  Each plate appears at its scene's first page, held ≥3 s, **staggered** when editions overlap
  on a scene (oldest edition first), with the **source credit** (artist/year) shown in the corner
  (baked into any recording). Karaoke (real LibriVox word timings) runs underneath; chapter-title
  reading skipped via `metadata.crop_ranges`. Built by `scripts/build_illustration_stream.py`
  from consolidated data only (no network, no R2 writes).
- **ALL-CAPS toggle** + **source-credit legend** in `perform.html`.
- **R2 ledger baseline** (`r2-inventory.json`): 194 objects / 265 MB; only 2 byte-dup pairs
  (~2 MB, both intentional cross-references). R2 is already clean.

## Anchoring note (why this is scene-accurate, not yet sentence-exact)
Anchors here come from each scene-folder's **first page** (`spine.json` → `start_sec`). So a plate
lands on the right *scene*, possibly a sentence or two off *within* it. The agreed PG-embedded-
position method (sentence-exact) is the **precision layer**, deferred below because its plate↔URL
join is worth verifying together.

## Flagged follow-ups (need you / a decision / paid)
1. **PG sentence-level refinement** (Tenniel #11 / Rackham #28885 / manuscript #19002): fetch the
   PG HTML, read each plate's embedded position → exact sentence anchor. Read-only; the only
   uncertain part is joining PG plates to our R2 files — verify a sample with you.
2. **Manuscript pages** (`manuscript-under-ground/`, 47 sequential scans) + **Liddell photos** (11):
   excluded from the scene-stream — they need page→text sequencing / interstitial placement.
3. **AI `generated/` images** (15): remake-eligible; regeneration costs credits (MCP
   `generate_item_image`) → **needs your go-ahead** before any spend.
4. **R2 tidy** (optional, with sign-off): normalize the few `chapter-NN-…` folders to `chNN-…`,
   and de-dup the 2 cross-referenced pairs. Never auto-deleted.
5. **Default-edition mode**: the stream shows *all* editions; a toggle for "one canonical plate
   per scene + edition switch" is easy if the all-editions flow feels busy.
6. **Recording / 16:9 clean mode** for a YouTube MP4 (the `record/` stack), and **per-word
   karaoke in the real `view.html`** so the main app lights words too (overlays already play there).

## Open decisions
- Default plate per moment if we add single-edition mode (oldest-first assumed for now).
- How far to push sentence-exactness before "good enough to ship."
