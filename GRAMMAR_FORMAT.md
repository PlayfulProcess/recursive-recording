# Grammar JSON — Canonical Format

The complete, authoritative shape for a recursive.eco grammar JSON file.

This document is the contract between the schemas repo and the
recursive.eco application. **If your grammar won't load in the viewer
or the editor, this is the first place to look.**

The other docs (`CLAUDE.md`, `CONTRIBUTING.md`, `QUICKSTART.md`,
`schemas/SCHEMAS_GUIDE.md`) all describe pieces of this format. This
doc is the single source of truth.

---

## Top-level shape

A grammar is a single JSON object:

```jsonc
{
  "name": "string",                    // REQUIRED — display title
  "description": "string",             // REQUIRED — what this grammar contains
  "grammar_type": "string",            // REQUIRED — see "Grammar types" below
  "cover_image_url": "string",         // OPTIONAL — hero image for the deck
  "tags": ["string"],                  // OPTIONAL — search/filter tags
  "creator_name": "string",            // OPTIONAL — your name or handle
  "creator_link": "string",            // OPTIONAL — your website or profile
  "is_published": false,               // OPTIONAL — false for drafts
  "items": [ /* UnifiedItem objects */ ]   // REQUIRED — see "UnifiedItem" below

  // Optional library-placement fields (see CLAUDE.md "Monad Fields"):
  // "roots": [...], "shelves": [...], "lineages": [...], "worldview": "...",

  // Optional commons metadata:
  // "_grammar_commons": { "schema_version": "1.0", "license": "...", "attribution": [...] }
}
```

**There is NO top-level `emergences` array.** Level-1 base items AND
level-2+ composite items ALL live inside `items[]`. Composite items
are distinguished by the presence of `composite_of: ["id1", "id2", ...]`
on the item itself. (Continued in "Composite items" below.)

---

## Grammar types

`grammar_type` must be one of:

| Type | What it's for |
|---|---|
| `"tarot"` | Card-draw oracle decks (Major Arcana, archetype decks). Items have Interpretation, Reversed, etc. |
| `"iching"` | I Ching hexagrams. Items have line data via the `lines` property. Must have 64 items. |
| `"astrology"` | Western or Vedic astrology. Items have planet / sign / house categories. |
| `"sequence"` | Curated playlists / story sequences / video collections. Often paired with `performance` blocks (see below). |
| `"course"` | Step-by-step learning sequences with lessons. |
| `"prompt"` | Prompt libraries for AI conversations. |
| `"birthchart"` | Astrological birth-chart grammars. |
| `"altar"` | Altar / shrine grammars — symbolic arrangements. |
| `"music"` | Music grammars — albums, songs, sequences. |
| `"custom"` | Anything else — chapter books, folk tales, poetry, journaling decks. Use when no other type fits. |

> ⚠️ **`"performance"` is NOT a valid `grammar_type`.** "Performance" is
> a viewer mode (timestamped video clip rendering). The grammar_type
> for a curated video playlist is `"sequence"` (or `"custom"`); the
> per-item `performance` object below carries the clip details.

If your `grammar_type` doesn't match what the items actually contain,
Flow / the viewer may render the grammar incorrectly. When in doubt,
use `"custom"`.

---

## UnifiedItem shape

Every entry in `items[]` follows this shape:

```jsonc
{
  "id": "stable-string-id",          // REQUIRED — unique within the grammar
  "name": "string",                  // REQUIRED — display name
  "category": "string",              // OPTIONAL — grouping key (e.g. "major_arcana")
  "sort_order": 0,                   // OPTIONAL — display order (default by array position)
  "image_url": "string",             // OPTIONAL — per-item image (R2 URL or any HTTPS)
  "sections": {                      // REQUIRED — at least {} (can be empty)
    "Section Label": "markdown content",
    "Another Section": "more content"
  },
  "keywords": ["string"],            // OPTIONAL — search tags for this item
  "composite_of": ["id-1", "id-2"],  // PRESENT ONLY ON COMPOSITE ITEMS — see below
  "metadata": { /* free-form */ },   // OPTIONAL — see "Metadata fields"
  "performance": { /* clip cfg */ }  // OPTIONAL — see "Performance object"
}
```

### Sections are flexible

Section keys are not restricted. Use whatever makes sense for your
content. Examples seen in production grammars:

