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
setup? ──► scope ──► build ──► review ──► ship
             │          │          │
       intake, grill  plan, debug  shrink, reviewers,
       goal card      prove        integrator
```

The loop runs itself: a request to change code goes through `scope`, `build`
and `review` without anyone typing a stage name, each stage invoking the next
through the host's skill tool. `ship` runs when you say ship, commit or PR, or
when the request said to carry the work through. `setup` installs the doctrine
in a project and builds its map; the map is refreshed by the model when its
stamp falls behind. Type a stage name only to run one alone or with flags.

## Skills

| stage | use when | what it does |
|---|---|---|
| `setup` | a project needs sniper's local rules, or its map is missing or stale | doctrine block in AGENTS.md, CLAUDE.md import, map pointer (only when you typed it); `docs/sniper/map.md` and `conventions.md` from git, the tracker and the reviewers' comments, with a stamp; `--map` refreshes only |
| `scope` | work arrives: a task, an issue, a PR, a report, an idea | intake for a tracker item (read, reproduce the claim, check already-done and already-rejected), grill for an undecided design (rounds through the host's question tool), then the goal card: outcome, acceptance, exclusions, risk, proof, size; hands to build |
| `build` | a card exists and code must change, or a failure has no known cause | plan when complex (`--tickets` publishes), debug when the cause is unknown, mode references for fix, refactor, migrate and UI, one runnable check where none exists, proof from the repository's own commands; hands to review |
| `review` | a change is built, or a branch, PR or tree needs review | shrink first (reuse, stdlib, native, delete, yagni, shrink, with the platform lookup and `ceiling:` on kept limits), one reviewer per area or lens, the integrator verifies, sweeps consumers in and out of the repository and runs the checks with failures attributed to the baseline; `--fix`, `--pr`, `--repo`, `--debt` |
| `ship` | you say ship, commit, PR, dossier, handoff, or asked up front to carry it through | atomic Conventional Commits, tracker item linked, `--pr` with the approval dossier as body, `--dossier` alone, one durable lesson (`--learn`, `--from-pr <n>`), `--handoff` when stopping early; push only with `--push` |

Every stage keeps its branches in `references/`: the root file is a router, read in full, and a branch is read only when its case applies.

## Agents

- `sniper-scout` — sonnet, never edits files. Locates code; returns `path:line`
  references or `No match.`. Never suggests fixes.
- `sniper-worker` — sonnet by default (opus for genuinely complex slices).
  Implements one owned, disjoint slice under an explicit contract; reports
  changed files, proof, blockers, follow-ups.
- `sniper-reviewer` — opus, never edits files. Reviews one lens (`correctness`,
  `slop`, or `safety`) against a baseline diff; reports every finding with a
  confidence score, never fixes anything itself.
- `sniper-integrator` — opus, never edits files. Merges the per-area reports of a
  `review` pass into one verified list, settles contradictions by
  reading the code, catches what crosses areas, and runs the nearest checks with
  every failure attributed to the baseline before it is called new.

## Scripts

Four detectors make the skills run the repository's own commands instead of guessing. Each reads the tree, prints key=value lines, and never changes anything; every skill that needs one names it.

| Script | Answers | Used by |
|---|---|---|
| `scripts/checks.sh <path>` | the project's own typecheck, lint, test and build commands for that path (nx targets, package scripts, pyproject, .NET, cargo, go, make), or `none=1` | `build` (prove), `review`, the integrator |
| `scripts/tracker.sh [repo]` | the forge, the CLI and whether it is logged in, from the origin remote alone (GitHub/gh, GitLab/glab, Azure DevOps/az, else files under `docs/tickets/`) | `scope` (intake), `build` (plan), `ship` |
| `scripts/tokens.sh <ui path>` | the design tokens the repository already defines, with counts: custom properties, colours, fonts, sizes, theme keys | `build` on UI work, the reviewer's `taste:` tag |
| `scripts/consumers.sh [repo]` | what depends on this repository outside its tree: the names it publishes (package, module, crate, assembly, remote) and every sibling checkout or workspace member whose manifest names one of them | `review`, `ship` (dossier), the integrator's cross-repo sweep |
| `scripts/repo-facts.sh [repo] [months] [prs]` | the facts a map starts from, read-only: layout, languages, hot spots, authors, commit conventions, checks, instruction files, and through `gh` the merged-PR cadence, reviewers and inline commenters (bots kept apart) | `setup` (map) |
| `scripts/debt.sh [repo]` | the ledger of declared shortcuts: every `ceiling:` comment with its limit and upgrade trigger, `no-trigger` on the ones that will rot | `review --debt`, `setup` (map) |
| `scripts/pr-partition.py BASE HEAD` | the diff split into judgment, tests, mechanical, generated, docs and config, so only judgment code is read | `review`, `ship` (dossier) |

`scripts/check.sh` is the plugin's own acceptance: four strict validations, the guard fixtures, manifest parity, doctrine sync, and the repository rules executed (skill bodies under 120 lines, references under 80, no host env var inside a skill, every script parses, both detectors answer on this repo).

## Hooks

`hooks/hooks.json` is shared by Claude Code and Codex, both scripts POSIX
`sh` + `python3 -c` (no node, no jq):

- `SessionStart` and `SubagentStart` run `scripts/core-context.sh`, which
  injects `core/SNIPER.md` as `additionalContext` so the doctrine is active
  every turn and inside every subagent. `SubagentStart` has no matcher, so it
  injects into every subagent in the session, not only sniper's; set
  `SNIPER_SUBAGENT_MATCHER=<regex>` (unanchored, case-insensitive, for
  example `^sniper`) to narrow it to the agent types that match.
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
  `sniper_scout`, `sniper_worker`, `sniper_reviewer`, `sniper_integrator`
  (hyphens become underscores) as `~/.codex/agents/*.toml`; `build`,
  `review`, `ship` and `setup` spawn them when installed, otherwise fall
  back to inline/sequential.
- No `disable-model-invocation` anywhere: every stage is model-invocable so
  the loop can chain; `setup` guards its doctrine write with the `--map`
  argument the model passes when it only refreshes the map.

Per project, run `/sniper:setup` (`$setup` on Codex): it writes the doctrine
block into the repository's `AGENTS.md` (created, or appended between
`<!-- sniper:core:start -->` / `<!-- sniper:core:end -->` markers, nothing else
touched) and makes `CLAUDE.md` import it with `@AGENTS.md` (or `.claude/CLAUDE.md`
when the project keeps it there). Claude Code and Codex load global and project
instructions together; the project file is the more specific one, and when the
block is present the `SessionStart` hook injects nothing, so the doctrine costs
its tokens once. Teammates without the plugin get the same rules from the file.
Re-run after a core update; the block is replaced, your sections stay.

- Codex substitutes `${CLAUDE_PLUGIN_ROOT}` in `hooks/hooks.json` only. Inside a skill body neither host expands a variable, and Codex presents skills to the model as absolute skill roots, so every path in a skill is written relative to the file that names it (`<this skill>/scripts/…`, `<plugin root>/scripts/…`); `scripts/check.sh` fails on any `CLAUDE_SKILL_DIR` or `${CLAUDE_PLUGIN_ROOT}` inside a skill or agent.

## Evals

`evals/` measures the plugin the only way that counts: a real headless session per cell, bare, with and without sniper, scored on the files it leaves behind by deterministic scorers that prove themselves on good and bad references first (`python3 evals/run.py --selftest`, also run by `scripts/check.sh`). Three probes to start: path traversal, per-client rate limiting, and a bug report that names one caller while the canonical cause sits in the shared function. See `evals/README.md`.

## Sources

See [`docs/sources.md`](docs/sources.md) for what was taken from where, with
star counts and rejected alternatives.

## License

MIT — see [`LICENSE`](LICENSE).
