# -*- coding: utf-8 -*-
"""
Build the MULTI-EDITION illustration stream: every original-edition plate (across
all editions + Carroll's manuscript) appears at its scene's text anchor, held >=3s,
staggered so overlapping plates queue instead of colliding, each credited.

Inputs (all consolidated locally — no network, no R2 writes):
  r2-inventory.json        every R2 plate key (scene-folder = first path segment)
  data/spine.json          scene-folder -> current_pages -> earliest page
  data/alice-performance.json  page "Ch.C, Page P" -> performance.start_sec + words[]

Output:
  data/illustration-stamps.json     the stamp table (plate -> edition/year/anchor/window)
  alice-illustration-stream.json    the playable sequence grammar (perform.html / view.html)

Anchor rule: a plate's anchor = the start_sec of the FIRST page of its scene-folder
(the first sentence as the scene begins). Stagger: display_start = max(anchor,
prev_end); display_end = next display_start (>=3s). Never before the anchor => no spoiler.
"""
import json, os, re

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R2 = "https://pub-71ebbc217e6247ecacb85126a6616699.r2.dev/"
MIN_HOLD = 3.0

inv  = json.load(open(os.path.join(HERE, "r2-inventory.json"), encoding="utf-8"))
spine = json.load(open(os.path.join(HERE, "data", "spine.json"), encoding="utf-8"))
prod = json.load(open(os.path.join(HERE, "alice-performance.json"), encoding="utf-8"))

# page (chapter,page) -> start_sec, from the performance items
page_start = {}
for it in prod["items"]:
    pf = it.get("performance")
    if not pf: continue
    m = re.search(r"Ch\.?\s*(\d+),\s*Page\s*(\d+)", it.get("name") or "")
    if m: page_start[(int(m.group(1)), int(m.group(2)))] = pf["start_sec"]

# global karaoke word stream (absolute times), for slicing each plate's window
words = []
for it in prod["items"]:
    pf = it.get("performance")
    if pf and pf.get("words"): words.extend(pf["words"])
words.sort(key=lambda w: w["start"])
def slice_words(a, b):
    return [w for w in words if a <= w["start"] < b]

# scene-folder -> anchor start_sec (earliest real page in current_pages)
def page_key(s):
    try:
        c, p = s.split("-"); c, p = int(c), int(p)
        return (c, p) if c >= 1 else None
    except Exception:
        return None
folder_anchor = {}
for e in spine:
    cands = [page_start[k] for k in (page_key(s) for s in e.get("current_pages", [])) if k in page_start]
    if cands:
        folder_anchor[e["entry_point"]] = min(cands)

# edition classifier (order matters: specific before generic)
EDS = [
    ("john-tenniel-harry-theaker", "Tenniel, colour Harry Theaker", 1911),
    ("harry-theaker",              "Tenniel, colour Harry Theaker", 1911),
    ("john-tenniel-colorized",     "The Nursery Alice (Tenniel / Edmund Evans)", 1890),
    ("e-g-thomson", "The Nursery Alice (Tenniel / Edmund Evans)", 1890),
    ("e-gertrude-thomson", "The Nursery Alice (Tenniel / Edmund Evans)", 1890),
    ("nursery", "The Nursery Alice (Tenniel / Edmund Evans)", 1890),
    ("john-tenniel", "John Tenniel", 1865),
    ("arthur-rackham", "Arthur Rackham", 1907),
    ("william-h-walker", "W. H. Walker", 1907),
    ("w-h-walker", "W. H. Walker", 1907),
    ("brinsley-le-fanu", "Brinsley Le Fanu", 1910),
    ("le-fanu", "Brinsley Le Fanu", 1910),
    ("emily-overnell", "“Emily Overnell”", 1912),
    ("overnell", "“Emily Overnell”", 1912),
    ("alice-b-woodward", "Alice B. Woodward", 1913),
    ("woodward", "Alice B. Woodward", 1913),
    ("gwynedd-hudson", "Gwynedd Hudson", 1922),
    ("hudson", "Gwynedd Hudson", 1922),
    ("harry-rountree", "Harry Rountree", 1928),
    ("rountree", "Harry Rountree", 1928),
    ("bessie-pease-gutmann", "Bessie Pease Gutmann", 1907),
    ("gutmann", "Bessie Pease Gutmann", 1907),
    ("lewis-carroll", "Lewis Carroll (manuscript)", 1864),
    ("manuscript", "Lewis Carroll (manuscript)", 1864),
    ("alice-liddell", "Photograph of Alice Liddell", 1860),
    ("-photo", "Photograph", 1860),
    ("flow-image-gen", "AI-generated", 2026),
    ("generated", "AI-generated", 2026),
    ("dall-e", "AI-generated", 2026),
]
def classify(key):
    k = key.lower()
    for sub, label, yr in EDS:
        if sub in k: return label, yr
    return "Unattributed", 9999