- Tarot: `Interpretation`, `Reversed`, `Summary`
- I Ching: `Image`, `Judgment`, `Line 1`, `Line 2`, ...
- Bus Passengers: `Thoughts`, `Thinking`, `Perception`, `Sensing`, `Context`, `Mystery`
- Story grammar: `Story`, `For Young Readers`, `For Parents`, `Themes`
- Tantric tattvas: `Mirror`, `Yantra`, `Essence`, `Practice`, `Question`, `Unmesa/Nimesa`
- Sequence / performance: `What she says`, `Why this clip`, `Test for listener`

The viewer renders all sections. Order is the JSON property order.

### Composite items (the L2/L3 emergence pattern)

A composite item is just a regular item that has a `composite_of`
array referencing the IDs of its children:

```json
{
  "id": "act-1-the-departure",
  "name": "Act 1: The Departure",
  "category": "act",
  "composite_of": ["scene-1", "scene-2", "scene-3"],
  "sections": {
    "About this act": "The hero leaves the ordinary world..."
  }
}
```

- L1 items are the leaves (cards, scenes, hexagrams, video clips).
- L2 items group L1 items via `composite_of`.
- L3 items can group L2 items.

**All of these live in the same `items[]` array.** Do not put
composite items in a separate `emergences[]` block. (Legacy grammars
that used a separate array no longer work; the editor saves
everything in `items[]`.)

The `level` field (`"level": 1`, `"level": 2`, `"level": 3`) is
*allowed* and helpful for tools that walk the hierarchy, but the
real source of truth is the presence/absence of `composite_of`. An
item without `composite_of` is L1; an item with `composite_of` is L2
or deeper.

`composite_of` references must point to IDs that exist in the same
`items[]` array. Broken references will fail validation.

---

## Metadata fields

`metadata` is a free-form object for whatever extra structured data
your grammar needs. Some conventions:

| Field | Meaning | Used by |
|---|---|---|
| `youtube_video_id` | The 11-character YouTube ID (e.g. `dQw4w9WgXcQ`) | Sequence grammars with video clips |
| `youtube_url` | Full URL to the source video | Sequence grammars (for click-through) |
| `lines` | Array of line texts (for I Ching items) | I Ching grammars |
| `planet`, `sign`, `house` | Astrology categorizations | Astrology grammars |
| `theme`, `mood`, `tradition` | Free-form taxonomy | Any grammar |

> ⚠️ **YouTube field naming gotcha:** The canonical field name is
> `youtube_video_id`, NOT `video_id`. Earlier drafts of grammars
> shipped with `video_id` will not be recognized by the performance
> viewer. Always use the `youtube_` prefix.

You can also put arbitrary keys in `metadata` for editorial / study
purposes. The viewer ignores unknown keys.

---

## Performance object (timestamped video clip rendering)

For grammars where each item is a clip from a YouTube video — common
in `sequence` grammars and useful in `custom` grammars too — each
item carries an optional `performance` object:

```jsonc
{
  "id": "clip-01-misconceptions-opening",
  "name": "Misconceptions about Hinduism — opening (5:00–7:30)",
  "metadata": {
    "youtube_video_id": "XS7RKHR_ink",
    "youtube_url": "https://www.youtube.com/watch?v=XS7RKHR_ink"
  },
  "performance": {
    "start_sec": 300,         // crop start, in seconds
    "end_sec": 450,           // crop end, in seconds
    "volume": 1.0,            // 0..1
    "video_visible": true,    // false = audio-only playback
    "cover_image_url": "https://...",   // OPTIONAL — used in audio-only mode

    "background_audio": {     // OPTIONAL — overlay background music/ambience
      "youtube_video_id": "different-id-here",
      "start_sec": 0,
      "end_sec": 600,
      "volume": 0.3
    },

    "overlays": [             // OPTIONAL — text or image overlays on the video
      {
        "kind": "text",       // "text" or "image"
        "content": "Overlay text or image URL",
        "start_sec": 5,       // when this overlay appears
        "end_sec": 12,        // when it disappears
        "x_pct": 10,          // horizontal position, 0..100
        "y_pct": 80,          // vertical position, 0..100
        "width_pct": 80       // width as percentage of viewport
      }
    ]
  },
  "sections": {
    "What she says": "...",
    "Why this clip": "..."
  }
}
```

