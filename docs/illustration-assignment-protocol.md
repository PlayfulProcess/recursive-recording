# Illustration Assignment Protocol (autonomous)

Deterministically assign each book page its illustration, placed against the **exact passage**
the plate was originally drawn for, with a fixed **source priority** and automatic **conflict
resolution**. Re-runnable, auditable, no manual picking required. Built for the Alice book but
edition-agnostic.

## Why exact-text, not chapter
A plate must sit against the precise passage it originally illustrated — *within-chapter* order
matters (a grown-Alice plate two pages before she grows is still a spoiler). Chapter-level is not
enough. The anchor is a short verbatim quote from the passage the plate sat against.

## Data model
- **Page**: `{ key:"chN-P", order_index, chapter, text }` — text is the exact rendered page text.
- **Plate**: `{ url, edition, year, tier, anchors:[normKey,...] }`
  - `tier ∈ {edition, manuscript, photo, ai}`
  - `anchors` = normalized (lowercase-alphanumeric) verbatim snippets from the passage(s) the plate
    was originally placed against.
- **Priority key** = `(tier_rank, year)` with `tier_rank: edition=0, manuscript=1, photo=2, ai=3`.
  Within a tier, **oldest year wins** ("most classical → newest").

## Source priority (hard order)
1. **Original printed editions**, oldest → newest:
   Tenniel 1865 → Walker 1907 → Rackham 1907 → Le Fanu 1910 → Tenniel/Theaker 1911 →
   Overnell 1912 → Woodward 1913 → Hudson 1922 → Rountree 1928 → Gutmann 1933.
2. **Manuscript** — *Alice's Adventures Under Ground* (1864, Carroll's own drawings).
3. **Photographs** — Alice Liddell / Carroll photos (decorative; may sit on any page of/after their era's scene).
4. **AI generation** — **last resort**, only where no original/manuscript/photo depicts the passage.

## Building the per-edition anchor index (oldest → new)
For each printed edition, obtain a source where plates are placed **inline with the text** so the
anchor is explicit — **no OCR**:
- Preferred: Project Gutenberg / archive.org illustrated edition HTML (image `<img>` sits next to
  its passage). Extract the passage immediately following each image = its anchor.
  - Tenniel 1865 → **PG ebook #28885** (42 plates inline). DONE → `index/.../tenniel-1865-index.json`.
- Fallback: documented plate-caption lists (each caption is a verbatim quote = the anchor).
- Manuscript: documented page-by-page contents (do **NOT** OCR Carroll's handwriting).
Normalize every anchor to `lowercase [a-z0-9]` for robust substring matching against page text.

## Anchor → page resolution
A plate's candidate pages = pages whose normalized text **contains** any of the plate's anchor
keys. Coarse fallback (until an exact index exists for that edition): pages in the plate's
scene-folder beat, then chapter. **Spoiler invariant (hard):** a plate may only be placed at a
page whose `order_index ≥` the plate's earliest matched anchor page. Never earlier.

## Assignment algorithm (greedy, reading order, push-conflicts-later)
1. `candidates[page]` = plates resolving to that page, sorted by priority `(tier_rank, year)`.
2. Walk pages in reading order. For each page, assign the **highest-priority UNUSED** candidate
   that satisfies the spoiler invariant.
3. **Conflict resolution**: a contested/duplicate plate is pushed to its **next valid candidate
   page later** in the book — never earlier. If none remain → unused pool.
4. **Coverage pass**: any still-unused ORIGINAL (edition/manuscript) plate is placed at any open
   valid candidate page so every original is used at least once.
5. **Fallback tiers**: a page still empty after editions+manuscript+photo gets an AI plate only if
   one depicts that passage; otherwise it stays blank (logged).

## Outputs
- `illustrations.csv` — the assignment the book reads.
- `ledger.json` — `page → { chosen, tier, year, why, alternatives[] }` (full audit).
- `unused-pool.json` — every plate not placed, with reason. **Nothing is ever deleted.**
- `image-registry.json` — kept in sync; every R2 URL preserved.

## Invariants
- Deterministic: same inputs → same output.
- Re-runnable & monotonic: adding a per-edition exact index only sharpens placement; never deletes art.
- Dev-branch only; `main` is the baseline to diff/revert.
- No R2 deletions, ever.
