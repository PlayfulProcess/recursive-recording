# -*- coding: utf-8 -*-
"""
Autonomous illustration assignment engine. Executes illustration-assignment-protocol.md.

Inputs (in --dir, default cwd):
  pages.json            [{key:"chN-P", order:int, chapter:int, text:str}, ...]   (exact page texts)
  image-registry.json   { url: {folder, file, desc, pages:[...]}, ... }          (the plate pool)
  index/*-index.json    optional per-edition exact-anchor indexes (e.g. tenniel-1865-index.json)

Outputs (in --dir):
  illustrations.out.csv   chapter,page,url,description,note   (the assignment)
  ledger.json             page -> {chosen, tier, year, why, alternatives}
  unused-pool.json        plates not placed (nothing deleted)

Deterministic. Re-runnable. Adding an exact index only sharpens placement.
"""
import json, re, csv, os, argparse

TIER_RANK = {'edition': 0, 'manuscript': 1, 'photo': 2, 'ai': 3}

# url substring -> (edition_name, year, tier).  Order matters (first match wins).
CLASSIFY = [
    ('tenniel-harry-theaker', ('Tenniel/Theaker', 1911, 'edition')),
    ('john-tenniel-harry-theaker', ('Tenniel/Theaker', 1911, 'edition')),
    ('tenniel-colorized', ('Tenniel', 1865, 'edition')),
    ('john-tenniel', ('Tenniel', 1865, 'edition')),
    ('walker-1907', ('Walker', 1907, 'edition')),
    ('rackham-1907', ('Rackham', 1907, 'edition')),
    ('le-fanu-1910', ('Le Fanu', 1910, 'edition')),
    ('overnell-1912', ('Overnell', 1912, 'edition')),
    ('woodward-1913', ('Woodward', 1913, 'edition')),
    ('hudson-1922', ('Hudson', 1922, 'edition')),
    ('rountree-1928', ('Rountree', 1928, 'edition')),
    ('gutmann-1933', ('Gutmann', 1933, 'edition')),
    ('nursery-alice', ('Nursery Alice', 1890, 'manuscript')),
    ('manuscript-under-ground', ('Under Ground ms', 1864, 'manuscript')),
    ('lewis-carroll-1864', ('Under Ground ms', 1864, 'manuscript')),
    ('manuscript-page', ('Under Ground ms', 1864, 'manuscript')),
    ('alice-liddell', ('Photograph', 1860, 'photo')),
    ('-photo', ('Photograph', 1860, 'photo')),
    ('flow-image-gen', ('AI', 2026, 'ai')),
    ('generated/', ('AI', 2026, 'ai')),
]

def classify(url):
    u = url.lower()
    for key, val in CLASSIFY:
        if key in u:
            return val
    return ('Unknown', 9999, 'edition')

def norm(s):
    return re.sub(r'[^a-z0-9]', '', (s or '').lower())

def folder_chapter(url):
    m = re.search(r'/ch(?:apter)?-?0*(\d+)[a-z0-9-]*/', url + '/')
    return int(m.group(1)) if m else None