### Field-name conventions inside `performance`

Note the **singular `sec`** (not `seconds`):

- ✅ `start_sec`, `end_sec`
- ❌ `start_seconds`, `end_seconds`

This applies inside `performance`, inside `background_audio`, and
inside `overlays[]`.

### When to use `performance`

- ✅ Sequence grammars where items are video clips
- ✅ Custom grammars that want timestamped audio/video segments
- ✅ Any item where you want the viewer to play a cropped portion
- ❌ Static items (tarot cards, hexagrams) — leave `performance` off

The `performance` object lives on the **individual item**, not at
the grammar root. Each clip has its own start/end.

---

## Reference items & meta-grammars (a grammar of grammars)

An item does not have to hold its own content — it can **point at another
grammar/document**. This is what makes a "grammar of grammars" possible: a
meta-grammar whose items are themselves whole decks or texts, so you can build a
tree whose leaves drill down into full sub-grammars (recursion **by reference**,
not by merging the item and grammar types).

On a **UnifiedItem**:

| Field | Meaning |
|---|---|
| `item_type` | `"content"` (default) or `"reference"` |
| `ref_document_id` | the `user_document` id this item opens |
| `ref_preview` | how the target opens: `"default" \| "study" \| "grammar" \| "altar"` |
| `grammars` | array of linked grammar/document ids (multi-link) |

On the **grammar root**:

| Field | Meaning |
|---|---|
| `default_preview` | the viewer that opens by default: `"grammar" \| "study" \| "tree" \| "altar" \| "course" \| "thumbnails"` |

The viewer renders a reference item as a link that opens the target
(`/play?id=<ref_document_id>`). Combined with the L1/L2/L3 `composite_of`
emergence, `default_preview: "tree"` renders the whole thing in the tree-viewer.

### Example 1 — a meta-grammar leaf that opens a full deck

```json
{
  "id": "deck-visconti-sforza",
  "name": "Visconti-Sforza Tarot",
  "level": 1,
  "item_type": "reference",
  "ref_document_id": "<the deck's user_document id>",
  "ref_preview": "grammar",
  "sections": { "What it is": "The oldest near-complete tarot…" },
  "metadata": { "branch": "branch-roots" }
}
```

### Example 2 — the genealogy tree that opens in tree view

A `grammar_type: "custom"` meta-grammar with `"default_preview": "tree"` and three
levels: **L1** decks (reference items), **L2** branches (`composite_of` the decks),
**L3** root (`composite_of` the branches). The tree-viewer
(`recursive.eco/pages/tree-viewer.html?type=custom&id=…`) draws root → branches →
decks, and each deck leaf opens its own grammar.

> Real example in this repo: **`grammars/tree-of-tarot/grammar.json`** — the
> genealogy of tarot. (Its leaves currently use text references; after the decks are
> imported to Supabase, set `ref_document_id` on each leaf so clicking opens the deck.
> See `plan/tarot-roadmap-and-supabase-log.md` §3d.)

---

## Three common mistakes (when grammars won't load)

These three errors account for the vast majority of "won't load"
failures. Check yours against this list first.

### Mistake 1 — `grammar_type: "performance"`

`"performance"` is not a valid grammar type. It is a viewer mode.

✅ For a curated video playlist: `"grammar_type": "sequence"`
✅ When unsure: `"grammar_type": "custom"`

### Mistake 2 — `emergences[]` at the top level

A separate top-level `emergences` array is not supported. Merge the
L2/L3 items into `items[]` with their `composite_of` field intact.

```diff
- "items": [ /* L1 items */ ],
- "emergences": [ /* L2 items */ ]
+ "items": [
+   /* L1 items */,
+   /* L2 items with composite_of */
+ ]
```

### Mistake 3 — `metadata.video_id` / `metadata.start_seconds`

The canonical field names are:

- `metadata.video_id` → `metadata.youtube_video_id`
- `metadata.start_seconds` → `performance.start_sec` (moved to `performance`)
- `metadata.end_seconds` → `performance.end_sec` (moved to `performance`)

Each item that has a YouTube clip should have BOTH
`metadata.youtube_video_id` AND a `performance` object with
`start_sec` and `end_sec`.

---

## Minimal working examples

