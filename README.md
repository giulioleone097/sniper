# sniper

One plugin for the whole development loop, for Claude Code, Codex, Devin and
Cursor. Lock the
outcome, take the shortest safe path, prove only changed behavior, stop. Five
stages carry setup through ship, eight entry points are typed by name (grill,
simplify, handoff, optimize, research, questionnaire, wayfinder, prototype);
four agents cover locating, bounded implementation, review, and integration.

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

Generates `sniper_scout`, `sniper_worker`, `sniper_reviewer`, and
`sniper_integrator` as Codex custom
agents from `agents/*.md`. Restart Codex after running it.

### Devin

```
devin plugins install giulioleone097/sniper   # or the local checkout path
```

Skills answer to `/sniper:<stage>`; the doctrine rides the plugin's always-on
`AGENTS.md` and the guard runs on `PreToolUse` via the root `hooks.json`. Where
the plugin manager is unavailable (`devin auth login` required), install at
user level instead:

```
sh /path/to/sniper/scripts/install-devin.sh     # --remove reverts
```

### Cursor

Install from **Customize → Plugins** pointing at `giulioleone097/sniper` (or a
local checkout). The `.cursor-plugin/plugin.json` manifest wires skills,
`rules/sniper-core.mdc` (the doctrine, `alwaysApply`), agents and
`hooks/cursor-hooks.json` (`beforeShellExecution` → the guard). At user level:

```
sh /path/to/sniper/scripts/install-cursor.sh    # --remove reverts
```

### Checks

`sh scripts/check.sh` — the one-command acceptance run (validates, guard
fixtures, manifest JSON, doctrine sync, four-manifest version parity, per-host
hook event rules).

## The flow

```
grill ─┐
setup? ──► scope ──► build ──► review ──► ship
             │          │          │
       intake, grill  plan, debug  shrink, reviewers,
       goal card      prove        integrator
                              simplify (shrink alone)

optimize ──► review           rounds of hypotheses toward a target
handoff  ──► scope <file>     stop early now, resume in the next session
```

The loop chooses its path: a small understood change uses direct implement,
review, fix and prove; broader or uncertain work goes through `scope`, `build`
and `review`, with each stage invoking the next through the host's skill tool.
`ship` runs when you say ship, commit or PR, or when the request said to carry
the work through. `setup` installs the doctrine in a project and builds its
map; the map is refreshed by the model when its stamp is behind facts needed for
the task. Type a
stage name only to run one alone or with flags.
`grill`, `simplify`, `handoff` and `optimize` are entry points you type by name:
an idea interrogated before any card exists, a shrink pass on code nobody asked
to review, a session written down for the next one (which resumes it through
`scope <file>`), and a measured number pushed toward a target by rounds of
parallel hypotheses that keep only what beats the baseline.

## Skills

