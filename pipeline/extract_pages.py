# -*- coding: utf-8 -*-
import re, html, json, os
D = r'C:\Users\ferna\AppData\Local\Temp\alice-qa'
s = open(os.path.join(D, 'book.html'), encoding='utf-8').read()

# Each spread carries data-spread="chN-P". Slice from one to the next; strip tags for text.
marks = [(m.start(), m.group(1)) for m in re.finditer(r'data-spread="(ch\d+-\d+)"', s)]
pages = []
for i, (pos, key) in enumerate(marks):
    end = marks[i+1][0] if i+1 < len(marks) else pos + 8000
    block = s[pos:end]
    block = block[block.find('>')+1:]          # skip past the rest of the opening tag (drops data-ch-ills JSON)
    block = re.sub(r"data-ch-ills='[^']*'", ' ', block)  # belt-and-suspenders
    # drop the image caption (figcaption / .credit) heuristically: remove alt="..." and small caption spans
    txt = html.unescape(re.sub(r'<[^>]+>', ' ', block))
    txt = re.sub(r'\s+', ' ', txt).strip()
    # strip a leading "[Artist — caption] NN " image-caption echo + printed page number
    txt = re.sub(r'^\W*(?:[A-Za-z][^0-9]{0,160}?\s)?\d{1,3}\s+', '', txt, count=1)
    m = re.match(r'(\d+)-(\d+)', key[2:])
    ch = int(key[2:].split('-')[0])
    # first sentence = up to first . ? ! followed by space/quote
    fs = re.split(r'(?<=[.?!”])\s', txt.strip())
    first_sentence = (fs[0] if fs else txt)[:160]
    pages.append({'key': key, 'order': i, 'chapter': ch,
                  'first_sentence': first_sentence, 'text': txt[:600]})

json.dump(pages, open(os.path.join(D, 'pages.json'), 'w', encoding='utf-8'), indent=0, ensure_ascii=False)
print('pages extracted:', len(pages))
for p in pages[:6]:
    print(p['key'], '|', p['first_sentence'][:80])
