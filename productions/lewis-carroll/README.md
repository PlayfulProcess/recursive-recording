# Lewis Carroll — the context grammar (NEW)

**This folder is the WRITE target for a brand-new Lewis Carroll context / genealogy grammar.**
Nothing like it exists yet, so there's no collision risk — build freely here.

## What to build
A map of the world around the books — the genealogy archetype (like the tarot / couples maps):
- **Lewis Carroll** (Charles Dodgson, 1832–1898) — the author, the "golden afternoon" origin (1862 boat trip).
- **Alice Liddell** — the real Alice the story was told to.
- **The illustrators** — John Tenniel (1865/1871), Peter Newell, Arthur Rackham, Carroll's own manuscript
  drawings in *Alice's Adventures Under Ground*.
- **The companion works** — *Through the Looking-Glass*, *Jabberwocky*, *The Hunting of the Snark*.
- Cross-link to the Alice performance(s).

## Tools to use (the new MCP — see memory `recursive-eco-mcp-performance-pipeline`)
- **`wikipedia_summary`** (FREE) — bios/blurbs for Carroll, Alice Liddell, Tenniel, the works.
- **`commons_image_search`** (FREE) — PD portraits + manuscript scans + Tenniel plates; it returns the
  **license + artist** → bake those into each item's `metadata.credit` (err toward EXCESSIVE attribution).
- Build on `../alice-in-wonderland/data/people.json` (already has Carroll/illustrator people) — reference,
  don't overwrite.
- Output the grammar JSON in THIS folder (e.g. `lewis-carroll-grammar.json`). Optionally also create it as a
  platform grammar via the MCP `create_grammar` (it's new, so safe) — but the file here is the source of truth.

## Guardrails
Public-domain only (Carroll d.1898, Tenniel d.1914 → all PD). **Excessive attribution** from the Commons
license/artist on every image. Author = **PlayfulProcess** (never a real name). AI disclosed where used.
Flag any billed MCP step (`generate_item_image`, `narrate_grammar`) + cost before running; prefer the FREE
`commons_image_search` for real Carroll/Tenniel art over AI generation.

## Status — BUILT (Jun 20 2026)
`lewis-carroll-grammar.json` is the source of truth: a 10-item genealogy map (`grammar_type: custom`,
`metadata.kind: genealogy`) — **Carroll, Alice Liddell, Tenniel, Rackham** (people) + **Under Ground 1864,
Wonderland 1865, Looking-Glass 1871, Jabberwocky, The Hunting of the Snark** (works) + the **1862 Golden
Afternoon** origin. Each item has a `relations[]` edge list (for a future Cytoscape graph), `sections`
(Who/What · In this map · Connections), and a `metadata.credit` with **excessive PD attribution**
(artist + license + Commons/BL file). Bios via free `wikipedia_summary`; every image PD via free
`commons_image_search` / British Library — **no AI image generation used, no billed steps**. All 9 distinct
image URLs HEAD-checked 200; loads + renders in `viewers/perform2.html?src=../productions/lewis-carroll/lewis-carroll-grammar.json`.
Cross-refs `../alice-in-wonderland` (people/editions/performance) — reference only, not overwritten.
Not yet pushed to the platform via `create_grammar` (optional; file is canonical).
