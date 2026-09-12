#!/bin/sh
# sniper install-devin: user-level install for Devin CLI/Desktop, for machines
# where `devin plugins install giulioleone097/sniper` is unavailable (the plugin
# manager needs `devin auth login`). Mirrors the plugin: skills land as
# ~/.config/devin/skills/sniper-<stage> with `sniper:` cross-refs rewritten to
# `sniper-`, agents land in ~/.config/devin/agents/ verbatim (their frontmatter
# already carries allowed-tools), the doctrine block goes into the global
# AGENTS.md, and the hooks merge into ~/.config/devin/config.json.
# Idempotent: re-run after pulling updates. Revert with --remove.
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEVIN_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/devin"

if [ "$1" = "--remove" ]; then
  for d in "$DEVIN_DIR"/skills/sniper-*/; do
    [ -d "$d" ] && rm -rf "$d"
  done
  rm -f "$DEVIN_DIR"/agents/sniper-*.md
  ROOT="$ROOT" DEVIN_DIR="$DEVIN_DIR" python3 - <<'PYEOF'
import json, os, re
devin = os.environ["DEVIN_DIR"]

agents = os.path.join(devin, "AGENTS.md")
if os.path.exists(agents):
    t = open(agents).read()
    t = re.sub(r"\n?# sniper\n\n<!-- sniper:core:start -->.*?<!-- sniper:core:end -->\n?", "\n", t, flags=re.S)
    if t.strip():
        open(agents, "w").write(t.rstrip() + "\n")
    else:
        os.remove(agents)

cfg_path = os.path.join(devin, "config.json")
if os.path.exists(cfg_path):
    cfg = json.load(open(cfg_path))
    hooks = cfg.get("hooks") or {}
    for ev, groups in list(hooks.items()):
        for g in groups:
            g["hooks"] = [h for h in g.get("hooks", [])
                if "scripts/core-context.sh" not in h.get("command", "")
                and "scripts/guard.sh" not in h.get("command", "")]
        hooks[ev] = [g for g in groups if g.get("hooks")]
        if not hooks[ev]:
            del hooks[ev]
    if hooks:
        cfg["hooks"] = hooks
    else:
        cfg.pop("hooks", None)
    open(cfg_path, "w").write(json.dumps(cfg, indent=2) + "\n")
PYEOF
  echo "sniper: removed from $DEVIN_DIR"
  exit 0
fi

mkdir -p "$DEVIN_DIR/skills" "$DEVIN_DIR/agents"

# skills: one dir per stage, prefixed sniper- so they never collide with other
# global skills; `sniper:` cross-references become `sniper-` and the display
# name follows the directory.
for d in "$ROOT"/skills/*/; do
  stage="$(basename "$d")"
  dest="$DEVIN_DIR/skills/sniper-$stage"
  rm -rf "$dest"
  cp -R "$d" "$dest"
  python3 - "$dest" "$stage" "$DEVIN_DIR" "$ROOT" <<'PYEOF'
import os, re, sys
dest, stage, devin, root = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
# only stage invocations (`sniper:<stage>`) become `sniper-<stage>`; markers
# like <!-- sniper:core:start --> or <!-- sniper:narrate --> must not move.
stages = "|".join(sorted(d for d in os.listdir(os.path.join(root, "skills"))
                         if os.path.isdir(os.path.join(root, "skills", d))))
for base, _, files in os.walk(dest):
    for f in files:
        if f.endswith((".md", ".py", ".yaml")):
            p = os.path.join(base, f)
            t = open(p).read()
            # cross-skill paths land on the installed prefixed dirs; every
            # other <plugin root> resolves to the live clone (scripts/, core/)
            t = re.sub(rf"<plugin root>/skills/({stages})/",
                       rf"{devin}/skills/sniper-\1/", t)
            t = t.replace("<plugin root>", root)
            t = re.sub(rf"sniper:({stages})\b", r"sniper-\1", t)
            if f == "SKILL.md":
                t = re.sub(rf"^name: {stage}$", f"name: sniper-{stage}", t, count=1, flags=re.M)
            open(p, "w").write(t)
PYEOF
done
# prune installed stages that no longer exist upstream
for d in "$DEVIN_DIR"/skills/sniper-*/; do
  [ -d "$d" ] || continue
  [ -d "$ROOT/skills/$(basename "$d" | sed 's/^sniper-//')" ] || rm -rf "$d"
