---
name: setup
description: Use when a project needs sniper's local rules, or when docs/sniper/map.md is missing or its stamp is behind HEAD. Installs the doctrine block and the map pointer only on the user's own invocation; builds or refreshes the repository map either way. Not for reviewing a change.
argument-hint: "[project-dir] [--map] [--refresh] [--prs N] [--linked]"
---

1. Resolve the project directory: the argument, else the git top level of the current directory, else the current directory. Refuse a home directory or `/`.

2. `--map` means the model invoked this to refresh the map: skip to step 5 and touch nothing else. Without `--map` the user typed it: continue.

3. Run `python3 <this skill>/scripts/upsert-agents.py <project-dir> <plugin root>/core/SNIPER.md --map`, where `<this skill>` is the directory this file lives in and `<plugin root>` is the parent of its `skills/` directory. It creates or refreshes only the block between `<!-- sniper:core:start -->` and `<!-- sniper:core:end -->` in `AGENTS.md`, makes sure `CLAUDE.md` imports it with `@AGENTS.md` (or `.claude/CLAUDE.md` with `@../AGENTS.md` when the project keeps it there), and adds one navigation line after the block pointing at `docs/sniper/map.md` and `conventions.md`. Report the status lines it prints.

4. When the script reports the fill marker present, replace it with the repository's own proof commands, three to six lines, one command each, taken from what the repository already declares: `package.json` scripts, `pyproject.toml`, `Makefile`, `nx` or `turbo` targets, the CI workflow; `sh <plugin root>/scripts/checks.sh <project-dir>` names them. Prefer the exact CI commands, and when they run against disposable fixtures with no production access, say so in one line so the agent runs them and reruns affected ones without asking at each step. Do not invent commands and do not run them here. Leave the section alone when the marker is absent: the user owns it.

5. Map: read `references/map.md` and follow it; a map whose stamp is current is left alone, otherwise only what moved since the stamp is read.

6. Print:

```
<project-dir>
AGENTS.md: created | block appended | block refreshed | unchanged | untouched (--map)
CLAUDE.md: created | import appended | unchanged | untouched (--map)
Working on this repo: <n> commands written | left as is
map: written | refreshed | current
```

7. Say in one line how precedence works: Claude Code and Codex load the global instructions and the project files together, the project file is the more specific one, and with the block present the plugin's SessionStart hook injects nothing, so the doctrine costs its tokens once.

Stop when the files are written and the result is printed. Do not edit any other file and do not commit.
