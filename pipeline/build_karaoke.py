# -*- coding: utf-8 -*-
"""build_karaoke.py — turn prose into karaoke-ready ALL-CAPS short lines, and (re)generate
the browser data file the reader loads.

Two jobs:
  1. allcaps_lines(text)  — split a paragraph into short, kid-trackable ALL-CAPS lines
     (<= MAX_WORDS words, broken at sentence/clause boundaries). This is what `ingest.py`
     would feed with raw chapter text from the kids-book-club source.
  2. regen_js()           — write karaoke/alice-passages.js (window.ALICE_PASSAGES = {...})
     from karaoke/alice-passages.json so alice-karaoke.html works under file://.

  python3 pipeline/build_karaoke.py            # regenerate the JS data file
  python3 pipeline/build_karaoke.py --demo     # also print a lines() demo on sample prose
"""
import json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JSON = os.path.join(ROOT, "karaoke", "alice-passages.json")
JS   = os.path.join(ROOT, "karaoke", "alice-passages.js")
MAX_WORDS = 7

_SENT = re.compile(r'[^.!?;:]+(?:[.!?;:]+|$)')

def allcaps_lines(text, max_words=MAX_WORDS):
    """Split prose into short ALL-CAPS lines for a young reader."""
    lines = []
    for sent in (s.strip() for s in _SENT.findall(text) if s.strip()):
        words = sent.split()
        # break long sentences at commas first, then by word count
        if len(words) <= max_words:
            lines.append(sent)
            continue
        chunk = []
        for w in words:
            chunk.append(w)
            if len(chunk) >= max_words and (w.endswith(',') or len(chunk) >= max_words + 2):
                lines.append(" ".join(chunk)); chunk = []
        if chunk:
            lines.append(" ".join(chunk))
    return [re.sub(r'\s+', ' ', l).strip().upper() for l in lines if l.strip()]

def regen_js():
    data = open(JSON, encoding="utf-8").read()
    header = "/* GENERATED from alice-passages.json by pipeline/build_karaoke.py — do not hand-edit. */\n"
    open(JS, "w", encoding="utf-8").write(header + "window.ALICE_PASSAGES = " + data.rstrip() + ";\n")
    g = json.loads(data)
    print(f"wrote {os.path.relpath(JS, ROOT)} — {len(g.get('passages', []))} passages")

if __name__ == "__main__":
    regen_js()
    if "--demo" in sys.argv:
        sample = ("Alice was beginning to get very tired of sitting by her sister on the bank, "
                  "and of having nothing to do: once or twice she had peeped into the book her "
                  "sister was reading, but it had no pictures or conversations in it.")
        print("\nallcaps_lines() demo:")
        for l in allcaps_lines(sample):
            print("   " + l)
