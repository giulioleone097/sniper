#!/bin/sh
# sniper acceptance in one command: manifests, components, guard fixtures, doctrine sync.
# Exit 1 on the first failing group; prints what failed.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail=0

for t in "" .claude-plugin/plugin.json skills agents; do
  if out=$(claude plugin validate --strict "$ROOT/$t" 2>&1); then
    echo "validate ${t:-marketplace}: ok"
  else
    echo "validate ${t:-marketplace}: FAIL"; echo "$out" | tail -5; fail=1
  fi
done

sh "$ROOT/scripts/test-guard.sh" || fail=1

# Repository rules, executed: skill bodies <= 120 lines, references <= 80, no host-specific
# env var in a skill body (Codex knows none of them there), every script parses, and the
# two detectors answer on this very repository.
for f in "$ROOT"/skills/*/SKILL.md; do
  n=$(wc -l < "$f" | tr -d ' '); [ "$n" -le 120 ] || { echo "rules: $f has $n lines (> 120)"; fail=1; }
done
for f in "$ROOT"/skills/*/references/*.md; do
  n=$(wc -l < "$f" | tr -d ' '); [ "$n" -le 80 ] || { echo "rules: $f has $n lines (> 80)"; fail=1; }
done
# the doctrine travels as hook additionalContext: Claude Code cuts it at 10,000 characters and Codex
# near 2,500 tokens, both silently replaced by a file preview, so it stays under 9,000 bytes
n=$(wc -c < "$ROOT/core/SNIPER.md" | tr -d ' '); [ "$n" -le 9000 ] || { echo "rules: core/SNIPER.md is $n bytes; hook additionalContext is cut at 10,000 chars (Codex ~2,500 tokens)"; fail=1; }
if grep -rn 'CLAUDE_SKILL_DIR\|\${CLAUDE_PLUGIN_ROOT}' "$ROOT"/skills/*/SKILL.md "$ROOT"/skills/*/references "$ROOT"/agents >/dev/null 2>&1; then
  echo "rules: host env var inside a skill or agent body"; grep -rln 'CLAUDE_SKILL_DIR\|\${CLAUDE_PLUGIN_ROOT}' "$ROOT"/skills/*/SKILL.md "$ROOT"/skills/*/references "$ROOT"/agents; fail=1
fi
# Codex shortens skill descriptions to ~45 characters when many plugins are installed, so the
# trigger must sit in the first clause; both hosts route on the description, so keep it short.
for f in "$ROOT"/skills/*/SKILL.md; do
  d=$(grep -m1 '^description:' "$f" | sed 's/^description: //')
  case "$d" in "Use when "*) ;; *) echo "rules: $f description must open with the trigger (Use when ...)"; fail=1;; esac
  w=$(printf '%s' "$d" | wc -w | tr -d ' '); [ "$w" -le 70 ] || { echo "rules: $f description has $w words (> 70)"; fail=1; }
done
for d in "$ROOT"/skills/*/; do
  [ -f "$d/agents/openai.yaml" ] || { echo "rules: $d has no Codex sidecar (agents/openai.yaml)"; fail=1; }
done
# every references/ or scripts/ file a skill names must exist: beside the skill, at the plugin root, or under the stage it names
python3 - "$ROOT" <<'PYEOF' || fail=1
import glob, os, re, sys
root = sys.argv[1]; bad = 0
pat = r'`(?:<this skill>/|<plugin root>/skills/([a-z]+)/)?(references/[a-z-]+\.md|scripts/[a-z_-]+\.(?:py|sh))`'
for f in glob.glob(f"{root}/skills/*/SKILL.md"):
    d = os.path.dirname(f)
    for stage, m in set(re.findall(pat, open(f).read())):
        where = [f"{root}/skills/{stage}"] if stage else [d, root]
        if not any(os.path.exists(os.path.join(x, m)) for x in where):
            print(f"rules: {f} names {m}, which does not exist under {where}"); bad += 1
