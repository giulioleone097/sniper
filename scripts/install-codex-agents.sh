#!/bin/sh
# sniper: install the three agents as Codex custom agents.
# Codex plugins cannot bundle agents, so this generates ~/.codex/agents/<name>.toml
# from agents/*.md: Claude Code and Codex share one agent definition.
# Re-run after editing an agent. Any error: exit 1 with the reason.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${CODEX_HOME:-$HOME/.codex}/agents"
mkdir -p "$DEST" || exit 1

exec python3 - "$ROOT/agents" "$DEST" <<'EOF'
import glob, os, re, sys

src, dest = sys.argv[1], sys.argv[2]
effort = {"opus": "high", "sonnet": "medium", "haiku": "low"}

for path in sorted(glob.glob(os.path.join(src, "*.md"))):
    text = open(path).read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        sys.exit(f"{path}: missing frontmatter")
    fm = dict(re.findall(r"^([\w-]+):\s*(.*)$", m.group(1), re.M))
    body = m.group(2).strip()
    if "'''" in body:
        sys.exit(f"{path}: body contains ''' which TOML literal strings cannot hold")
    name = fm["name"].replace("-", "_")
    tools = fm.get("tools", "")
    lines = [
        f'name = "{name}"',
        'description = "' + fm["description"].replace('"', '\\"') + '"',
    ]
    if fm.get("model") in effort:
        lines.append(f'model_reasoning_effort = "{effort[fm["model"]]}"')
    if tools and not re.search(r"\b(Edit|Write)\b", tools):
        lines.append('sandbox_mode = "read-only"')
    lines.append("developer_instructions = '''\n" + body + "\n'''")
    out = os.path.join(dest, name + ".toml")
    open(out, "w").write("\n".join(lines) + "\n")
    print(out)
print("restart Codex to load them; spawn with the names above")
EOF
