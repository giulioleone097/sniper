#!/bin/sh
# sniper core-context: session/subagent-start hook.
# Injects core/SNIPER.md so the doctrine is active every turn: Claude Code,
# Codex and Devin read hookSpecificOutput.additionalContext (event
# SessionStart/SubagentStart), Cursor reads top-level additional_context
# (event sessionStart). hookEventName comes from the hook_event_name field on
# stdin, default SessionStart. Any parse or read error: print nothing, exit 0.

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

# A project that carries the block (installed by /sniper:setup) already loads it as project
# instructions, and non-fork subagents receive the same instruction files; injecting again would
# cost the doctrine twice. The hook runs in the session cwd, which may be a subdirectory, so the
# block is looked for up the tree to the filesystem root.
cwd = data.get("cwd") if isinstance(data, dict) else None
d = os.path.abspath(cwd) if cwd else os.getcwd()
while d:
    for name in ("AGENTS.md", "CLAUDE.md"):
        try:
            if "<!-- sniper:core:start -->" in open(os.path.join(d, name)).read():
                sys.exit(0)
        except Exception:
            pass
    parent = os.path.dirname(d)
    d = parent if parent != d else None

# The same block may live in a host-global rules file (installed by
# scripts/install-devin.sh or by hand): those load in every session too, so
# injecting again would still cost the doctrine twice. Cursor never sends
# hook_event_name and does not read those files, so the check is skipped there.
home = os.path.expanduser("~")
is_cursor = isinstance(data, dict) and "hook_event_name" not in data and (
    "composer_mode" in data or "is_background_agent" in data
)
if not is_cursor:
    for name in (".config/devin/AGENTS.md", ".claude/CLAUDE.md", ".codex/AGENTS.md"):
        try:
            if "<!-- sniper:core:start -->" in open(os.path.join(home, name)).read():
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
            agent = str((data or {}).get("agent_type") or (data or {}).get("agentType") or (data or {}).get("subagent_type") or "")
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
    },
    "additional_context": core,
}
sys.stdout.write(json.dumps(payload))
sys.exit(0)
' "$CORE_FILE"