done

# agents: copied with `model:` resolved through agents/models.json (sonnet/opus
# are not Devin model ids); the shared frontmatter already carries allowed-tools.
ROOT="$ROOT" DEVIN_DIR="$DEVIN_DIR" python3 - <<'PYEOF'
import glob, json, os, re
root, devin = os.environ["ROOT"], os.environ["DEVIN_DIR"]
models = json.load(open(os.path.join(root, "agents/models.json")))["hosts"]["devin"]["models"]
for src in glob.glob(os.path.join(root, "agents/sniper-*.md")):
    t = open(src).read()
    m = re.search(r"^model: (\w+)$", t, flags=re.M)
    if m and m.group(1) in models:
        t = t.replace(m.group(0), f'model: {models[m.group(1)]}', 1)
    open(os.path.join(devin, "agents", os.path.basename(src)), "w").write(t)
PYEOF

# doctrine + hooks: global AGENTS.md block (always-on) and config.json hooks
# (SessionStart self-heals if the block is removed; PreToolUse guards exec and
# write_to_process). Both merge without touching other entries.
ROOT="$ROOT" DEVIN_DIR="$DEVIN_DIR" python3 - <<'PYEOF'
import json, os, re
root, devin = os.environ["ROOT"], os.environ["DEVIN_DIR"]
core = open(os.path.join(root, "core/SNIPER.md")).read().strip()
block = f"<!-- sniper:core:start -->\n{core}\n<!-- sniper:core:end -->"

agents = os.path.join(devin, "AGENTS.md")
t = open(agents).read() if os.path.exists(agents) else ""
if "<!-- sniper:core:start -->" in t:
    t = re.sub(r"<!-- sniper:core:start -->.*?<!-- sniper:core:end -->", block, t, flags=re.S)
else:
    t = t.rstrip() + ("\n\n" if t.strip() else "") + "# sniper\n\n" + block + "\n"
open(agents, "w").write(t)

cfg_path = os.path.join(devin, "config.json")
cfg = json.load(open(cfg_path)) if os.path.exists(cfg_path) else {"version": 1}
hooks = cfg.setdefault("hooks", {})
ours = {
    "SessionStart": [{"hooks": [{"type": "command",
        "command": f'sh "{root}/scripts/core-context.sh"', "timeout": 5}]}],
    "PreToolUse": [{"matcher": "^(exec|Bash|Shell|write_to_process)$",
        "hooks": [{"type": "command",
        "command": f'sh "{root}/scripts/guard.sh"', "timeout": 5}]}],
}
for ev, groups in ours.items():
    existing = hooks.get(ev) or []
    for g in existing:
        g["hooks"] = [h for h in g.get("hooks", [])
            if "scripts/core-context.sh" not in h.get("command", "")
            and "scripts/guard.sh" not in h.get("command", "")]
    hooks[ev] = [g for g in existing if g.get("hooks")] + groups
open(cfg_path, "w").write(json.dumps(cfg, indent=2) + "\n")
PYEOF

n=$(ls -d "$DEVIN_DIR"/skills/sniper-*/ 2>/dev/null | wc -l | tr -d ' ')
echo "sniper: installed for Devin in $DEVIN_DIR ($n skills, 4 agents, doctrine, guard)"
echo "sniper: open a new Devin session; stages answer to /sniper-<stage>"
echo 'sniper: when `devin auth login` is done, `devin plugins install giulioleone097/sniper` replaces this'
