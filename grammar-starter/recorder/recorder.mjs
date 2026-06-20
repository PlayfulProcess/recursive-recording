/*
 * recorder.mjs — replay a flow and screenshot each step into a course.
 *
 * Headless by default; uses the saved login from `auth.json` (run `node login.mjs`
 * once) so it can capture authenticated views. This is "method #2" — it captures the
 * page's RENDERED content, so it works on background/headless pages and is immune to
 * what's on your screen (no foreground tab, no window juggling).
 *
 *   npm install && npx playwright install chromium     # one time
 *   node login.mjs                                      # one time (logs in, saves auth.json)
 *   node recorder.mjs flows/build-a-grammar.example.json
 *   node recorder.mjs flows/<your-flow>.json --headed   # watch it run
 *
 * Output: out/<flow.name>/NN-<step>.png  +  out/<flow.name>/steps.json
 * Embed the PNGs in a course MDX, or upload them wherever you publish.
 */
import { chromium } from 'playwright';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const flowPath = argv.find((a) => !a.startsWith('--'));
const headed = argv.includes('--headed');
if (!flowPath) {
  console.error('Usage: node recorder.mjs <flow.json> [--headed]');
  process.exit(1);
}

const flow = JSON.parse(readFileSync(resolve(flowPath), 'utf8'));
const name = flow.name || 'flow';
const baseUrl = (flow.base_url || 'https://dev.flow.recursive.eco').replace(/\/+$/, '');
const outDir = join(HERE, 'out', name);
mkdirSync(outDir, { recursive: true });

const authFile = join(HERE, 'auth.json');
const hasAuth = existsSync(authFile);
const pad = (n) => String(n).padStart(2, '0');

const browser = await chromium.launch({ headless: !headed });
const context = await browser.newContext({
  viewport: flow.viewport || { width: 1440, height: 900 },
  ...(hasAuth ? { storageState: authFile } : {}),
});
const page = await context.newPage();

const manifest = [];
let i = 0;
for (const step of flow.steps || []) {
  i += 1;
  const label = `${pad(i)}-${(step.name || 'step').replace(/[^a-z0-9]+/gi, '-').toLowerCase()}`;
  try {
    if (step.goto) {
      const url = /^https?:\/\//.test(step.goto) ? step.goto : baseUrl + step.goto;
      await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 });
    }
    if (step.fill) await page.fill(step.fill.selector, step.fill.value);
    if (step.click) await page.click(step.click, { timeout: 15000 });
    if (step.wait_for) await page.waitForSelector(step.wait_for, { timeout: 20000 }).catch(() => {});
    await page.waitForTimeout(step.wait_ms ?? 1200); // let the SPA settle / animations finish

    // Optional: outline a data-tour element so the screenshot "points" at it.
    if (step.highlight) {
      await page.evaluate((sel) => {
        const el = document.querySelector(sel);
        if (el) { el.setAttribute('data-rec-outline', '1'); el.style.outline = '3px solid #f59e0b'; el.style.outlineOffset = '2px'; el.scrollIntoView({ block: 'center' }); }
      }, step.highlight).catch(() => {});
      await page.waitForTimeout(300);
    }

    const file = `${label}.png`;
    await page.screenshot({ path: join(outDir, file), fullPage: !!step.full_page });

    if (step.highlight) {
      await page.evaluate(() => { const el = document.querySelector('[data-rec-outline]'); if (el) { el.style.outline = ''; el.removeAttribute('data-rec-outline'); } }).catch(() => {});
    }

    manifest.push({ n: i, name: step.name, caption: step.caption || step.name || '', screenshot: `out/${name}/${file}`, authed: !!step.authed });
    console.log(`  ✓ ${label}`);
  } catch (e) {
    manifest.push({ n: i, name: step.name, error: e instanceof Error ? e.message : String(e) });
    console.warn(`  ✗ ${label}: ${e instanceof Error ? e.message : e}${step.authed && !hasAuth ? '  (authed step — run `node login.mjs` first)' : ''}`);
  }
}

writeFileSync(join(outDir, 'steps.json'), JSON.stringify({ name, base_url: baseUrl, authed: hasAuth, steps: manifest }, null, 2));
await browser.close();
console.log(`\nDone. ${manifest.filter((s) => !s.error).length}/${manifest.length} shots → ${outDir}`);
if (!hasAuth && (flow.steps || []).some((s) => s.authed)) {
  console.log('NOTE: authed steps were skipped — run `node login.mjs` once, then re-run.');
}
