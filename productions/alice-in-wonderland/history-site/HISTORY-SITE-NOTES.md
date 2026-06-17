# CLAUDE.md — alice-in-wonderland

A static, fork-it-yourself **history website about the illustrated editions of *Alice's
Adventures in Wonderland*** — the editions, illustrators, colorists, publishers, and the
behind-the-scenes relationships around Lewis Carroll. Modeled on the `recursive-tarot` repo
(sibling in this GitHub folder).

## What this is
Carroll's *Alice* has been reillustrated by dozens of artists across 160 years. This site maps
**who drew/published which edition, when, and how they relate** — Carroll → Tenniel/Macmillan
(canonical 1865) → the post-1907-copyright wave (Rackham, Walker, Le Fanu, Woodward, Hudson,
Rountree, Gutmann…). No build step; GitHub Pages serves it.

## Structure (mirrors recursive-tarot)
- `data/editions.json` — the editions manifest (id, year, illustrator, publisher, `derives_from`, R2 folder). **The genealogy data source.**
- `data/people.json` — author / muse / illustrators / colorists / publishers, with `made` / `published` relationship arrays.
- `research/editions/<id>.md` — one dossier per edition (rich frontmatter + prose). *To be filled.*
- `research/people/<id>.md` — one dossier per person. *To be filled.*
- `editions/<id>/` — per-edition assets/plates (or just reference R2 URLs). *To be filled.*
- `index.html` — site home (reads the two manifests; lists editions timeline + people).
- `genealogy.html` — Cytoscape graph of the relationships (adapt from recursive-tarot/genealogy.html; feed it editions.json + people.json). *To be built.*
- `style.css`, `site-header.js` — shared shell (copy/adapt from recursive-tarot). *To be added.*
- `CNAME` — custom domain (e.g. `alice.recursive.eco`?). *To be decided.*
- `.nojekyll` — present (Pages serves raw).

## Conventions (from recursive-tarot)
- Every dossier/manifest entry carries `confidence` + a `note`/`maintainer_note`. **AI-assisted facts
  marked `confidence:low` MUST be web-verified before publishing** (lifespans, minor illustrators,
  "Emily Overnell" identity, the 1890 colorist).
- Relationships live in arrays (`illustrator`, `publisher`, `derives_from`, `made`, `published`) so
  the genealogy graph is data-driven — add an edition/person to the JSON and it appears.
- Honest edges: `derives_from` here means "answers to / reillustrates," not exact derivation.

## R2 assets
Edition plates already live on Cloudflare R2 under
`https://pub-71ebbc217e6247ecacb85126a6616699.r2.dev/grammar-illustrations/alice-in-wonderland/`
(see each edition's `r2_folder`). The sibling `recursive-kids-stories-club` repo holds the
audiobook/reader using the same R2 images; this repo is the *editions/people/history* site.

## Status / next
- DONE: repo scaffold, `data/editions.json`, `data/people.json`, `index.html`, this guide.
- NEXT: verify the `confidence:low` facts; write `research/people/*.md` + `research/editions/*.md`
  dossiers; copy+adapt `style.css`/`site-header.js` and build `genealogy.html` from the manifests;
  decide the CNAME and create the GitHub repo + Pages.
