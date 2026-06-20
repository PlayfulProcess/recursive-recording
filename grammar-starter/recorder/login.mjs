/*
 * login.mjs — one-time login. Opens a real (headed) browser window so YOU can log in
 * once; auto-saves the session to auth.json the moment it detects you're signed in.
 * After this, recorder.mjs runs fully headless with that session — no window, no typing.
 *
 *   node login.mjs                         # logs into recursive.eco (dev)
 *   node login.mjs --prod                  # logs into recursive.eco (prod)
 *   node login.mjs --github                # also open a github.com tab to log in
 *
 * IMPORTANT: run this from YOUR OWN terminal (it needs a desktop to draw the window).
 * It cannot be launched as a detached/background process — that's the `spawn UNKNOWN`
 * failure. A plain Chromium window opening (not your normal Chrome) is expected.
 *
 * auth.json holds your live session — it's gitignored. Never commit it.
 */
import { chromium } from 'playwright';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const prod = argv.includes('--prod');
const alsoGithub = argv.includes('--github');
const appUrl = prod ? 'https://flow.recursive.eco/library' : 'https://dev.flow.recursive.eco/library';

const browser = await chromium.launch({ headless: false });
const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });

const page = await context.newPage();
await page.goto(appUrl).catch(() => {});
if (alsoGithub) { const gh = await context.newPage(); await gh.goto('https://github.com/login').catch(() => {}); }

console.log('\n=== one-time login ===');
console.log('A Chromium window opened. Log in:');
console.log(`  • Tab 1 — ${appUrl}: sign in (email + the OTP code from your inbox).`);
if (alsoGithub) console.log('  • Tab 2 — github.com: sign in (+ 2FA if asked).');
console.log('Then just wait — I auto-detect the session and save it.\n');

// Poll for the Supabase auth cookie (project-ref agnostic). Optionally also wait for
// a github session cookie. Times out after 5 minutes.
const deadline = Date.now() + 5 * 60 * 1000;
let saved = false;
while (Date.now() < deadline) {
  const cookies = await context.cookies();
  const hasSupabase = cookies.some((c) => /^sb-.*-auth-token(\.\d+)?$/.test(c.name) && c.value);
  const hasGithub = !alsoGithub || cookies.some((c) => c.name === 'user_session' && c.domain.includes('github.com'));
  if (hasSupabase && hasGithub) {
    await context.storageState({ path: join(HERE, 'auth.json') });
    console.log('✓ Session saved to auth.json. You can close the window — recorder.mjs is ready.');
    saved = true;
    break;
  }
  await new Promise((r) => setTimeout(r, 2000));
}
if (!saved) console.log('Timed out waiting for login. Re-run `node login.mjs` and finish signing in.');

// Keep the window open a moment so you can read the message, then close.
await new Promise((r) => setTimeout(r, 4000));
await browser.close();