def load(dirp, name):
    p = os.path.join(dirp, name)
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default='.')
    args = ap.parse_args()
    D = args.dir

    pages = load(D, 'pages.json')                 # ordered list
    registry = load(D, 'image-registry.json')     # url -> info
    pages.sort(key=lambda p: p['order'])
    page_norm = {p['key']: norm(p['text']) for p in pages}
    page_order = {p['key']: p['order'] for p in pages}
    order_of_chapter_start = {}
    for p in pages:
        order_of_chapter_start.setdefault(p['chapter'], p['order'])

    # exact anchors per edition, keyed by a scene/caption -> anchor normKey
    idx_dir = os.path.join(D, 'index')
    edition_anchors = {}   # edition_name -> [ (anchor_normkey, our_page_or_None) ]
    if os.path.isdir(idx_dir):
        for fn in os.listdir(idx_dir):
            if fn.endswith('-index.json'):
                data = json.load(open(os.path.join(idx_dir, fn), encoding='utf-8'))
                ed = data.get('edition', fn)
                ekey = 'Tenniel' if 'tenniel' in fn.lower() else ed
                arr = []
                for pl in data.get('plates', []):
                    arr.append((norm(pl.get('anchor', '')), pl.get('our_page')))
                edition_anchors[ekey] = arr

    # Build plate pool
    plates = []
    for url, info in (registry or {}).items():
        ed, year, tier = classify(url)
        fch = folder_chapter(url)
        plates.append({'url': url, 'edition': ed, 'year': year, 'tier': tier,
                       'folder': info.get('folder', ''), 'chapter': fch, 'desc': info.get('desc', '')})

    def candidate_pages(plate):
        """Return ordered_index list of pages this plate may occupy (>= its anchor)."""
        cands = []
        # 1) exact anchors for this edition (Tenniel today)
        anchors = edition_anchors.get(plate['edition'], [])
        # match this plate to an anchor by description/scene keywords is hard; instead, for editions
        # WITH an exact index, use the index's our_page directly when available.
        matched_exact = False
        for nk, our_page in anchors:
            if our_page and our_page in page_order:
                # crude: associate by chapter (sharpened later by per-plate caption mapping)
                pass
        # 2) coarse anchor: the plate's scene-folder chapter -> any page in that chapter or later
        ch = plate['chapter']
        if ch is not None:
            start = order_of_chapter_start.get(ch)
            if start is not None:
                for p in pages:
                    if p['order'] >= start and p['chapter'] >= ch:
                        cands.append(p['order'])
        return cands

    # Candidate map page_order -> list of plates (with priority)
    from collections import defaultdict
    cand = defaultdict(list)
    order_to_key = {p['order']: p['key'] for p in pages}
    for pl in plates:
        for o in candidate_pages(pl):
            cand[o].append(pl)

    used = set()
    assignment = {}   # page_key -> plate
    ledger = {}
    for p in sorted(pages, key=lambda x: x['order']):
        o = p['order']
        opts = [pl for pl in cand.get(o, []) if pl['url'] not in used]
        opts.sort(key=lambda pl: (TIER_RANK[pl['tier']], pl['year']))
        if opts:
            chosen = opts[0]
            used.add(chosen['url'])
            assignment[p['key']] = chosen
            ledger[p['key']] = {'chosen': chosen['url'], 'tier': chosen['tier'], 'year': chosen['year'],
                                'edition': chosen['edition'],
                                'alternatives': [a['url'] for a in opts[1:6]]}
        else:
            ledger[p['key']] = {'chosen': None, 'why': 'no candidate (blank)'}

    unused = [pl['url'] for pl in plates if pl['url'] not in used]

    # write outputs
    with open(os.path.join(D, 'illustrations.out.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['chapter', 'page', 'url', 'description', 'note'])
        for p in sorted(pages, key=lambda x: x['order']):
            ch, pg = p['key'][2:].split('-')
            pl = assignment.get(p['key'])
            if pl:
                w.writerow([ch, pg, pl['url'], pl['desc'], 'auto:%s/%s/%d' % (pl['tier'], pl['edition'], pl['year'])])
            else:
                w.writerow([ch, pg, '', '(blank)', 'auto:no-candidate'])
    json.dump(ledger, open(os.path.join(D, 'ledger.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    json.dump(unused, open(os.path.join(D, 'unused-pool.json'), 'w', encoding='utf-8'), indent=1)
    tiers = {}
    for k, v in assignment.items():
        tiers[v['tier']] = tiers.get(v['tier'], 0) + 1
    print('pages:', len(pages), '| assigned:', len(assignment), '| unused plates:', len(unused))
    print('by tier:', tiers)

if __name__ == '__main__':
    main()
