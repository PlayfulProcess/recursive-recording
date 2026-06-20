# CLAUDE.md — build & illustrate a grammar via the recursive.eco MCP

You are helping the user build a **grammar** (a tarot deck, I Ching book, astrology
set, or illustrated story) by driving the **recursive.eco grammar MCP**. Everything
here runs through that MCP, scoped to the user's own account (their token). You do not
need the platform source code — the MCP is the whole interface.

If the MCP tools below aren't available, the user hasn't connected it yet → point them
to `MCP_SETUP.md`.

## The tool menu (recursive.eco MCP)
**Author**
- `create_grammar(name, grammar_type, description, tags)` → returns the grammar id + links.
  `grammar_type`: `tarot | iching | sequence | astrology | custom`.
- `add_items(grammar_id, items[])` — **batch** (one write). Each item: `{ name, symbol?,
  keywords?, category?, sections{label→text}, image_url?, metadata?, illustrations?,
  performance? }`. Prefer this over many `add_item` calls.
- `update_item(s)` — edit fields / sections (sections merge; null removes one).
- `get_grammar(id)` — read it back (returns a `links` object — use those URLs, don't
  hand-build them). `list_grammars`, `delete_item`, `delete_grammar` (dry_run first).

**Illustrate**
- `commons_image_search(q, limit)` — **public-domain sourcing** from Wikimedia Commons,
  no browser. Returns each hit's `thumb_url` (~1024px, pass straight to `set_item_image`),
  plus its **license + artist + attribution**. Use this for PD plates / scans / portraits.
- `generate_item_image(grammar_id, item_id, prompt?, reference_item_id?, provider?)` —
  **AI art** (billed ~$0.15). For a consistent deck, illustrate one card, then pass
  `reference_item_id` of it on the rest so the style matches. Check `reference_honored:true`.
- `set_item_image(grammar_id, item_id, image_url | image_base64, copy?)` — host any URL on
  the CDN (mirrors to R2). Free. Pass `copy:true` to own a delete-safe copy.
- `set_item_images` — bulk image set.

**Reference / facts**
- `wikipedia_summary(title, lang?)` — article summary + lead image + page URL, for
  card history, author bios, tradition/lineage notes.

**Audio (optional)**
- `narrate_grammar(grammar_id, voice?, provider?)` — synth karaoke narration (billed TTS).
- `upload_audio` + `align_audio` — host real (LibriVox) audio + word-time it.

**Publish / test**
- `set_grammar_visibility(grammar_id, is_public, open_to_community?)` — publish.
- `cast(grammar_id, question, count)` — draw a reading to sanity-check the deck.
- `storage_usage`, `list_files`, `delete_file` — manage R2 storage.

## The build workflow
1. **Create.** `create_grammar` with a clear name + type + 1-line description. Keep the id.
2. **Author the items in one batch.** `add_items` with the full set (22 arcana, 64
   hexagrams, the story's scenes…). Give each a rich `sections` map — e.g. tarot:
   `Upright`, `Reversed`, `Keywords`, `Visual_Contemplation`; story: `Narration`, `Notes`.
   Write `Visual_Contemplation` as an art-directable image prompt in ONE shared style.
3. **Illustrate every item** (target 100% coverage):
   - **Public-domain content** (historical tarot, classic literature, real people):
     `commons_image_search` for each → `set_item_image(thumb_url)` → set the returned
     **license + artist** into `metadata.credit` (see Attribution below).
   - **Original art**: `generate_item_image` for the first item to set the style, then the
     rest with `reference_item_id` = that first item for deck consistency.
4. **Attribute generously.** Err toward EXCESSIVE attribution. For PD images, write a
   structured credit: `metadata.credit = { artist, year, edition, source, source_url,
   license }` from what `commons_image_search` returned. For multiple editions on one
   item, use the `illustrations[]` array.
5. **(Optional) Narrate.** For a story/sequence, `narrate_grammar` (synthetic karaoke) or
   `upload_audio` + `align_audio` (real LibriVox audio). Then it plays in the Performance viewer.
6. **Publish + test.** `set_grammar_visibility(is_public:true)`, then `cast` a reading to
   confirm it draws sensibly. Hand the user the `links.open` URL.

## Attribution rules (important)
- Always credit the artist + year + edition + source for every illustration. `commons_image_search`
  hands you the license + artist — put them in `metadata.credit`. Never strip provenance.
- Only public-domain or freely-licensed images go into a shared/published grammar. If a
  source is copyrighted (a modern redesign, an in-copyright edition), do **not** use it —
  find a genuine PD scan (pre-1900 works, museum/archive open-access) instead.

## The grammar JSON shape
See [`../GRAMMAR_FORMAT.md`](../GRAMMAR_FORMAT.md) for the canonical item + performance
shape. You rarely build JSON by hand — the MCP tools write it — but the format doc is the
source of truth if you need to fix structure.

## Domain quick-starts (only the prompt changes)
- **Tarot:** "22-card Major Arcana, Rider–Waite PD plates from Commons, upright/reversed
  meanings, publish."
- **I Ching:** "64 hexagrams with `number` 1–64 + binary, judgment + image + changing-lines
  sections."
- **Astrology:** "Planets + signs + houses as an interpretation set."
- **Illustrated story (Alice / kids book):** "One item per scene with a `Narration` section;
  source PD illustrations (Tenniel, Rackham) from Commons; then `narrate_grammar` for karaoke."

## Building a *course* about the flow (screenshots)
That's a separate, **local** step — see `recorder/`. It screenshots the real app UI as you
perform a flow and produces a step-by-step course. It runs on the user's machine with their
own login (the MCP can't and shouldn't screenshot an authenticated UI server-side).
