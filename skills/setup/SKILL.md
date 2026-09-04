---
name: setup
description: Installs the sniper doctrine into the current project as local AGENTS.md and CLAUDE.md, so teammates and agents without the plugin follow the same rules and the project file takes precedence over global ones. Idempotent - re-run to refresh the doctrine block; existing content is never overwritten. Use when starting sniper in a repository or after a core update. Not for per-user settings or hooks.
argument-hint: "[project-dir]"
disable-model-invocation: true
---

1. Resolve the project directory: the argument, else the git top level of the current directory, else the current directory. Refuse a home directory or `/`.

2. Run `python3 ${CLAUDE_SKILL_DIR}/scripts/upsert-agents.py <project-dir> ${CLAUDE_SKILL_DIR}/../../core/SNIPER.md` (the script lives in `scripts/` beside this file; `core/SNIPER.md` is at the plugin root). It creates or refreshes only the block between `<!-- sniper:core:start -->` and `<!-- sniper:core:end -->` in `AGENTS.md`, and makes sure `CLAUDE.md` imports it with `@AGENTS.md`. Report the two status lines it prints.

3. When the script reports the fill marker present, replace it with the repository's own proof commands, three to six lines, one command each, taken from what the repository already declares: `package.json` scripts, `pyproject.toml`/`Makefile`/`justfile`, `nx`/`turbo` targets, the CI workflow. Prefer the exact CI commands. Do not invent commands and do not run them here. Leave the section alone when the marker is absent: the user owns it.

4. Print the result:

```
<project-dir>
AGENTS.md: created | block appended | block refreshed | unchanged
CLAUDE.md: created | import appended | unchanged
Working on this repo: <n> commands written | left as is
```

5. Say in one line how precedence works: Claude Code and Codex load the global instructions and the project files together, the project file is the more specific one, and with the block present the plugin's SessionStart hook injects nothing, so the doctrine costs its tokens once.

Stop when the two files are written and the result is printed. Do not edit any other file and do not commit.