# collect scene-folder plate events
events, skipped = [], []
for o in inv["objects"]:
    key = o["key"]
    if not key.lower().endswith((".jpg", ".jpeg", ".png", ".webp")): continue
    rest = key.split("alice-in-wonderland/", 1)[-1]
    folder = rest.split("/")[0] if "/" in rest else ""
    # only true SCENE folders (chNN-* / chapter-NN-*); page-sequences like
    # manuscript-under-ground (47 sequential scans) and alice-liddell-photos
    # need their own sequential/interstitial anchoring — handled separately.
    if not re.match(r"(ch\d|chapter-\d)", folder):
        skipped.append(key); continue
    if folder not in folder_anchor:        # scene-folder with a known text anchor
        skipped.append(key); continue
    label, yr = classify(key)
    if label in ("AI-generated",):         # AI handled separately (remake-eligible)
        skipped.append(key); continue
    events.append({
        "url": R2 + key, "credit": "%s, %d" % (label, yr) if yr < 9999 else label,
        "edition": label, "year": yr, "scene": folder,
        "chapter": next((e["chapter"] for e in spine if e["entry_point"] == folder), 99),
        "anchor": round(folder_anchor[folder], 2),
    })

# order by anchor, then edition year (oldest first), then scene for stability
events.sort(key=lambda x: (x["anchor"], x["year"], x["scene"], x["url"]))

# stagger: each plate shows >= MIN_HOLD, never before its anchor
prev_end = -1
for ev in events:
    start = max(ev["anchor"], prev_end)
    ev["display_start"] = round(start, 2)
    prev_end = start + MIN_HOLD
# display_end = next plate's display_start (last one holds to end of its scene + a beat)
for i, ev in enumerate(events):
    nxt = events[i + 1]["display_start"] if i + 1 < len(events) else ev["display_start"] + 8
    ev["display_end"] = round(max(nxt, ev["display_start"] + MIN_HOLD), 2)

# write the stamp table
json.dump({"min_hold_sec": MIN_HOLD, "count": len(events), "stamps": events},
          open(os.path.join(HERE, "data", "illustration-stamps.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# build the playable sequence grammar (one item per plate event)
items = []
for i, ev in enumerate(events):
    items.append({
        "id": "stamp-%03d" % i,
        "name": "%s — %s" % (ev["scene"], ev["credit"]),
        "sort_order": i,
        "category": "illustration",
        "image_url": ev["url"],
        "metadata": {"credit": ev["credit"], "edition": ev["edition"], "year": ev["year"], "scene": ev["scene"]},
        "performance": {
            "start_sec": ev["display_start"], "end_sec": ev["display_end"],
            "video_visible": False, "reading_style": "full-prose-karaoke",
            "words": slice_words(ev["display_start"], ev["display_end"]),
        },
    })

md = prod.get("metadata", {})
grammar = {
    "name": "Alice's Adventures in Wonderland — Illustrated Editions Performance",
    "description": ("Every illustrated edition of Alice (1864–1933), each plate appearing at the "
        "passage it depicts, held ≥3s and staggered when editions overlap, credited on screen. "
        "Public-domain LibriVox narration drives word-by-word karaoke underneath."),
    "grammar_type": "sequence", "default_preview": "performance", "is_published": False,
    "tags": ["alice", "carroll", "illustrated-editions", "karaoke", "public-domain"],
    "metadata": {"audio": md.get("audio"), "total_sec": md.get("total_sec"),
                 "crop_ranges": md.get("crop_ranges", []), "audio_source": md.get("audio_source"),
                 "reading_style": "full-prose-karaoke"},
    "item_count": len(items), "items": items,
}
json.dump(grammar, open(os.path.join(HERE, "alice-illustration-stream.json"), "w", encoding="utf-8"),
          ensure_ascii=False)

# report
from collections import Counter
byed = Counter(e["edition"] for e in events)
print("scene-folder plate events:", len(events), "| skipped (no anchor / AI / non-scene):", len(skipped))
print("editions in the stream:")
for ed, n in sorted(byed.items(), key=lambda x: -x[1]):
    print("  %3d  %s" % (n, ed))
print("\nfirst 8 events (anchor -> display window):")
for ev in events[:8]:
    print("  ch%-2d %-34s %-30s anchor %.0f  show %.0f-%.0f" % (
        ev["chapter"], ev["scene"][:34], ev["credit"][:30], ev["anchor"], ev["display_start"], ev["display_end"]))
print("\nwrote data/illustration-stamps.json + alice-illustration-stream.json (%d items)" % len(items))
