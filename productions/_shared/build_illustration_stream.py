# -*- coding: utf-8 -*-
"""
Build a ~3s ROTATING public-domain illustration stream for an Ovid myth performance,
the Alice illustration-stream model adapted for a denser rotation.

Difference from Alice's build_illustration_stream.py: Alice held one plate until the
next scene's plate (long holds). Here the narration is tiled into fixed ~3s windows and
we ROUND-ROBIN through the pool of artworks that have "unlocked" (an artwork unlocks at
the start_sec of the passage/beat it is anchored to — never shown before its beat, so no
spoiler). A freshly-unlocked artwork is shown first at its beat, then the rotation
continues, so something new appears roughly every 3 seconds while the karaoke runs under.

Inputs (per production):
  <perf>.json          the per-passage karaoke performance (start_sec/end_sec + words[] per beat)
  data/image-stream.json   the verified PD artwork set (anchor_beat_idx + artist/year/license[/credit])

Outputs:
  data/illustration-stamps.json        the human-readable stamp table (one row per 3s window)
  <prod>-illustration-stream.json      the playable sequence grammar (viewers/perform2.html)

Usage:
  python build_illustration_stream.py <prod_dir> [perf.json] [out.json]
  defaults: perf = <basename>-performance.json, out = <basename>-illustration-stream.json
"""
import json, os, sys

WIN = 3.0  # seconds per image window (the "~3s rotation")

prod = os.path.abspath(sys.argv[1])
base = os.path.basename(prod)
perf_path = os.path.join(prod, sys.argv[2] if len(sys.argv) > 2 else base + "-performance.json")
out_path  = os.path.join(prod, sys.argv[3] if len(sys.argv) > 3 else base + "-illustration-stream.json")
imgs_path = os.path.join(prod, "data", "image-stream.json")
stamps_path = os.path.join(prod, "data", "illustration-stamps.json")

perf = json.load(open(perf_path, encoding="utf-8"))
imgdoc = json.load(open(imgs_path, encoding="utf-8"))
images = imgdoc["images"] if isinstance(imgdoc, dict) else imgdoc

# beat (passage) timeline + names, from the karaoke performance
beats = sorted(perf["items"], key=lambda it: it.get("sort_order", it.get("number", 0)))
beat_start, beat_end, beat_name = {}, {}, {}
for i, it in enumerate(beats):
    pf = it.get("performance") or {}
    idx = it.get("sort_order", i)
    beat_start[idx] = pf.get("start_sec", 0.0)
    beat_end[idx]   = pf.get("end_sec", 0.0)
    beat_name[idx]  = it.get("name", "")

# global karaoke word stream (absolute times), for slicing each 3s window
words = []
for it in beats:
    pf = it.get("performance") or {}
    if pf.get("words"):
        words.extend(pf["words"])
words.sort(key=lambda w: w["start"])
def slice_words(a, b):
    return [w for w in words if a <= w["start"] < b]

md = perf.get("metadata", {})
total = md.get("total_sec") or (beats[-1].get("performance", {}).get("end_sec", 0.0))

def credit_of(im):
    if im.get("credit"):
        base_c = im["credit"]
    else:
        bits = [im.get("artist", "Unknown artist")]
        if im.get("title"):   bits.append("“%s”" % im["title"])
        if im.get("year"):    bits.append("(%s)" % im["year"])
        base_c = " ".join(bits)
    lic = im.get("license", "")
    if lic and lic.lower() not in base_c.lower():
        base_c = "%s — %s" % (base_c, lic)
    return base_c

# group artworks by the beat they depict (order preserved)
by_beat = {}
for k, im in enumerate(images):
    im["_idx"] = im.get("anchor_beat_idx", 0)
    by_beat.setdefault(im["_idx"], []).append(im)

def emit(im, a, b, stamps):
    stamps.append({
        "url": im["image_url"], "credit": credit_of(im),
        "artist": im.get("artist", ""), "year": im.get("year", ""),
        "license": im.get("license", ""), "title": im.get("title", ""),
        "source_page": im.get("source_page", im.get("page_url", "")),
        "scene": beat_name.get(im["_idx"], ""), "anchor_beat_idx": im["_idx"],
        "display_start": round(a, 2), "display_end": round(b, 2),
    })

