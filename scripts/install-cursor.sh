#!/bin/sh
# atlas install-cursor: user-level install for Cursor, for machines where the
# plugin is not installed from Customize -> Plugins. Mirrors the plugin: skills
# land as ~/.cursor/skills/atlas-<stage> with `atlas:` cross-refs rewritten
# to `atlas-`, agents land in ~/.cursor/agents/ with `model:` reset to
# `inherit` (the tier names are not Cursor model ids), and the hooks merge into
# ~/.cursor/hooks.json (sessionStart injects the doctrine,
# beforeShellExecution guards shell commands).
# Idempotent: re-run after pulling updates. Revert with --remove.
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CURSOR_DIR="$HOME/.cursor"

if [ "$1" = "--remove" ]; then
  # sniper-* dirs/agents: left by the pre-rename installer; --remove reverts those too
  for d in "$CURSOR_DIR"/skills/atlas-*/ "$CURSOR_DIR"/skills/sniper-*/; do
    [ -d "$d" ] && rm -rf "$d"
  done
  rm -f "$CURSOR_DIR"/agents/atlas-*.md "$CURSOR_DIR"/agents/sniper-*.md
  ROOT="$ROOT" CURSOR_DIR="$CURSOR_DIR" python3 - <<'PYEOF'
import json, os
cfg_path = os.path.join(os.environ["CURSOR_DIR"], "hooks.json")
if os.path.exists(cfg_path):
    cfg = json.load(open(cfg_path))
    hooks = cfg.get("hooks") or {}
    for ev, entries in list(hooks.items()):
        hooks[ev] = [h for h in entries
            if "scripts/core-context.sh" not in h.get("command", "")
            and "scripts/guard.sh" not in h.get("command", "")]
        if not hooks[ev]:
            del hooks[ev]
    cfg["hooks"] = hooks
    open(cfg_path, "w").write(json.dumps(cfg, indent=2) + "\n")
PYEOF
  echo "atlas: removed from $CURSOR_DIR"
  exit 0
fi

mkdir -p "$CURSOR_DIR/skills" "$CURSOR_DIR/agents"

for d in "$ROOT"/skills/*/; do
  stage="$(basename "$d")"
  dest="$CURSOR_DIR/skills/atlas-$stage"
  rm -rf "$dest"
  cp -R "$d" "$dest"
  python3 - "$dest" "$stage" "$CURSOR_DIR" "$ROOT" <<'PYEOF'
import os, re, sys
dest, stage, cursor, root = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
# only stage invocations (`atlas:<stage>`) become `atlas-<stage>`; markers
# like <!-- atlas:core:start --> or <!-- atlas:narrate --> must not move.
stages = "|".join(sorted(d for d in os.listdir(os.path.join(root, "skills"))
                         if os.path.isdir(os.path.join(root, "skills", d))))
for base, _, files in os.walk(dest):
    for f in files:
        if f.endswith((".md", ".py", ".yaml")):
            p = os.path.join(base, f)
            t = open(p).read()
            t = re.sub(rf"<plugin root>/skills/({stages})/",
                       rf"{cursor}/skills/atlas-\1/", t)
            t = t.replace("<plugin root>", root)
            t = re.sub(rf"atlas:({stages})\b", r"atlas-\1", t)
            if f == "SKILL.md":
                t = re.sub(rf"^name: {stage}$", f"name: atlas-{stage}", t, count=1, flags=re.M)
            open(p, "w").write(t)
PYEOF
done
for d in "$CURSOR_DIR"/skills/atlas-*/; do
  [ -d "$d" ] || continue
  [ -d "$ROOT/skills/$(basename "$d" | sed 's/^atlas-//')" ] || rm -rf "$d"
done

for f in "$ROOT"/agents/atlas-*.md; do
  python3 - "$f" "$CURSOR_DIR/agents/$(basename "$f")" "$ROOT/agents/models.json" <<'PYEOF'
import json, re, sys
src, dst, reg = sys.argv[1], sys.argv[2], sys.argv[3]
models = json.load(open(reg))["hosts"]["cursor"]["models"]
t = open(src).read()
t = re.sub(r"^model: (\w+)$", lambda m: f'model: {models.get(m.group(1), "inherit")}', t, count=1, flags=re.M)
open(dst, "w").write(t)
PYEOF
done

ROOT="$ROOT" CURSOR_DIR="$CURSOR_DIR" python3 - <<'PYEOF'
import json, os
root, cursor = os.environ["ROOT"], os.environ["CURSOR_DIR"]
cfg_path = os.path.join(cursor, "hooks.json")
cfg = json.load(open(cfg_path)) if os.path.exists(cfg_path) else {"version": 1}
cfg.setdefault("version", 1)
hooks = cfg.setdefault("hooks", {})
ours = {
    "sessionStart": [{"command": f'sh "{root}/scripts/core-context.sh"', "timeout": 5}],
    "beforeShellExecution": [{"command": f'sh "{root}/scripts/guard.sh"', "timeout": 5}],
}
for ev, entries in ours.items():
    existing = [h for h in hooks.get(ev, [])
        if "scripts/core-context.sh" not in h.get("command", "")
        and "scripts/guard.sh" not in h.get("command", "")]
    hooks[ev] = existing + entries
open(cfg_path, "w").write(json.dumps(cfg, indent=2) + "\n")
PYEOF

n=$(ls -d "$CURSOR_DIR"/skills/atlas-*/ 2>/dev/null | wc -l | tr -d ' ')
echo "atlas: installed for Cursor in $CURSOR_DIR ($n skills, 4 agents, doctrine hook, guard)"
echo "atlas: open a new Cursor agent session; stages answer to /atlas-<stage>"
