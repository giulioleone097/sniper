# sniper

One plugin for the whole development loop, for Claude Code and Codex. Lock the
outcome, take the shortest safe path, prove only changed behavior, stop. Twelve
skills carry setup through ship; three agents do the locating, the bounded
implementing, and the read-only reviewing.

## Install

### Claude Code

From a local checkout:

```
/plugin marketplace add /path/to/sniper
/plugin install sniper@sniper
```

From GitHub:

```
/plugin marketplace add giulioleone097/sniper
/plugin install sniper@sniper
```

### Codex

```
codex plugin marketplace add giulioleone097/sniper   # or the local checkout path
codex plugin add sniper@sniper
```

Then run `codex`, open `/hooks`, trust the three plugin hooks (SessionStart,
SubagentStart, PreToolUse), and start a new thread.

```
sh /path/to/sniper/scripts/install-codex-agents.sh
```

Generates `sniper_scout`, `sniper_worker`, `sniper_reviewer` as Codex custom
agents from `agents/*.md`. Restart Codex after running it.

### Checks

`sh scripts/check.sh` — the one-command acceptance run (validates, guard
fixtures, manifest JSON, doctrine sync, version parity).

## The flow

```
scope ──► plan? ──► build ──► simplify ──► review ──► prove ──► narrate ──► ship ──► learn?
  ▲                   │
  └──── debug ◄───────┘ (when a real failure appears)
```

`plan` only runs for 4+ steps or more than one owner; otherwise `scope` hands
straight to `build`. `simplify` runs on the changed code before `review`, so
review sees the lean diff. `learn` only runs when the fix's reasoning is not
already in code, tests, or docs. `flow` runs the whole pipeline hands-off and
stops before push/PR unless told otherwise.

## Skills

Invoke as `/sniper:<name>` in Claude Code, `$<name>` in Codex.

| skill | when | output |
|---|---|---|
| `setup` | first time in a repository, or after a core update | local `AGENTS.md` + `CLAUDE.md` carrying the doctrine block; the hook then injects nothing there |
| `scope` | before touching code, to lock the outcome | goal card (<= 10 lines) |
| `plan` | work has 4+ steps or more than one owner | chat brief or `docs/plans/<date>-<slug>.md` |
| `build` | implementing under a locked goal card | changed files + proof line |
| `debug` | a real failure needs a proven root cause | cause in one line + evidence + fix |
| `review` | after `simplify`, before shipping a diff | `path:line` findings, or `CLEAN` |
| `simplify` | on the changed code before `review` (or `--repo` audit) | shorter diff, or `Lean already.` |
| `prove` | acceptance needs the smallest decisive check | exact commands + `DONE` / `DONE_WITH_CONCERNS` / `BLOCKED` / `NEEDS_CONTEXT` |
| `narrate` | a PR body is needed, or a reviewer must approve without reading every file | approval dossier in the PR's language: verdict, what changes in plain words, a map of the change (lanes, unchanged neighbours, the one edge that matters), then a deep drill-down per affected domain or repository - why it was touched, what the change does, the before/after shape, every boundary crossed with the consumer that absorbs it, the decisions with their rejected alternative, executed evidence with base attribution, residual risk - plus what lies outside this verification and who covers it; no task is ever handed to the approver; commands and the engineer's reading guide fold into collapsible sections |
| `ship` | committing, pushing, or opening a PR | commit shas, PR url |
| `learn` | a non-obvious fix needs its reasoning captured | file path, or "nothing to record" |
| `flow` | running the whole pipeline hands-off | final report |

## Agents

- `sniper-scout` — sonnet, never edits files. Locates code; returns `path:line`
  references or `No match.`. Never suggests fixes.
- `sniper-worker` — sonnet by default (opus for genuinely complex slices).
  Implements one owned, disjoint slice under an explicit contract; reports
  changed files, proof, blockers, follow-ups.
- `sniper-reviewer` — opus, never edits files. Reviews one lens (`correctness`,
  `slop`, or `safety`) against a baseline diff; reports every finding with a
  confidence score, never fixes anything itself.

## Hooks

`hooks/hooks.json` is shared by Claude Code and Codex, both scripts POSIX
`sh` + `python3 -c` (no node, no jq):

- `SessionStart` and `SubagentStart` run `scripts/core-context.sh`, which
  injects `core/SNIPER.md` as `additionalContext` so the doctrine is active
  every turn and inside every subagent. `SubagentStart` has no matcher, so it
  injects into every subagent in the session, not only sniper's; add
  `"matcher": "sniper:.*"` to that entry in `hooks/hooks.json` to narrow it.
- `PreToolUse` on `Bash` runs `scripts/guard.sh`, which denies:
  - `--no-verify` as a token in a segment that also has `git`
  - `git push --force` / `-f` / a `+refspec` (e.g. `+main`), but not
    `--force-with-lease`
  - `git reset --hard`
  - `git checkout ... .` in any form (`checkout .`, `checkout -- .`,
    `checkout HEAD -- .`, `checkout -f .`)
  - `git restore ... .` in any form, unless it is staged-only
    (`--staged`/`-S` without `--worktree`/`-W`)
  - `git clean -f*` (any flag combination containing `f`)
  - `rm -rf` / `-fr` / `-r -f` targeting `/`, `~`, `$HOME`, `${HOME}`, `.`,
    `..`, or `*` (with or without a trailing `/` or `/*`)

  Everything else is allowed, including `rm -rf node_modules`,
  `rm -rf dist`, and `git push --force-with-lease`. Any parse or script error
  prints nothing and allows the command — the guard never traps the user.

To disable: `/plugin disable sniper`, or delete the entry in
`hooks/hooks.json`.

## Codex notes

- Skills: same files, invoked as `$name` instead of `/sniper:name`.
- Hooks: same `hooks/hooks.json`; trust it once in `/hooks` (see Install).
- Agents: not bundled — `scripts/install-codex-agents.sh` generates
  `sniper_scout`, `sniper_worker`, `sniper_reviewer` (hyphens become
  underscores) as `~/.codex/agents/*.toml`; `build`/`review` spawn them
  when installed, otherwise fall back to inline/sequential.
- No `disable-model-invocation` on Codex; each skill's sidecar
  `policy.allow_implicit_invocation` plays that role, `false` only on
  `flow`'s `agents/openai.yaml`.

Per project, run `/sniper:setup` (`$setup` on Codex): it writes the doctrine
block into the repository's `AGENTS.md` (created, or appended between
`<!-- sniper:core:start -->` / `<!-- sniper:core:end -->` markers, nothing else
touched) and makes `CLAUDE.md` import it with `@AGENTS.md` (or `.claude/CLAUDE.md`
when the project keeps it there). Claude Code and Codex load global and project
instructions together; the project file is the more specific one, and when the
block is present the `SessionStart` hook injects nothing, so the doctrine costs
its tokens once. Teammates without the plugin get the same rules from the file.
Re-run after a core update; the block is replaced, your sections stay.

## Sources

See [`docs/sources.md`](docs/sources.md) for what was taken from where, with
star counts and rejected alternatives.

## License

MIT — see [`LICENSE`](LICENSE).