# Walk beats in order. Each beat plays through ITS OWN images in sequence, one per ~WIN-second
# window — so with enough images per beat every window is a fresh, on-scene picture (no A-B-A-B
# looping). A beat with more images than windows shows only as many as fit; a beat with fewer
# cycles its own set. A beat with NO images of its own borrows from the most recently shown ones
# (fallback only). No future-beat image is ever shown early (no spoiler).
stamps, last_url, recent = [], None, []
for bi in sorted(beat_start.keys()):
    start = beat_start[bi]
    end = beat_end.get(bi) or (start + WIN)
    if bi == max(beat_start):  # last beat holds to the very end of the audio
        end = max(end, total)
    pool = list(by_beat.get(bi, [])) or list(recent)   # own images, else recent fallback
    if not pool:  # nothing available yet (before the first beat with art) -> leave a gap
        continue
    if len(pool) > 1 and pool[0]["image_url"] == last_url:   # don't repeat across the seam
        pool = pool[1:] + pool[:1]
    t, k = start, 0
    while t < end - 0.2:
        e = min(t + WIN, end)
        im = pool[k % len(pool)]
        if im["image_url"] == last_url and len(pool) > 1:     # never back-to-back duplicate
            k += 1; im = pool[k % len(pool)]
        emit(im, t, e, stamps); last_url = im["image_url"]
        recent = [r for r in recent if r["image_url"] != im["image_url"]]
        recent.append(im); recent = recent[-8:]
        k += 1; t = e

# stamp table (human-readable; the "illustration-stamps track" like Alice's)
json.dump({"min_hold_sec": WIN, "win_sec": WIN, "rotation": "round-robin over unlocked pool",
           "count": len(stamps), "stamps": stamps},
          open(stamps_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# playable sequence grammar (one item per 3s window)
items = []
for i, s in enumerate(stamps):
    items.append({
        "id": "stamp-%03d" % i, "name": "%s — %s" % (s["scene"], s["credit"]),
        "sort_order": i, "category": "illustration", "image_url": s["url"],
        "metadata": {"credit": s["credit"], "artist": s["artist"], "title": s["title"],
                     "year": s["year"], "license": s["license"], "source_page": s["source_page"],
                     "scene": s["scene"], "anchor_beat_idx": s["anchor_beat_idx"]},
        "performance": {"start_sec": s["display_start"], "end_sec": s["display_end"],
                        "video_visible": False, "reading_style": md.get("reading_style", "tts-neural"),
                        "words": slice_words(s["display_start"], s["display_end"])},
    })

grammar = {
    "id": perf.get("id", base) + "-illustrated",
    "name": perf.get("name", base) + " — Illustrated (PD-art rotation)",
    "description": ("%s Rotating public-domain artworks (~3s each), each anchored to the beat it "
        "depicts, credited on screen; the narration's word-by-word karaoke runs underneath. "
        "A recursive-recording performance." % perf.get("description", "")),
    "grammar_type": "sequence", "default_preview": "performance", "is_published": False,
    "tags": perf.get("tags", []) + ["illustrated", "pd-art", "rotation"],
    "metadata": {k: md.get(k) for k in ("audio", "total_sec", "audio_source", "reading_style",
                 "translation", "translation_note", "content_note") if md.get(k) is not None},
    "item_count": len(items), "items": items,
}
grammar["metadata"]["crop_ranges"] = md.get("crop_ranges", [])
json.dump(grammar, open(out_path, "w", encoding="utf-8"), ensure_ascii=False)

# report
from collections import Counter
byart = Counter(s["credit"].split(" —")[0][:34] for s in stamps)
print("images:", len(images), "| 3s windows:", len(stamps), "| total_sec:", round(total, 1))
print("appearances per artwork:")
for c, n in byart.most_common():
    print("  %2dx  %s" % (n, c))
print("wrote", os.path.relpath(stamps_path, prod), "+", os.path.relpath(out_path, prod))
