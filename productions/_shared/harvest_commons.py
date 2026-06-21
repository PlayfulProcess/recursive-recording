# -*- coding: utf-8 -*-
"""
Harvest a LARGE, scene-matched public-domain image set for an Ovid myth from Wikimedia Commons
CATEGORIES (curated membership = high precision, on-theme), so the 3s rotation shows a fresh
picture almost every window instead of looping a handful.

Each narrative beat maps to Commons categories of what it DEPICTS (Arachne's web literally shows
Europa / Leda / Danaë / Neptune's disguises — each its own well-populated Commons category).
Files from the category (+ one level of subcategories) are PD/CC0-filtered via extmetadata,
deduped globally, and capped per beat to ~(beat_seconds / 3). Artist + license -> 'credit'.

Usage: python harvest_commons.py <prod_dir>
"""
import json, os, sys, re, time, urllib.parse, urllib.request, html

API = "https://commons.wikimedia.org/w/api.php"
UA = "recursive-recording/1.0 (PD-art harvester; pp@playfulprocess.com)"
WIN = 3.0

prod = os.path.abspath(sys.argv[1]); base = os.path.basename(prod)
perf = json.load(open(os.path.join(prod, base + "-performance.json"), encoding="utf-8"))
beats = sorted(perf["items"], key=lambda it: it.get("sort_order", 0))
beat_dur, beat_name = {}, {}
for i, it in enumerate(beats):
    pf = it.get("performance") or {}
    beat_dur[i] = max(0.0, pf.get("end_sec", 0) - pf.get("start_sec", 0))
    beat_name[i] = it.get("name", "")
