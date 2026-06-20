# Connect Claude Desktop to the recursive.eco MCP (one time)

The grammar MCP lives at:

```
https://flow.recursive.eco/api/mcp
```

It authenticates **as your recursive.eco account**, so every tool acts on *your* grammars
and storage. Two ways to connect — the Connector flow is easiest.

## Option A — Connector (recommended, no token to manage)
1. Open **Claude Desktop → Settings → Connectors → Add custom connector**.
2. Paste the URL above and add it.
3. Claude opens a **sign-in** page for recursive.eco (OAuth). Sign in with your account.
4. Done — the recursive.eco tools (`create_grammar`, `add_items`, `commons_image_search`,
   …) now appear in Claude Desktop. Nothing to copy, nothing secret on disk.

## Option B — API token + `mcp-remote` (config file)
Use this if you prefer a token or the connector isn't available.

1. **Get your token:** sign in at [recursive.eco](https://recursive.eco) → **Account** →
   **API / MCP access** → **Generate token** → copy it. (You can Revoke/Rotate it there
   anytime. Treat it like a password — it *is* your account authority.)
2. **Edit `claude_desktop_config.json`** (Claude Desktop → Settings → Developer → Edit Config):
   ```json
   {
     "mcpServers": {
       "recursive-eco": {
         "command": "npx",
         "args": [
           "-y", "mcp-remote",
           "https://flow.recursive.eco/api/mcp",
           "--header", "Authorization: Bearer YOUR_TOKEN_HERE"
         ]
       }
     }
   }
   ```
3. **Restart Claude Desktop.** Ask "list the recursive.eco MCP tools" to confirm.

## Safety
- **Never commit your token** (or `claude_desktop_config.json` if it contains one). This
  template's `.gitignore` already excludes `*.token` / `mcp-token.txt` / `auth.json`.
- The token grants your account's data powers — revoke + regenerate it in Account if it
  ever leaks.

## Testing against dev
Swap the URL to `https://dev.flow.recursive.eco/api/mcp` to hit the dev environment (a
separate database — your prod grammars won't be there). Use prod for real work.
