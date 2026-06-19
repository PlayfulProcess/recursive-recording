#!/usr/bin/env python3
"""
narrate.py — neural-TTS narration + exact word-timings, the LibriVox replacement.

The reference implementation of the recursive.eco `narrate` / `align_audio` MCP tool, ported from
recursive-eco/apps/flow/src/lib/ai-pkg/tts-core.ts. Google Cloud TTS is the only provider that
returns real SSML-mark word timepoints — so we get a chosen neural voice AND karaoke alignment in
one pass, with no Whisper step.

Pipeline (per production):
  data/text.json (passages: {idx, beat, text})
   -> for each passage: SSML with a <mark> before every word -> Google Cloud TTS
      -> mp3 chunk + per-word timepoints
   -> ffprobe each chunk for its exact duration -> cumulative offsets
   -> ffmpeg concat (re-encode) -> audio/narration-tts.mp3
   -> rewrite the *-performance.json grammar: metadata.audio (relative), total_sec,
      per-item performance.{start_sec,end_sec,words:[{w,start,end}]} ; keep everything else.

Usage:  python narrate.py <production_dir> [voice]
        voice defaults to en-US-Neural2-D (proven to return timepoints). Swap freely — any
        en-US Neural2 / Studio voice works (Studio = highest quality). One-line change.

Key: GOOGLE_DRIVE_API_KEY (read from recursive-eco env; never printed). Run with real Windows
python (ffmpeg/ffprobe on PATH).
"""
import os, re, sys, json, glob, base64, subprocess, tempfile, urllib.request, urllib.error

VOICE = sys.argv[2] if len(sys.argv) > 2 else "en-US-Neural2-D"
PROD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
ENV_CANDIDATES = [
    r"C:\Users\ferna\OneDrive\Documentos\GitHub\recursive-eco\apps\flow\.env.local",
    r"C:\Users\ferna\OneDrive\Documentos\GitHub\recursive-eco\.env.local",
]

def read_key():
    for p in ENV_CANDIDATES:
        try:
            for line in open(p, encoding="utf-8"):
                m = re.match(r"\s*GOOGLE_DRIVE_API_KEY\s*=\s*(.+)", line)
                if m:
                    return m.group(1).strip().strip('"').strip("'").strip()
        except FileNotFoundError:
            pass
    sys.exit("GOOGLE_DRIVE_API_KEY not found in recursive-eco env")

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))

def synth_passage(text, key, voice, out_mp3):
    """Synthesize one passage; return [(word, rel_start_sec), ...]."""
    words = text.split()
    ssml = "<speak>" + " ".join(f'<mark name="w{i}"/>{esc(w)}' for i, w in enumerate(words)) + "</speak>"
    body = json.dumps({
        "input": {"ssml": ssml},
        "voice": {"languageCode": "en-US", "name": voice},
        "audioConfig": {"audioEncoding": "MP3", "effectsProfileId": ["headphone-class-device"]},
        "enableTimePointing": ["SSML_MARK"],
    }).encode()
    req = urllib.request.Request(
        "https://texttospeech.googleapis.com/v1beta1/text:synthesize?key=" + key,
        data=body, headers={"Content-Type": "application/json"})
    try:
        d = json.load(urllib.request.urlopen(req, timeout=60))
    except urllib.error.HTTPError as e:
        sys.exit(f"Google TTS {e.code}: {e.read().decode()[:300]}")
    open(out_mp3, "wb").write(base64.b64decode(d["audioContent"]))
    by_idx = {}
    for tp in d.get("timepoints", []):
        m = re.match(r"w(\d+)$", tp.get("markName", ""))
        if m:
            by_idx[int(m.group(1))] = tp["timeSeconds"]
    return [(words[i], by_idx.get(i)) for i in range(len(words))]

def ffprobe_dur(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", path], text=True)
    return float(out.strip())

def main():
    key = read_key()
    text = json.load(open(os.path.join(PROD, "data", "text.json"), encoding="utf-8"))
    passages = text if isinstance(text, list) else text.get("passages") or list(text.values())[0]
    gpath = glob.glob(os.path.join(PROD, "*-performance.json"))[0]
    grammar = json.load(open(gpath, encoding="utf-8"))
    assert len(grammar["items"]) == len(passages), "item/passage count mismatch"

    tmp = tempfile.mkdtemp(prefix="narrate_")
    chunks, offset, total_words = [], 0.0, 0
    per_item = []  # (start_sec, end_sec, words[])
    print(f"voice={VOICE}  passages={len(passages)}  -> {tmp}")
    for i, p in enumerate(passages):
        txt = p["text"] if isinstance(p, dict) else p
        mp3 = os.path.join(tmp, f"c{i:02d}.mp3")
        marks = synth_passage(txt, key, VOICE, mp3)
        dur = ffprobe_dur(mp3)
        chunks.append(mp3)
        # build absolute word times; word end = next word start (in-passage) or passage end
        starts = [(w, (t if t is not None else 0.0) + offset) for (w, t) in marks]
        words = []
        for k, (w, st) in enumerate(starts):
            en = starts[k + 1][1] if k + 1 < len(starts) else offset + dur
            words.append({"w": w, "start": round(st, 3), "end": round(max(en, st + 0.05), 3)})
        per_item.append((round(offset, 3), round(offset + dur, 3), words))
        total_words += len(words)
        offset += dur
        print(f"  [{i:02d}] {dur:6.2f}s {len(words):3d}w  {(p.get('beat') if isinstance(p,dict) else '')[:40]}")

    # concat (re-encode for a clean continuous file)
    listf = os.path.join(tmp, "list.txt")
    open(listf, "w").write("".join(f"file '{c}'\n" for c in chunks))
    audio_dir = os.path.join(PROD, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    out_mp3 = os.path.join(audio_dir, "narration-tts.mp3")
    subprocess.check_call(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listf,
                           "-c:a", "libmp3lame", "-q:a", "4", out_mp3],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # rewrite the grammar: audio + per-item timings; keep names/images/sections/notes
    slug = os.path.basename(PROD)
    grammar["metadata"]["audio"] = f"../productions/{slug}/audio/narration-tts.mp3"
    grammar["metadata"]["total_sec"] = round(offset, 2)
    grammar["metadata"]["audio_source"] = f"Google Cloud TTS ({VOICE}) — neural narration, AI-generated"
    grammar["metadata"]["reading_style"] = "tts-neural"
    grammar["metadata"].pop("crop_ranges", None)
    for it, (s, e, words) in zip(grammar["items"], per_item):
        perf = it.setdefault("performance", {})
        perf["start_sec"], perf["end_sec"] = s, e
        perf["words"] = words
        perf["video_visible"] = False
        perf["reading_style"] = "tts-neural"
    json.dump(grammar, open(gpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    size = os.path.getsize(out_mp3) / 1e6
    print(f"\nOK: {out_mp3}  {size:.1f}MB  total={offset:.1f}s  words={total_words}")
    print(f"updated grammar: {gpath}")

if __name__ == "__main__":
    main()