cap = {i: max(3, int(beat_dur[i] // WIN) + 2) for i in beat_dur}

# beat -> Commons categories of what the beat depicts (no "Category:" prefix)
CATS = {
"ovid-arachne": {
 0:["Pallas Athena","Minerva"],
 1:["Spinning in art","Weaving in art"],
 2:["Distaffs in art","Spindles"],
 3:["Arachne"],
 4:["Arachne"],
 5:["Minerva in art"],
 6:["Looms in art","Tapestries"],
 7:["Contest between Athena and Poseidon","Parthenon (mythology)"],
 8:["Metamorphoses by Antonio Tempesta","Engravings of Metamorphoses (Ovid)"],
 9:["Rape of Europa","Leda and the Swan","Danaë","Jupiter and Antiope","Proserpina"],
 10:["Neptune in art","Apollo in art","Medusa in art","Chiron","Bacchus in art"],
 11:["Arachne"],
 13:["Arachne"],
 14:["Arachne","Spiders in art"],
},
"ovid-narcissus": {
 0:["Tiresias"],
 1:["Ephebes","Antinous"],
 2:["Echo (mythology)"],
 3:["Juno (mythology)"],
 4:["Narcissus (mythology)","Echo (mythology)"],
 5:["Narcissus (mythology)"],
 6:["Echo (mythology)"],
 7:["Echo (mythology)"],
 8:["Nemesis (mythology)"],
 9:["Springs in art","Fountains in art"],
 10:["Narcissus (mythology)"],
 11:["Narcissus (mythology)"],
 12:["Narcissus (mythology)"],
 13:["Narcissus (mythology)"],
 14:["Narcissus (mythology)"],
 15:["Narcissus (mythology)"],
 16:["Narcissus (mythology)"],
 17:["Narcissus (mythology)"],
 18:["Narcissus (mythology)"],
 19:["Narcissus (mythology)"],
 20:["Echo (mythology)","Narcissus (mythology)"],
 21:["Narcissus (mythology)"],
 22:["Narcissus poeticus","Narcissus (plant) in art"],
}}
catmap = CATS.get(base)
if not catmap: print("no category map for", base); sys.exit(1)

def api(params):
    params = dict(params); params.update({"action":"query","format":"json"})
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)
        except Exception as e:
            time.sleep(1.5 * (attempt + 1))
    return {}

def cat_files(cat, depth=1, _seen=None):
    """File titles in Category:cat plus one level of subcategories."""
    if _seen is None: _seen = set()
    files, subcats = [], []
    cont = {}
    while True:
        d = api({"list":"categorymembers","cmtitle":"Category:"+cat,"cmlimit":"200",
                 "cmtype":"file|subcat", **cont})
        for m in (d.get("query",{}) or {}).get("categorymembers", []):
            if m["title"].startswith("File:"): files.append(m["title"])
            elif m["title"].startswith("Category:"): subcats.append(m["title"][9:])
        cont = d.get("continue", {}); time.sleep(0.25)
        if not cont: break
    if depth > 0:
        for sc in subcats[:8]:
            if sc in _seen: continue
            _seen.add(sc)
            files += cat_files(sc, depth-1, _seen)
    return files

def clean(s):
    if not s: return ""
    s = re.sub(r"<[^>]+>", "", s); s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()

def is_pd(ext):
    blob = " ".join([(ext.get(k,{}).get("value") or "") for k in ("License","LicenseShortName","UsageTerms")]).lower()
    if "share" in blob or "by-sa" in blob or "by-nc" in blob or "noncommercial" in blob: return False
    return ("public domain" in blob) or ("cc0" in blob) or ("pdm" in blob) or ext.get("License",{}).get("value","").lower()=="pd"

def imageinfo(titles):
    out = {}
    for k in range(0, len(titles), 40):
        chunk = titles[k:k+40]
        d = api({"titles":"|".join(chunk),"prop":"imageinfo",
                 "iiprop":"url|extmetadata|mime|size","iiurlwidth":"1280"})
        for p in (d.get("query",{}) or {}).get("pages", {}).values():
            ii = (p.get("imageinfo") or [None])[0]
            if ii: out[p["title"]] = ii
        time.sleep(0.3)
    return out

catcache = {}
def files_for(cat):
    if cat not in catcache:
        try: catcache[cat] = cat_files(cat)
        except Exception as e: print("  ! cat failed", cat, e); catcache[cat] = []
    return catcache[cat]

# 1) per-beat candidate file titles (union of the beat's categories)
beat_titles, all_titles = {}, set()
for bi in sorted(catmap):
    ts = []
    for cat in catmap[bi]: ts += files_for(cat)
    beat_titles[bi] = list(dict.fromkeys(ts)); all_titles.update(beat_titles[bi])

# 2) one imageinfo pass over the whole union
info = imageinfo(sorted(all_titles))

def mk(t):
    ii = info.get(t)
    if not ii or not ii.get("mime","").startswith("image/"): return None
    if ii.get("width",0) < 700: return None
    ext = ii.get("extmetadata") or {}
    if not is_pd(ext): return None
    artist = clean(ext.get("Artist",{}).get("value","")) or "Unknown artist"
    licn = clean(ext.get("LicenseShortName",{}).get("value","")) or "Public domain"
    obj = clean(ext.get("ObjectName",{}).get("value","")) or t.replace("File:","").rsplit(".",1)[0]
    return {"_t":t,"w":ii.get("width",0),"artist":artist[:90],"license":licn,"title":obj[:90],
        "image_url":ii.get("thumburl") or ii.get("url"), "source_page":ii.get("descriptionurl",""),
        "credit":"%s — %s (Wikimedia Commons, %s)" % (artist[:70], obj[:60], licn),
        "license_confidence":"commons-category"}

# 3) per-beat PD-filtered candidate lists (biggest first)
beat_cands = {}
for bi, ts in beat_titles.items():
    cs = [c for c in (mk(t) for t in ts) if c]
    cs.sort(key=lambda c: -c["w"])
    beat_cands[bi] = cs

# 4) DEAL round-robin across beats so beats sharing a category split its pool evenly
taken, chosen = set(), []
ptr = {bi:0 for bi in beat_cands}; counts = {bi:0 for bi in beat_cands}
order = sorted(beat_cands)
progress = True
while progress:
    progress = False
    for bi in order:
        if counts[bi] >= cap[bi]: continue
        cs = beat_cands[bi]
        while ptr[bi] < len(cs):
            c = cs[ptr[bi]]; ptr[bi] += 1
            if c["_t"] in taken: continue
            taken.add(c["_t"])
            cc = {k:v for k,v in c.items() if k not in ("_t","w")}
            cc["anchor_beat_idx"] = bi
            chosen.append(cc); counts[bi] += 1; progress = True
            break
chosen.sort(key=lambda c: c["anchor_beat_idx"])
for bi in order:
    print("  beat %2d  cap %2d  got %2d  | %s" % (bi, cap[bi], counts[bi], beat_name[bi][:32]))

doc = {"_note":"PD/CC0 images harvested from Wikimedia Commons CATEGORIES (curated membership) via the API, "
       "PD-filtered via extmetadata, deduped, capped per beat to ~(beat_seconds/3). Each beat maps to "
       "categories of what it depicts. Artist + license from extmetadata; baked into 'credit' (excessive "
       "attribution). Curated by PlayfulProcess; all images public domain / CC0; only the narration is AI.",
       "count":len(chosen),"images":chosen}
out = os.path.join(prod, "data", "image-stream.json")
json.dump(doc, open(out,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nTOTAL:", len(chosen), "->", os.path.relpath(out, prod))
