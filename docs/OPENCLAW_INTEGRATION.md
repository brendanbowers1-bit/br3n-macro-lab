# OpenClaw + OpenAI + FX Lab

FX Lab does **not** call OpenAI directly. **OpenClaw** is the agent layer: it uses your configured OpenAI model to read FX Lab outputs, run scripts, and reply (including iMessage).

## What you already have

| Piece | Status |
|-------|--------|
| OpenClaw gateway | `~/.openclaw/openclaw.json` — local mode, port 18789 |
| OpenAI model | `openai/gpt-5.4` (primary) |
| OpenAI auth | `openai:default` profile, `api_key` mode |
| iMessage channel | Enabled for your allowlist |
| Codex plugin | Enabled |

## Connect FX Lab

### 1. Install the FX Lab skill into OpenClaw workspace

```bash
openclaw skills install /Users/brendanbowers/fx_regime_lab/openclaw/skills/fx-lab --as fx-lab
openclaw gateway restart
```

Skills load from `~/.openclaw/workspace/skills/` on the next agent session.

### 2. Ensure OpenAI API key is available to the gateway

OpenClaw reads `OPENAI_API_KEY` for the `openai:default` profile. Set it in your shell profile or gateway env:

```bash
# One-time onboard (stores auth profile)
openclaw onboard --auth-choice openai-api-key --openai-api-key "$OPENAI_API_KEY"

# Or export before starting gateway
export OPENAI_API_KEY="sk-..."
openclaw gateway restart
```

Verify:

```bash
openclaw models list --provider openai
```

### 3. Test FX Lab snapshot (no LLM)

```bash
cd ~/fx_regime_lab && source .venv/bin/activate
python scripts/openclaw_fx_lab_snapshot.py
python scripts/openclaw_fx_lab_snapshot.py --json
```

### 4. Test via OpenClaw

Message your agent (iMessage or control UI):

> What's the FX Lab snapshot? Use the fx-lab skill.

Or in a new session, ask it to run:

```bash
cd /Users/brendanbowers/fx_regime_lab && source .venv/bin/activate && python scripts/openclaw_fx_lab_snapshot.py
```

## Architecture

```
You (iMessage / UI)
    ↓
OpenClaw gateway  ←→  OpenAI (gpt-5.4)  ← reasoning & replies
    ↓
Shell / read tools
    ↓
~/fx_regime_lab  ← Python pipelines, CSVs, reports (no OpenAI)
```

## Optional: heartbeat check

Edit `~/.openclaw/workspace/HEARTBEAT.md` to add:

```markdown
- FX Lab: run `python /Users/brendanbowers/fx_regime_lab/scripts/openclaw_fx_lab_snapshot.py` once per day; alert Brendan only if regime changed or pipeline outputs are missing.
```

## Security

- Do not commit `OPENAI_API_KEY` or OpenClaw gateway tokens
- FX Lab remains research-only; OpenClaw should not place trades
- iMessage allowlist stays in `openclaw.json` → `channels.imessage.allowFrom`

## Public site

After pipeline runs:

```bash
python scripts/build_site.py
git add reports/publication && git commit -m "Update site" && git push
```

Live: https://brendanbowers1-bit.github.io/br3n-macro-lab/
