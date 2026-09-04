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
if grep -rn 'CLAUDE_SKILL_DIR\|\${CLAUDE_PLUGIN_ROOT}' "$ROOT"/skills/*/SKILL.md "$ROOT"/skills/*/references "$ROOT"/agents >/dev/null 2>&1; then
  echo "rules: host env var inside a skill or agent body"; grep -rln 'CLAUDE_SKILL_DIR\|\${CLAUDE_PLUGIN_ROOT}' "$ROOT"/skills/*/SKILL.md "$ROOT"/skills/*/references "$ROOT"/agents; fail=1
fi
for s in "$ROOT"/scripts/*.sh; do sh -n "$s" || { echo "rules: $s does not parse"; fail=1; }; done
sh "$ROOT/scripts/tracker.sh" "$ROOT" | grep -q '^forge=' || { echo "rules: tracker.sh gave no forge"; fail=1; }
sh "$ROOT/scripts/checks.sh" "$ROOT" | grep -qE '^(project=|none=1)' || { echo "rules: checks.sh gave no answer"; fail=1; }
[ "$fail" -eq 0 ] && echo "rules: ok"

python3 - "$ROOT" <<'EOF' || fail=1
import json, re, sys
root = sys.argv[1]
for f in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
          ".codex-plugin/plugin.json", ".agents/plugins/marketplace.json", "hooks/hooks.json"):
    json.load(open(f"{root}/{f}"))
core = open(f"{root}/core/SNIPER.md").read().strip()
m = re.search(r"<!-- sniper:core:start -->\n(.*?)\n<!-- sniper:core:end -->", open(f"{root}/AGENTS.md").read(), re.S)
if not m or m.group(1).strip() != core:
    sys.exit("doctrine: AGENTS.md block differs from core/SNIPER.md")
v = [json.load(open(f"{root}/{f}"))["version"] for f in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json")]
if v[0] != v[1]:
    sys.exit(f"version mismatch: {v[0]} vs {v[1]}")
print(f"manifests, doctrine sync, version {v[0]}: ok")
EOF

if [ "$fail" -eq 0 ]; then echo "check: ok"; else echo "check: FAIL"; exit 1; fi
