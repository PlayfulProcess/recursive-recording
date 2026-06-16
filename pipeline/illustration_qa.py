# -*- coding: utf-8 -*-
"""illustration_qa.py — the vision loop for fixing a kids' book's pictures.

For each passage it produces a QA WORKSHEET (an illustration-map). The one step a script
can't do alone is SEE the image — that's an agent/vision action (download the image bytes and
look). This file structures that loop so the agent fills in a verdict and the regenerate prompt
is ready to fire at the recursive-eco MCP `generate_item_image`.

Loop per passage:
  1. SEE     — download illustration.image_url locally; view it (agent vision).  [needs network]
  2. MATCH   — does the picture depict THIS passage? set `depicts_passage`.
  3. ORDER   — if it belongs to a different passage, set `reorder_to`.
  4. CRITIQUE— note problems (e.g. "door drawn huge though text says 'fifteen inches'").
  5. DECIDE  — action: keep | reorder | regenerate.  If regenerate, use illustration.prompt.
  6. APPLY   — regenerate via MCP, then re-SEE to confirm; record new_url.

  python3 pipeline/illustration_qa.py        # writes productions/alice-in-wonderland/illustration-map.json + .md
"""
import json, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JSON = os.path.join(ROOT, "karaoke", "alice-passages.json")
OUTJ = os.path.join(ROOT, "productions", "alice-in-wonderland", "illustration-map.json")
OUTM = os.path.join(ROOT, "productions", "alice-in-wonderland", "illustration-qa.md")

# cheap heuristics: words in the text that imply a SIZE/quantity the picture must honor.
SIZE_CUES = re.compile(r'\b(tiny|small|little|fifteen inches|ten inches|nine feet|huge|giant|enormous|tall|grew|shrink|shutting up)\b', re.I)

def worksheet():
    data = json.load(open(JSON, encoding="utf-8"))
    rows = []
    for i, p in enumerate(data["passages"]):
        ill = p.get("illustration", {})
        text = " ".join(p["lines"])
        cues = sorted(set(m.group(0).lower() for m in SIZE_CUES.finditer(text)))
        # PROVENANCE GATE: only AI-generated art may be REMADE. Public-domain / human art
        # (e.g. original Tenniel engravings) may be reordered but NEVER regenerated.
        prov = (ill.get("provenance") or "unknown").lower()      # ai | public-domain | human | unknown
        eligible_for_remake = prov == "ai"
        status = ill.get("status")
        if status in ("regenerated", "reordered"):
            action = status if (status != "regenerated" or eligible_for_remake) else "review"
        else:
            action = "review"
        rows.append({
            "passage_index": i,
            "passage_id": p["id"],
            "title": p.get("title"),
            "text": text,
            "size_cues_to_honor": cues,             # the picture must match these
            "current_image_url": ill.get("image_url"),
            "has_offline_placeholder_svg": bool(ill.get("svg")),
            "provenance": prov,
            "eligible_for_remake": eligible_for_remake,   # False → reorder only, do NOT regenerate
            # --- agent fills these after SEEing the image ---
            "seen": False,
            "depicts_passage": None,                # true/false
            "reorder_to": None,                     # passage_id if it belongs elsewhere
            "problems": [m.strip() for m in [ill.get("regenerated_reason")] if m] or [],
            "action": action,                       # review | keep | reorder | regenerate
            "regenerate_prompt": ill.get("prompt", "") if eligible_for_remake else "",
            "new_url": None,
            "reverified": False,
        })
    return data, rows

def build():
    data, rows = worksheet()
    os.makedirs(os.path.dirname(OUTJ), exist_ok=True)
    json.dump({"production": data.get("title"), "passages": rows}, open(OUTJ, "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    md = ["# Illustration QA worksheet — Alice", "",
          "Fill `seen / depicts_passage / problems / action / new_url` after viewing each image. "
          "`action`: keep · reorder · regenerate. **Provenance gate:** only `eligible_for_remake` "
          "(AI-generated) images may be regenerated; public-domain / human art may be reordered "
          "but never remade. Regenerate via recursive-eco `generate_item_image`.", ""]
    for r in rows:
        gate = "remake OK" if r["eligible_for_remake"] else "REORDER ONLY (provenance=%s)" % r["provenance"]
        md += [f"## {r['passage_index']}. {r['title']}  ·  `{r['action']}`  ·  {gate}",
               f"- text: {r['text']}",
               f"- **size cues the picture MUST honor:** {', '.join(r['size_cues_to_honor']) or '(none)'}",
               f"- problems: {'; '.join(r['problems']) or '—'}",
               f"- regenerate prompt: {(r['regenerate_prompt'][:160]+'…') if r['regenerate_prompt'] else '(blocked — not AI provenance)'}", ""]
    open(OUTM, "w", encoding="utf-8").write("\n".join(md))
    flagged = [r for r in rows if r["action"] in ("regenerate", "review")]
    remakeable = [r for r in rows if r["eligible_for_remake"]]
    print(f"wrote {os.path.relpath(OUTJ, ROOT)} + .md — {len(rows)} passages, "
          f"{len(flagged)} need a vision pass, {len(remakeable)} eligible for remake (AI provenance)")

if __name__ == "__main__":
    build()
