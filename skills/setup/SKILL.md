---
name: setup
description: Use when a project needs sniper's local rules. Writes the doctrine block into the project's AGENTS.md and makes CLAUDE.md import it, idempotently; own content is preserved and the session hook then injects nothing there. Not for editing the doctrine itself.
argument-hint: "[project-dir] [--no-map]"
disable-model-invocation: true
---

1. Resolve the project directory: the argument, else the git top level of the current directory, else the current directory. Refuse a home directory or `/`.

2. Run `python3 <this skill>/scripts/upsert-agents.py <project-dir> <plugin root>/core/SNIPER.md --map` (drop `--map` with `--no-map`), where `<this skill>` is the directory this file lives in and `<plugin root>` is the parent of its `skills/` directory: the script sits in `scripts/` beside this file, `core/SNIPER.md` at the plugin root. It creates or refreshes only the block between `<!-- sniper:core:start -->` and `<!-- sniper:core:end -->` in `AGENTS.md`, and makes sure `CLAUDE.md` imports it with `@AGENTS.md`. With `--map` it also adds one navigation line after the block pointing at `docs/sniper/map.md` and `conventions.md`, which step 4 creates. Report the status lines it prints.

3. When the script reports the fill marker present, replace it with the repository's own proof commands, three to six lines, one command each, taken from what the repository already declares: `package.json` scripts, `pyproject.toml`/`Makefile`/`justfile`, `nx`/`turbo` targets, the CI workflow. Prefer the exact CI commands. Do not invent commands and do not run them here. Leave the section alone when the marker is absent: the user owns it.

4. Unless `--no-map`: invoke the `map` skill on the project (`sniper:map` through the Skill tool, `$map` on Codex) so `docs/sniper/map.md` and `conventions.md` exist and carry a stamp; a map that is already current is left alone.

5. Print the result:

```
<project-dir>
AGENTS.md: created | block appended | block refreshed | unchanged
CLAUDE.md: created | import appended | unchanged
Working on this repo: <n> commands written | left as is
map: written | refreshed | current | skipped
```

6. Say in one line how precedence works: Claude Code and Codex load the global instructions and the project files together, the project file is the more specific one, and with the block present the plugin's SessionStart hook injects nothing, so the doctrine costs its tokens once.

Stop when the files are written and the result is printed. Do not edit any other file and do not commit.
