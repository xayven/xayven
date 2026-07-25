# Xayven Claude Code Integration

This directory contains the Claude Code skill bundle for Xayven.

## User Flow

1. Open Xayven Settings > Integrations.
2. Add a Claude Agent.
3. Copy the full setup commands shown after the generated token.
4. Toggle the tools Claude is allowed to use.
5. Configure the terminal Claude Code session:

```bash
export XAYVEN_URL=http://your-xayven-host:7777
export XAYVEN_API_TOKEN=xayven_generated_token
mkdir -p ~/.claude
curl -fsSL -H "Authorization: Bearer $XAYVEN_API_TOKEN" "$XAYVEN_URL/api/claude/plugin.zip" -o /tmp/xayven-claude-skill.zip
python3 -m zipfile -e /tmp/xayven-claude-skill.zip ~/.claude/
```

Claude Code auto-loads anything under `~/.claude/skills/`, so the `xayven` skill is
available in any session that has `XAYVEN_URL` and `XAYVEN_API_TOKEN` in its
environment.

## What's in the bundle

- `skills/xayven/SKILL.md` — the skill definition Claude Code reads.
- `skills/xayven/scripts/xayven_api.py` — small helper that calls the scoped
  `/api/codex/*` endpoints (these are the canonical scope-gated agent API; the
  `codex` path is historic and shared by all agent integrations).

## Scope enforcement

The token is scope-gated. Every tool surface is checked server-side in Xayven,
so even if Claude tries to call a forbidden endpoint, it gets `403` until the
user enables the matching toggle in Settings > Integrations > Claude Agent.