| skill | use when | what it does |
|---|---|---|
| `setup` | a project needs sniper's local rules, or its map is missing or stale | doctrine block in AGENTS.md, CLAUDE.md import, map pointer (only when you typed it); `docs/sniper/map.md` and `conventions.md` from git, the tracker and the reviewers' comments, with a stamp; `--map` refreshes only |
| `scope` | work arrives: a task, an issue, a PR, a report, a screenshot, a handoff or grill file, an idea | intake for a tracker item, an image or a resume file (forge and CLI from `tracker.sh`, read, reproduce the claim, check already-done and already-rejected, reuse what a handoff proved and honour what it decided; `--reply` posts the result or the questions back on the item after your confirmation), grill for an undecided design, reach of a touched contract measured (`git grep`, `consumers.sh`) or reused from the grill file before Risk and Size, then the goal card with its Source line (forge#n, PR, path, pasted, or `request`); typed with no argument and no request in the conversation it offers to resume the latest handoff; hands to build |
| `build` | a card exists and code must change, or a failure has no known cause | an issue, URL, image, handoff or grill file goes back through `scope` first; plan when complex (a brief in chat, a file under `docs/plans/` for four or more tasks, several owners or a risk surface; `--tickets` publishes), debug when the cause is unknown, mode references for fix, refactor and migrate, UI taste when a visual decision is made, parallel workers in their own worktrees (seeded with your uncommitted work, integrated back as a diff) when their builds or tests would collide, indispensable tests only, run red before green in a detached worktree of `HEAD` when the code already exists, the card's proof command run as written, else proof from the repository's own commands and a real picture for a UI change; hands to review unless `--no-review`, which skips only that handoff |
| `review` | a change is built, or a branch, PR or tree needs review, or reviewers left comments | the task's diff, or on a clean branch the diff against the default branch; shrink within scope (the slop catalog names what to cut and what stays), economical reviewers only when useful, verify reports and fix real in-scope defects by default, sweep consumers in and out of the repository when external contracts change, checks with failures attributed to the baseline; `--pr` posts one thread per finding at its line in the branch's PR (drafted to a file when there is no PR, CLI or login), `--address <pr>` checks out the PR's head when the tree is clean and answers the reviewers' threads from the code (fixed, landing through `ship --push`; rebutted with evidence; or follow-up); `--fix`, `--read-only` (cuts and fixes as proposals, nothing applied), `--repo`, `--debt` |
| `grill` | you say grill me, or bring an idea, plan, file, issue or PR still undecided | typed bare, asks what to grill; reads a document or item first and grills only what it leaves open; the decision tree worked in rounds through the host's question tool, facts looked up itself, every option costed by its reach at HEAD (domains from the map, consumers counted, linked repositories, a code-graph impact query when exposed), the recommendation first on every question; the settled tree carries reach and risk per decision and one map when more than one domain is reached; ends by asking build now, card only or stop; card only, stop and `--out` write the settled tree to disk so `scope <file>` resumes it |
| `simplify` | you ask to simplify, shrink or de-slop code outside a review, or `--repo` / `--debt` | the files named, else the diff since the baseline or merge-base plus staged, unstaged and new files; the six rungs (reuse, stdlib, native, delete, yagni, shrink) per area, `slop` reviewers proposing when there are several, then the nearest check or the integrator proving nothing moved; never runs review |
| `handoff` | you say hand off, stop here, pick this up later, or a session stops before the work is done | where the work stands (branch, tree, workers' worktrees), proven lines with their command and result, open items as work, decisions only the conversation carries, artifacts pointed at rather than copied, the skill the next session calls first; written to `--out <file>` or `docs/handoff-<date>-<slug>.md`, `scope <file>` resumes it and `ship` deletes it once the work is committed |
| `optimize` | you ask to speed up, shrink or push a measured number toward a target | one `--metric` command that starts what it measures from the checkout, `--paths` for what may change (asked for when neither flag nor request names them); the baseline measured in a detached worktree of `HEAD` that stays as the champion tree, re-measured every round; rounds of distinct hypotheses (one family each) in parallel `git worktree`s, each measured three times; a candidate is kept only when it beats the baseline beyond the noise band, passes the regression check and narrows nothing the metric measures; families named from a profile of the metric when the stack has a profiler, `--guard <command> <max>` metrics that must stay under a maximum (memory, size, p99), runs raised from three to five or seven when the noise band is too wide for the target; stops at the target, after two dry rounds of new families, or at the budget, and a stopped run's `optimize/<slug>` branch blocks the next until landed or deleted; every run ends with `kpi:` lines (baseline to final, rounds, hypotheses, kept, wall time, regression) in the ledger and the report; the kept diff goes to `review`, and a review edit is re-measured |
| `research` | a question needs an answer grounded in primary sources before work continues | a background subagent investigates the question against primary sources and writes one cited Markdown file; never edits code |
| `questionnaire` | a decision is blocked on another person's knowledge, not on more digging | the open questions become `docs/questionnaire-<slug>.md`, one document handed to the person who holds the answers |
| `wayfinder` | a multi-session effort needs a map of the decisions still open | `docs/wayfinder-<date>-<slug>.md`, a map of decision nodes resolved one at a time through `grill` |
| `prototype` | a design question needs a throwaway UI to answer it, not production code | HTML/UI variants built to answer the question, compared, then discarded; never committed |
| `ship` | you say ship, commit, PR, dossier, or asked up front to carry it through | atomic Conventional Commits (scope only when recent commits carry one), tracker item linked, `--pr` with the approval dossier as body (minimal: verdict, one map, one diagram per domain, real e2e screenshots or videos attached where the forge hosts them, in the repository's language or `--lang`; on the default branch a `<type>/<slug>` branch is created first, an open PR is reused, on Azure DevOps the drill-down goes as closed threads), `--dossier [pr]` alone on GitHub, GitLab or Azure DevOps (`--post` replaces the body, `--walkthrough` GitHub only), commit language from the repository's recent commits, CI awaited after `--pr` with failures attributed to base or new, one durable lesson (`--learn`, `--from-pr <n>`; `proposed (not written)` on a hands-off run), the handoff or grill file the work resumed from deleted; the block ends with `proof:`, `learned:` and `left:` naming what was kept out; push only with `--push` |

Every stage keeps its branches in `references/`: the root file is a router, read in full, and a branch is read only when its case applies.

## Agents

- `sniper-scout` — sonnet, or `gpt-5.6-luna` on Codex, never edits files.
  Locates code; returns `path:line` references or `No match.`. Never suggests
  fixes.
- `sniper-worker` — sonnet by default (opus for complex slices), or
  `gpt-5.6-luna` / `gpt-5.6-terra` on Codex. Implements one owned, disjoint
  slice under an explicit contract; reports changed files, proof, blockers,
  follow-ups.
- `sniper-reviewer` — opus, or `gpt-5.6-terra` on Codex, never edits files.
  Reviews one lens (`correctness`, `slop`, `safety`, or `all`) against a baseline diff;
  reports every finding with a confidence score, never fixes anything itself.
- `sniper-integrator` — opus, or `gpt-5.6-terra` on Codex, never edits files.
  Merges reports when several areas need integration, settles contradictions by
  reading the code, catches cross-area defects, and runs the nearest checks with
  every failure attributed to the baseline before it is called new. There is no
  minimum reviewer team; Astra/Fable coordinate scope, decisions, and integration.

## Scripts

Four detectors make the skills run the repository's own commands instead of guessing. Each reads the tree, prints key=value lines, and never changes anything; every skill that needs one names it.

| Script | Answers | Used by |
|---|---|---|
| `scripts/checks.sh <path>` | the project's own typecheck, lint, test, build and e2e commands for that path or file (nx targets, package scripts, Playwright and Cypress configs, pyproject, .NET, cargo, go, make), or `none=1` | `build` (prove), `review`, `optimize`, `ship` (evidence), the integrator |
| `scripts/tracker.sh [repo]` | the forge, the CLI and whether it is logged in, from the origin remote (GitHub/gh, GitLab/glab, Azure DevOps/az; any other host is probed through gh then glab, so an enterprise GitHub or self-hosted GitLab the CLI is logged into is found; else files under `docs/tickets/`) | `scope` (intake), `build` (plan), `ship` |
| `scripts/tokens.sh <ui path>` | the design tokens the repository already defines, with counts: custom properties, colours, fonts, sizes, theme keys | `build` on UI work, the reviewer's `taste:` tag |
| `scripts/consumers.sh [repo]` | what depends on this repository outside its tree: the names it publishes (package, module, crate, assembly, remote) and every sibling checkout or workspace member whose manifest names one of them | `review`, `ship` (dossier), the integrator's cross-repo sweep |
| `scripts/repo-facts.sh [repo] [months] [prs]` | the facts a map starts from, read-only: layout, languages, hot spots, authors, commit conventions, checks, instruction files, and through `gh` the merged-PR cadence, reviewers and inline commenters (bots kept apart) | `setup` (map) |
| `scripts/debt.sh [repo]` | the ledger of declared shortcuts: every `ceiling:` comment with its limit and upgrade trigger, `no-trigger` on the ones that will rot | `review --debt`, `setup` (map) |
| `scripts/pr-partition.py BASE HEAD` | the diff split into judgment, tests, mechanical, generated, docs and config, so only judgment code is read | `review`, `ship` (dossier) |

`scripts/check.sh` is the plugin's own acceptance: four strict validations, the guard fixtures, manifest parity, doctrine sync, per-host hook event rules, and the repository rules executed (skill bodies under 120 lines, references under 80, no host env var inside a skill, every script parses, both detectors answer on this repo).

## Hooks

One hooks file per host family — the events and the output shape differ, so
they do not share a file. All scripts are POSIX `sh` + `python3 -c` (no node,
no jq):

- `hooks/hooks.json` — Claude Code and Codex. `SessionStart` and
  `SubagentStart` run `scripts/core-context.sh`, which injects
  `core/SNIPER.md` as `additionalContext` so the doctrine is active
  every turn and inside every subagent. `SubagentStart` has no matcher, so it
  injects into every subagent in the session, not only sniper's; set
  `SNIPER_SUBAGENT_MATCHER=<regex>` (unanchored, case-insensitive, for
  example `^sniper`) to narrow it to the agent types that match.
  `PreToolUse` on `Bash` runs `scripts/guard.sh`.
- `hooks.json` (plugin root) — Devin. `PreToolUse` on `exec` /
  `write_to_process` runs the guard; the doctrine rides the plugin's always-on
  `AGENTS.md` rule instead of a session hook.
- `hooks/cursor-hooks.json` — Cursor. `beforeShellExecution` runs the guard;
  the doctrine rides `rules/sniper-core.mdc` (`alwaysApply`).

The guard and the context script answer every host with one payload — each
host reads the fields it knows (`permissionDecision` for Claude/Codex,
`decision`/`reason` for Devin, `permission`/`user_message` and
`additional_context` for Cursor) — and both read the command from whichever
field the host sends (`tool_input.command`, `text_input`/`bytes_input`, or
top-level `command`). The guard denies:
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

To disable: `/plugin disable sniper` (Claude), `codex plugin remove sniper`
(Codex), `devin plugins remove sniper` (Devin), or remove the host's entry in
its hooks file.

## Codex notes

- Skills: same files, invoked as `$name` instead of `/sniper:name`.
- Hooks: same `hooks/hooks.json`; trust it once in `/hooks` (see Install).
- Agents: not bundled — `scripts/install-codex-agents.sh` generates
  `sniper_scout`, `sniper_worker`, `sniper_reviewer`, `sniper_integrator`
  (hyphens become underscores) as `~/.codex/agents/*.toml`; `build`,
  `review`, `optimize`, `ship` and `setup` spawn them when installed,
  otherwise fall back to inline/sequential.
- No `disable-model-invocation` anywhere: every stage is model-invocable so
  the loop can chain; `setup` guards its doctrine write with the `--map`
  argument the model passes when it only refreshes the map.

Per project, run `/sniper:setup` (`$setup` on Codex): it writes the doctrine
block into the repository's `AGENTS.md` (created, or appended between
`<!-- sniper:core:start -->` / `<!-- sniper:core:end -->` markers, nothing else
touched) and makes `CLAUDE.md` import it with `@AGENTS.md` (or `.claude/CLAUDE.md`
when the project keeps it there). Claude Code and Codex load global and project
instructions together; the project file is the more specific one, and when the
block is present the hook injects nothing at either event, so the doctrine costs
its tokens once. Teammates without the plugin get the same rules from the file.
Re-run after a core update; the block is replaced, your sections stay.

- Codex substitutes `${CLAUDE_PLUGIN_ROOT}` in `hooks/hooks.json` only. Inside a skill body neither host expands a variable, and Codex presents skills to the model as absolute skill roots, so every path in a skill is written relative to the file that names it (`<this skill>/scripts/…`, `<plugin root>/scripts/…`); `scripts/check.sh` fails on any `CLAUDE_SKILL_DIR` or `${CLAUDE_PLUGIN_ROOT}` inside a skill or agent.

## Devin and Cursor notes

- Devin reads the plugin's `AGENTS.md` as an always-on rule (the doctrine),
  `agents/*.md` as custom subagents (it uses the `allowed-tools` field, and
  `sniper:`-prefixed profile names), and the root `hooks.json` — its only
  plugin hooks convention. There is no `SubagentStart` on Devin, so subagents
  there rely on their own prompts.
- Cursor reads `.cursor-plugin/plugin.json`; `rules/sniper-core.mdc` carries
  the doctrine with `alwaysApply` (its body must stay identical to
  `core/SNIPER.md` — `check.sh` verifies). Agent frontmatter `readonly: true`
  keeps scout/reviewer/integrator read-only; `model:` pins are
  Claude/Devin names — on Cursor the installers rewrite them to `inherit`,
  and the plugin bundle leaves them for the model picker to resolve.
- Both installers (`install-devin.sh`, `install-cursor.sh`) exist because the
  plugin managers are not always reachable; they copy skills as `sniper-<stage>`
  (rewriting `sniper:` references to `sniper-`), merge hook entries without
  touching others, and are idempotent and reversible (`--remove`).

## Evals

`evals/` measures the plugin with real headless sessions per cell, bare, using
baseline, current, and optional previous-plugin arms, scored on the files left
behind by deterministic scorers that prove themselves on good and bad
references first (`python3 evals/run.py --selftest`, also run by
`scripts/check.sh`). Five probes cover path safety, canonical root causes,
per-client limits, bounded fixes, and meaningful domain/I/O boundaries. See
`evals/README.md`; missing or partial live metrics remain explicitly unavailable.

## Sources

See [`docs/sources.md`](docs/sources.md) for what was taken from where, with
star counts and rejected alternatives.

## License

MIT — see [`LICENSE`](LICENSE).
