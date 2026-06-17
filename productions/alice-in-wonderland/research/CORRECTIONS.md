# CORRECTIONS

Every fact that changed from the manifests (`data/editions.json`, `data/people.json`) after
web verification. Format: **field** — old → new · source · new-confidence.

Proposed corrected manifests live alongside this file as
`research/editions.proposed.json` and `research/people.proposed.json` (originals untouched).

## Editions

### nursery-1890 — The Nursery "Alice"
- **colorist** — `e-gertrude-thomson` → `[john-tenniel, edmund-evans]` (interior plates) · Thomson did the **cover only** · [@vam_nursery][@morgan_nursery][@wp_nursery] · **high**
- **cover_artist** — (absent) → `e-gertrude-thomson` · [@vam_nursery] · **high**
- **people** — add `edmund-evans` · [@wp_evans][@morgan_nursery] · **high**
- **confidence** — low → **high** (attribution resolved)
- Note: the "Thomson coloured the interior plates" claim (on her own Wikipedia page) is a **known error**.

### walker-1907
- **publisher** — `null` → `john-lane` (John Lane / The Bodley Head) · [@wp_illustrators][@marchpane_walker] · **medium-high**
- **illustrator identity** — implicitly settled → **disputed** (see people) · [@pdil_walker] · **low**
- **confidence** — low → **medium** (edition), illustrator identity remains **low**

### le-fanu-1910
- **publisher** — `null` → `british-esperanto-association` · [@wp_illustrators] · **medium**
- **title/nature** — generic English "Alice" → the **Esperanto** edition *La Aventuroj de Alicio en Mirlando* · [@wp_illustrators] · **medium**

### theaker-1911
- **publisher** — `null` → `macmillan` · [@panmac_theaker][@wp_theaker] · **high**
- **confidence** — low → **high**

### overnell-1912
- **publisher** — `null` → `everett` (Everett & Co.) · [@wp_illustrators][@worthpoint_overnell] · **medium**
- **illustrator** — `emily-overnell` (treated as a person) → **unverified name from a signature**; identity **unknown** · [@wp_illustrators] · **low**

### woodward-1913
- **publisher** — `null` → `g-bell` (G. Bell & Sons, "Queen's Treasure Series") · [@wp_woodward][@bushey_woodward] · **high**
- **confidence** — low → **high**

### hudson-1922
- **publisher** — `null` → `hodder-stoughton` (also a Boots the Chemist issue) · [@askart_hudson][@collectingalice_hudson] · **high**
- **confidence** — low → **high** (edition; artist lifespan still low)

### rountree-1928
- **publisher** — `null` → `collins` (Collins Clear-Type Press; 1928 combined Alice + Looking-Glass) · [@wp_rountree][@collectingalice_rountree] · **high**
- **note** — add earlier **1908 Thomas Nelson** edition; correct the common "Nister/Children's Press" misattribution; flag "1916 edition" as unverified · [@wp_rountree][@pook_rountree] · **high**
- **confidence** — low → **high**

### gutmann-1933 — MAJOR
- **year** — `1933` → **1907** (first edition, Dodge Publishing Co., New York) · [@wp_gutmann][@nocloo_gutmann] · **high**
- **publisher** — `null` → `dodge` · [@nocloo_gutmann] · **high**
- **id** — `gutmann-1933` is misleading; recommend `gutmann-1907` (1933 = a later J. Coker & Co. London reissue) · [@wp_gutmann] · **high**
- **confidence** — low → **high**

### (no change) under-ground-1864, tenniel-1865, rackham-1907
- Verified as stated; anchors confirmed: PG #19002 = Under Ground manuscript; PG #28885 = Rackham 1907; Tenniel 1865 = 42 illustrations, Dalziel-engraved, 1866 reissue · [@gutenberg_19002][@gutenberg_28885][@hermitage_firstedition][@aiw_tenniel] · **high**

## People

### e-gertrude-thomson
- **name** — "E. Gertrude Thomson" → full "Emily Gertrude Thomson" · [@wp_thomson] · **high**
- **role** — "colorist?" (interior plates) → **cover designer/colorist only** for The Nursery "Alice" · [@vam_nursery] · **high**
- **confidence** — low → **high**

### edmund-evans — ADDED
- New person: **Edmund Evans, 1826–1905**, colour wood-engraver/printer of The Nursery "Alice" · [@wp_evans][@odnb_evans] · **high**

### heinemann
- **confidence** — medium → **high**; William Henry Heinemann **1863–1920**, firm est. 1890 · [@wp_heinemann][@odnb_heinemann] · **high**

### william-h-walker
- **lifespan** — `?` → **unknown / disputed** (most likely American cartoonist William Henry Walker 1871–1938; conflated with architect W. H. Romaine-Walker 1854–1940) · [@pdil_walker] · **low**

### brinsley-le-fanu
- **name** — → "George Brinsley Sheridan Le Fanu" · [@onlinebooks_lefanu] · **high**
- **lifespan** — `1854–1929` → **1854/1855–1929** (birth year unsettled; death firm) · [@onlinebooks_lefanu][@artbiogs_lefanu] · **medium**

### harry-theaker
- **lifespan** — `1873–1954` confirmed (23 Jan 1954) · [@wp_theaker] · **high** (confidence low → high)

### emily-overnell
- **lifespan/identity** — `?` → **unknown / unverified**; name from a frontispiece signature, no biographical record · [@wp_illustrators] · **low**

### alice-b-woodward
- **lifespan** — `1862–1951` confirmed · [@wp_woodward] · **high** (confidence low → high)

### gwynedd-hudson
- **lifespan** — `fl. 1910s–1930s` → **c.1882–1935** (do NOT use "1909–1935") · [@askart_hudson][@wikidata_hudson] · **low**

### harry-rountree
- **lifespan** — `1878–1950` confirmed (NZ-born) · [@wp_rountree] · **high** (confidence low → high)

### bessie-pease-gutmann
- **lifespan** — `1876–1960` confirmed (American) · [@wp_gutmann] · **high** (confidence low → high)
- **made** — her Alice is the **1907 Dodge** edition (manifest's 1933 is a later reissue)

### New publisher/firm ids referenced by corrected editions (stubs to add)
`john-lane` (John Lane / The Bodley Head), `british-esperanto-association`, `everett` (Everett & Co.),
`g-bell` (G. Bell & Sons), `hodder-stoughton`, `collins` (Collins Clear-Type Press),
`dodge` (Dodge Publishing Co.). Added to `people.proposed.json` as publisher stubs.
