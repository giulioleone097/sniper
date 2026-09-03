#!/bin/sh
# sniper core-context: SessionStart / SubagentStart hook.
# Injects core/SNIPER.md as additionalContext so the doctrine is active every
# turn. hookEventName comes from the hook_event_name field on stdin, default
# SessionStart. Any parse or read error: print nothing, exit 0.

CORE_FILE="$(dirname "$0")/../core/SNIPER.md"

exec python3 -c '
import sys, json

core_path = sys.argv[1]

event = "SessionStart"
try:
    raw = sys.stdin.read()
    if raw.strip():
        data = json.loads(raw)
        e = data.get("hook_event_name")
        if isinstance(e, str) and e:
            event = e
except Exception:
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
