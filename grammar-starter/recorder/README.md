# Course recorder (local)

Drive a real recursive.eco flow and screenshot each step into a course. Runs **on your
machine** with **your own** login — there's no server-side screenshotting (a server
can't, and shouldn't, hold your session). This is the reliable "method #2" capture:
it grabs the page's *rendered content*, so it works headless and ignores whatever's on
your screen (no foreground-tab juggling).

## Setup (one time)
```bash
cd grammar-starter/recorder
npm install
npx playwright install chromium
```

## Capture a flow
```bash
# Public-only shots (no login needed):
node recorder.mjs flows/build-a-grammar.example.json

# For authenticated shots (the editor, the Grammar Assistant), log in once:
node login.mjs                 # opens a window; sign in; it auto-saves auth.json
node login.mjs --github        # also log into GitHub if your flow has GitHub steps
# then:
node recorder.mjs flows/build-a-grammar.example.json
```
Add `--headed` to watch it run. Output lands in `out/<flow>/NN-step.png` + `steps.json`.

## Make your own flow
Copy `flows/build-a-grammar.example.json` and edit the `steps`. Each step:
- `goto`: a path (`/create`) or full URL. `click` / `fill`: interact. `wait_for`: wait for a selector.
- `highlight`: a `data-tour="..."` selector to outline (the app's stable selectors — they're
  built to survive UI changes; `?tour-debug=1` on any page helps you find them).
- `caption`: the line that goes under the screenshot in the course.
- `authed: true`: this step needs `auth.json` (login first).
- `full_page: true`: capture the whole scrollable page.

Re-run any time the UI changes to regenerate the course screenshots.

## Turn it into a course
The screenshots + `steps.json` captions are your course material. Paste them into a course
MDX (frontmatter + an H2/H3 per step + `![caption](out/<flow>/NN-step.png)`), or ask Claude
to assemble the MDX from `steps.json`.

## Don't commit secrets
`auth.json` is your live session and `out/` is generated — both are gitignored. Never commit
`auth.json`.
