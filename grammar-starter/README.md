# Grammar Starter — build & illustrate a grammar with Claude + the recursive.eco MCP

A **copy-me template** for making a *grammar* — a symbolic system like a tarot deck,
an I Ching book, an astrology set, or an illustrated story (Alice in Wonderland, a
kids' book) — almost entirely by **talking to Claude Desktop**, which drives the
[recursive.eco](https://recursive.eco) grammar MCP.

You describe what you want; Claude creates the grammar, writes the cards/entries,
**illustrates** them (AI art or public-domain scans from Wikimedia), optionally adds
narration/karaoke, and publishes it — all through the MCP, scoped to *your* account.

## What you get
- **`CLAUDE.md`** — the build playbook Claude reads. It teaches the whole workflow
  (create → author → illustrate → attribute → narrate → publish) and the tool menu.
- **`MCP_SETUP.md`** — one-time: get your MCP token + connect Claude Desktop.
- **`recorder/`** — an optional **local** screenshot recorder (Playwright) for turning
  a real in-app flow into a step-by-step **course** with screenshots. Runs on your
  machine with your own login; nothing server-side.

## The 60-second start
1. **Copy this folder** into a new repo (e.g. `my-astrology-deck`).
2. Follow **`MCP_SETUP.md`** once to connect Claude Desktop to the recursive.eco MCP.
3. Open Claude Desktop and say, e.g.:
   > "Read CLAUDE.md. Build me a 22-card Major Arcana tarot deck called *Forest Tarot*.
   > Source public-domain Rider–Waite plates from Wikimedia for each card, set the
   > license + artist as the credit, write upright/reversed meanings, then publish it."
4. Claude does it via the MCP. Open the link it returns to see your deck.

## Is it safe that this repo is public?
Yes — **the template and recorder contain no secrets.** Two rules keep it that way,
already wired into `.gitignore`:
- **Never commit your MCP token** (it's your account credential — keep it in Claude
  Desktop's config or an untracked file).
- **Never commit `auth.json`** (the recorder's saved browser login).
The grammar *content* you make is yours to license (this open layer is CC-BY-SA); the
recursive.eco *platform code* stays private — this template only uses the public MCP +
the published [grammar JSON format](../GRAMMAR_FORMAT.md).

## Works for any domain
The exact same flow builds a tarot deck, an I Ching book (64 hexagrams), an astrology
interpretation set, or an illustrated `Alice in Wonderland` — only the prompt changes.
The MCP tools and `CLAUDE.md` are domain-general.