### Tarot card (L1 only)

```json
{
  "name": "Tiny Tarot",
  "description": "Just one card.",
  "grammar_type": "tarot",
  "tags": ["tarot"],
  "is_published": false,
  "items": [
    {
      "id": "major-00-fool",
      "name": "The Fool",
      "sort_order": 0,
      "category": "major_arcana",
      "keywords": ["new beginnings"],
      "sections": {
        "Interpretation": "The beginning of all journeys.",
        "Reversed": "Fear of the unknown."
      }
    }
  ]
}
```

### Sequence of video clips with emergence theme

```json
{
  "name": "Three clips on dharma",
  "description": "Curated video study.",
  "grammar_type": "sequence",
  "tags": ["dharma", "study"],
  "is_published": false,
  "items": [
    {
      "id": "clip-01",
      "name": "What is dharma",
      "category": "foundation",
      "sort_order": 1,
      "metadata": {
        "youtube_video_id": "abc12345XYZ",
        "youtube_url": "https://www.youtube.com/watch?v=abc12345XYZ"
      },
      "performance": {
        "start_sec": 120,
        "end_sec": 240,
        "video_visible": true,
        "volume": 1.0
      },
      "sections": {
        "Summary": "Teacher defines dharma in plain terms."
      }
    },
    {
      "id": "clip-02",
      "name": "The four legs of dharma",
      "category": "foundation",
      "sort_order": 2,
      "metadata": {
        "youtube_video_id": "def67890XYZ",
        "youtube_url": "https://www.youtube.com/watch?v=def67890XYZ"
      },
      "performance": {
        "start_sec": 600,
        "end_sec": 780,
        "video_visible": true,
        "volume": 1.0
      },
      "sections": {
        "Summary": "Satyam, daya, sochá, tapas."
      }
    },
    {
      "id": "theme-foundations",
      "name": "Foundations of dharma",
      "category": "theme",
      "sort_order": 100,
      "composite_of": ["clip-01", "clip-02"],
      "sections": {
        "About this theme": "Two starting-point clips."
      }
    }
  ]
}
```

Both clips live in `items[]`. The theme is also an item in `items[]`,
just with `composite_of`. No separate `emergences[]` array.

---

## Validating before upload

A minimal Python check:

```python
import json
g = json.load(open("your-grammar.json", encoding="utf-8"))

# Required top-level
assert "name" in g and "description" in g
assert "grammar_type" in g
assert g["grammar_type"] in {
    "tarot", "iching", "astrology", "sequence",
    "course", "prompt", "birthchart", "altar", "music", "custom"
}
assert isinstance(g.get("items"), list) and len(g["items"]) > 0

# No top-level emergences array
assert "emergences" not in g, "Move emergences into items[] with composite_of"

# Per-item checks
ids = {it["id"] for it in g["items"]}
for it in g["items"]:
    assert "id" in it and "name" in it and "sections" in it
    if "composite_of" in it:
        for child in it["composite_of"]:
            assert child in ids, f"composite_of references missing id: {child}"
    if "metadata" in it:
        # Common YouTube field-name gotcha
        assert "video_id" not in it["metadata"], \
            "Rename metadata.video_id -> metadata.youtube_video_id"
    if "performance" in it:
        p = it["performance"]
        # Singular "sec" not "seconds"
        assert "start_seconds" not in p, "Rename performance.start_seconds -> start_sec"
        assert "end_seconds" not in p, "Rename performance.end_seconds -> end_sec"

print("OK")
```

If you write a more thorough validator and submit it as
`scripts/validate-grammar.py`, others will thank you.

---

## See also

- [`README.md`](README.md) — repo overview and how to copy / fork / share grammars
- [`QUICKSTART.md`](QUICKSTART.md) — fastest path to your first grammar
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — contribution workflow and git identity setup
- [`CLAUDE.md`](CLAUDE.md) — guidance for AI assistants working in this repo (includes
  monad/library-placement fields and the emergence-creation playbook)
- [`schemas/SCHEMAS_GUIDE.md`](schemas/SCHEMAS_GUIDE.md) — directory layout for the
  `schemas/` subtree

If you find a discrepancy between this doc and the actual behavior of
the editor or the viewer, **the editor's behavior is the source of
truth** — please open an issue or PR so we can update this doc.
