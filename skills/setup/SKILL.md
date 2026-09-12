---
name: setup
description: Use when the user asks to install or remove project rules, or discovery needs a missing or outdated map. Installs the doctrine only on explicit invocation; otherwise refreshes relevant map facts. Not for routine edits with known locations.
argument-hint: "[project-dir] [--map] [--refresh] [--prs N] [--linked] [--remove]"
---

1. Resolve the project directory: the argument, else the git top level of the current directory, else the current directory. Refuse a home directory or `/`.

2. `--map` means the model invoked this to refresh the map: skip to step 5 and touch nothing else. `--remove` means the user asked to take atlas back out: run `python3 <this skill>/scripts/upsert-agents.py <project-dir> --remove` — it deletes the doctrine block from `AGENTS.md` (the whole file when it is still the untouched skeleton) and the `CLAUDE.md` import, reports each status, and leaves `docs/atlas/` for manual deletion — then print the result block and stop. Without `--map` or `--remove` the user typed it: continue.

3. Run `python3 <this skill>/scripts/upsert-agents.py <project-dir> <plugin root>/core/ATLAS.md --map`, where `<this skill>` is the directory this file lives in and `<plugin root>` is the parent of its `skills/` directory. It creates or refreshes only the block between `<!-- atlas:core:start -->` and `<!-- atlas:core:end -->` in `AGENTS.md`, makes sure `CLAUDE.md` imports it with `@AGENTS.md` (or `.claude/CLAUDE.md` with `@../AGENTS.md` when the project keeps it there), and adds one navigation line after the block pointing at `docs/atlas/map.md` and `conventions.md`. Report the status lines it prints.

4. When the script reports the fill marker present, replace it with the repository's own proof commands, three to six lines, one command each, taken from what the repository already declares: `package.json` scripts, `pyproject.toml`, `Makefile`, `nx` or `turbo` targets, the CI workflow; `sh <plugin root>/scripts/checks.sh <project-dir>` names them. Prefer the exact CI commands, and when they run against disposable fixtures with no production access, say so in one line so the agent runs them and reruns affected ones without asking at each step. Do not invent commands and do not run them here. Leave the section alone when the marker is absent: the user owns it.

5. Map: read `references/map.md`; use a targeted refresh when changed facts affect this task. An older stamp alone does not require a full survey.

6. Print:

```
<project-dir>
AGENTS.md: created | block appended | block refreshed | unchanged | untouched (--map)
CLAUDE.md: created | import appended | unchanged | deleted | untouched (--map)
Working on this repo: <n> commands written | left as is
map: written | refreshed | current
```

7. Say in one line how precedence works: Claude Code and Codex load the global instructions and the project files together, the project file is the more specific one, and with the block present the plugin's SessionStart hook injects nothing, so the doctrine costs its tokens once.

Stop when the files are written and the result is printed. Do not edit any other file and do not commit.