sys.exit(1 if bad else 0)
PYEOF
for s in "$ROOT"/scripts/*.sh; do sh -n "$s" || { echo "rules: $s does not parse"; fail=1; }; done
sh "$ROOT/scripts/tracker.sh" "$ROOT" | grep -q '^forge=' || { echo "rules: tracker.sh gave no forge"; fail=1; }
sh "$ROOT/scripts/checks.sh" "$ROOT" | grep -qE '^(project=|none=1)' || { echo "rules: checks.sh gave no answer"; fail=1; }
sh "$ROOT/scripts/debt.sh" "$ROOT" | grep -qE '^(markers=|none=1)' || { echo "rules: debt.sh gave no answer"; fail=1; }
python3 "$ROOT/evals/run.py" --selftest >/dev/null 2>&1 || { echo "rules: evals selftest failed (a scorer no longer separates good from bad)"; fail=1; }
[ "$fail" -eq 0 ] && echo "rules: ok"

# hooks and installer shape per host: each hooks file may name only the events
# its host fires, and every user-level installer must exist and parse
python3 - "$ROOT" <<'PYEOF' || fail=1
import json, os, sys
root = sys.argv[1]
bad = 0
EVENTS = {
    "hooks/hooks.json": {"SessionStart", "SubagentStart", "PreToolUse"},          # Claude Code + Codex
    "hooks.json": {"PreToolUse", "PostToolUse", "PermissionRequest",              # Devin (plugin root)
                   "UserPromptSubmit", "Stop", "PostCompaction", "SessionStart", "SessionEnd"},
    "hooks/cursor-hooks.json": {"sessionStart", "sessionEnd", "preToolUse",       # Cursor
                   "postToolUse", "postToolUseFailure", "subagentStart", "subagentStop",
                   "beforeShellExecution", "afterShellExecution", "beforeMCPExecution",
                   "afterMCPExecution", "beforeReadFile", "afterFileEdit", "beforeSubmitPrompt",
                   "preCompact", "stop", "afterAgentResponse", "afterAgentThought",
                   "beforeTabFileRead", "afterTabFileEdit", "workspaceOpen"},
}
for path, allowed in EVENTS.items():
    body = json.load(open(f"{root}/{path}"))
    inner = body.get("hooks")
    if isinstance(inner, dict):
        events = set(inner.keys())
    else:
        events = set(body.keys()) - {"description", "version"}  # Devin bare format
    unknown = events - allowed
    if unknown:
        print(f"rules: {path} names events its host never fires: {sorted(unknown)}"); bad += 1
for f in ("scripts/install-devin.sh", "scripts/install-cursor.sh",
          "scripts/install-codex-agents.sh", "rules/sniper-core.mdc"):
    if not os.path.exists(f"{root}/{f}"):
        print(f"rules: {f} missing"); bad += 1
sys.exit(1 if bad else 0)
PYEOF

python3 - "$ROOT" <<'EOF' || fail=1
import json, re, sys
root = sys.argv[1]
for f in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
          ".codex-plugin/plugin.json", ".agents/plugins/marketplace.json",
          ".devin-plugin/plugin.json", ".cursor-plugin/plugin.json",
          "hooks/hooks.json", "hooks.json", "hooks/cursor-hooks.json",
          "agents/models.json"):
    json.load(open(f"{root}/{f}"))
reg = json.load(open(f"{root}/agents/models.json"))
for host, h in reg["hosts"].items():
    missing = set(reg["tiers"]) - set(h["models"])
    if missing:
        sys.exit(f"models.json: host {host} lacks tiers {sorted(missing)}")
import glob
for f in glob.glob(f"{root}/agents/*.md"):
    m = re.search(r"^model: (\w+)$", open(f).read(), re.M)
    if m and m.group(1) not in reg["tiers"]:
        sys.exit(f"models.json: {f} declares unknown tier {m.group(1)}")
core = open(f"{root}/core/SNIPER.md").read().strip()
for f in ("AGENTS.md", "rules/sniper-core.mdc"):
    m = re.search(r"<!-- sniper:core:start -->\n(.*?)\n<!-- sniper:core:end -->", open(f"{root}/{f}").read(), re.S)
    if not m or m.group(1).strip() != core:
        sys.exit(f"doctrine: {f} block differs from core/SNIPER.md")
v = [json.load(open(f"{root}/{f}"))["version"] for f in (
    ".claude-plugin/plugin.json", ".codex-plugin/plugin.json",
    ".devin-plugin/plugin.json", ".cursor-plugin/plugin.json")]
if len(set(v)) != 1:
    sys.exit(f"version mismatch: {v}")
print(f"manifests, doctrine sync, version {v[0]}: ok")
EOF

if [ "$fail" -eq 0 ]; then echo "check: ok"; else echo "check: FAIL"; exit 1; fi
