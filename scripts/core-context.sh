#!/bin/sh
# sniper core-context: SessionStart / SubagentStart hook.
# Injects core/SNIPER.md as additionalContext so the doctrine is active every
# turn. hookEventName comes from the hook_event_name field on stdin, default
# SessionStart. Any parse or read error: print nothing, exit 0.

CORE_FILE="$(dirname "$0")/../core/SNIPER.md"

exec python3 -c '
import os, sys, json

core_path = sys.argv[1]

event = "SessionStart"
data = {}
try:
    raw = sys.stdin.read()
    if raw.strip():
        data = json.loads(raw)
        e = data.get("hook_event_name")
        if isinstance(e, str) and e:
            event = e
except Exception:
    pass

# A project that carries the block (installed by /sniper:setup) already loads it as
# project instructions; injecting again would cost the doctrine twice.
if event == "SessionStart":
    cwd = data.get("cwd") if isinstance(data, dict) else None
    for name in ("AGENTS.md", "CLAUDE.md"):
        try:
            if cwd and "<!-- sniper:core:start -->" in open(os.path.join(cwd, name)).read():
                sys.exit(0)
        except Exception:
            pass

# SNIPER_SUBAGENT_MATCHER: an unanchored, case-insensitive regex; when set, subagents whose
# agent_type does not match get no doctrine. Unset means every subagent, as before. A bad
# regex counts as unset rather than failing the hook.
if event == "SubagentStart":
    pat = os.environ.get("SNIPER_SUBAGENT_MATCHER")
    if pat:
        import re
        try:
            agent = str((data or {}).get("agent_type") or (data or {}).get("agentType") or "")
            if not re.search(pat, agent, re.I):
                sys.exit(0)
        except re.error:
            pass

try:
    with open(core_path, "r") as f:
        core = f.read()
except Exception:
    sys.exit(0)

payload = {
    "hookSpecificOutput": {
        "hookEventName": event,
        "additionalContext": core,
    }
}
sys.stdout.write(json.dumps(payload))
sys.exit(0)
' "$CORE_FILE"
