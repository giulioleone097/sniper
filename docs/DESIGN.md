# sniper — design

One plugin for the whole development loop, on Claude Code and Codex: read the repository once, take work in from wherever it arrives, lock the outcome, take the shortest safe path, prove only changed behavior, hand the reviewer a dossier, ship, and keep what was learned. Everything here is deliberately small: the plugin itself must not be slop.

## Non-goals

- No PRD/architecture/tech-doc quintuplets, no 50 KB skills, no telemetry, no MCP server, no modes or intensity levels: one doctrine.
- No per-language rule packs. Repository instructions (AGENTS.md / CLAUDE.md) own language conventions.
- No memory outside the repository. What a session learns goes into `docs/sniper/` and AGENTS.md, where the next session and the next person read it.
- No dependency on any other plugin, server or registry. Every detector reads git, the filesystem and the CLIs the repository already uses.
- No CHANGELOG/VERSION ceremony in `ship` unless the repository already has it.

## Layout

```
sniper/
  .claude-plugin/plugin.json, marketplace.json   Claude Code manifest and marketplace ("sniper", source "./")
  .codex-plugin/plugin.json, .agents/plugins/marketplace.json   Codex manifest and marketplace
  core/SNIPER.md                    the doctrine, injected at SessionStart and SubagentStart
  skills/<stage>/SKILL.md           5 stages, each a router under 120 lines
  skills/<stage>/references/*.md    the branches, read only when their case applies, under 80 lines each
  skills/<stage>/agents/openai.yaml Codex sidecar, one per stage
  skills/setup/scripts/upsert-agents.py          doctrine block and map pointer in AGENTS.md
  skills/ship/scripts/*.py          pr-contracts, pr-walkthrough, test-summary (the dossier's evidence)
  agents/sniper-{scout,worker,reviewer,integrator}.md   one definition per role for both hosts
  hooks/hooks.json                  shared: SessionStart, SubagentStart, PreToolUse(Bash)
  scripts/core-context.sh, guard.sh, test-guard.sh   the hooks and the guard fixtures
  scripts/checks.sh, tracker.sh, consumers.sh, tokens.sh, repo-facts.sh, debt.sh, pr-partition.py   detectors
  scripts/install-codex-agents.sh, check.sh      Codex agents generation, one-command acceptance
  evals/run.py, tasks.py            the agentic benchmark
  docs/sniper/map.md, conventions.md   the plugin's own map, built by its own setup
  AGENTS.md, .claude/CLAUDE.md      doctrine verbatim plus repo rules; CLAUDE.md imports it
  docs/DESIGN.md, docs/sources.md, README.md, LICENSE (MIT)
```

Stages are invoked as `/sniper:<stage>` in Claude Code and `$<stage>` in Codex, and by each other through the host's skill tool.

## The flow

```
setup? ──► scope ──► build ──► review ──► ship
             │          │          │
       intake, grill  plan, debug  shrink, reviewers,
       goal card      prove        integrator
```

- The loop runs itself: a request to change code goes through `scope`, `build` and `review` without a typed stage name; each stage invokes the next. `ship` runs on the user's word (ship, commit, PR) or when the request said to carry the work through. A question or a described problem gets an assessment, not the loop.
- `scope` routes by what arrived: a tracker item goes through intake (read, reproduce, already-done and already-rejected checks), an undecided design through grill (rounds through the host's question tool), a clear task straight to the card.
- `build` routes by the card: complex size plans first (`--tickets` publishes), an unknown cause debugs first, then the mode reference (fix, refactor, migrate, UI), then implementation at seams and the proof set from the repository's own commands.
- `review` shrinks first, then reviews per area and ends in the integrator, which verifies, sweeps consumers inside and outside the repository, and runs the checks with failures attributed to the baseline. `--repo` and `--debt` are read-only audits.
- `ship` commits proven work, writes the dossier as the PR body, keeps one lesson, and hands off when a session stops early. `setup` installs the doctrine on the user's invocation and builds or refreshes the map on anyone's.

## Doctrine

`core/SNIPER.md` is the one text every session and every subagent gets, about 1.3k tokens: precedence (user over skill, and a blocking skill names itself), the goal lock, the map read before discovery, the reuse ladder with the never-add and never-remove lists, the operational bug rule (grep every caller, guard the shared function once), elision with `ceiling:` comments for deliberate shortcuts, test discipline including one runnable check for non-trivial logic where none exists, proof reported exactly, adjacent findings as follow-ups, surgical edits and evidence before state changes, delegation of parallel work with results read as claims, and a stop that closes every stated intention and reports for a reader who did not watch.

It is written against the current guidance of both vendors and re-audited when either publishes a new model guide. From Anthropic's Claude Fable 5.1 guidance: goals and constraints rather than step choreography, sub-agents for parallel work, progress grounded in tool results, an assessment rather than a fix when the user asks a question, evidence before a state-changing command, a final report written outcome first for someone who was not there, no anti-formatting rules and no numeric word caps. From OpenAI's GPT-6 Astra and Codex guides: user instructions outrank a skill, bias to action with every intention closed before the turn ends, tests calibrated to the change, delegation stated explicitly, and descriptions that open with the trigger because Codex shortens them to about 45 characters when many plugins are installed. From both: no pressure language, prohibitions only where the failure is real and the reason stated, exact commands only for fragile bridges.

## Skills

Every SKILL.md: frontmatter `name`, `description` opening with `Use when`, under 70 words, ending with what it is not for; body imperative, one output block, the stop condition last, under 120 lines; every branch in `references/<branch>.md` under 80 lines, read only when its case applies; paths written as `<this skill>/…` or `<plugin root>/…` because neither host expands a variable in a skill body. Each stage ships `agents/openai.yaml` for Codex and is model-invocable, so the loop can chain; `setup` alone distinguishes the user's invocation (installs the doctrine) from the model's (`--map`, refreshes the map only).

| stage | branches | ends when |
|---|---|---|
| `setup` | `map.md` | files written, map current |
| `scope` | `intake.md`, `grill.md`, `asking.md` | card emitted and handed to build |
| `build` | `plan.md`, `debug.md`, `prove.md`, `fix.md`, `refactor.md`, `migrate.md`, `ui-taste.md` | acceptance proven and handed to review |
| `review` | `audit.md`, `platform-native.md` | one pass printed with `ship: ready` or what blocks |
| `ship` | `narrate.md`, `shapes.md`, `posting.md`, `learn.md`, `environment.md`, `handoff.md` | commits exist and any requested push, PR, dossier or handoff ran |

## Agents

`sniper-scout` (sonnet, read-only) locates code and returns `path:line` lines. `sniper-worker` (sonnet, opus on request) implements one owned slice under a contract and reports changed files, proof, blockers. `sniper-reviewer` (opus, read-only) reviews one area or lens and reports every finding with severity and confidence; its slop lens carries the six rungs plus `taste:` on UI diffs and never flags the one runnable check. `sniper-integrator` (opus, read-only) merges the per-area reports of a review pass, settles contradictions by reading the code, sweeps consumers inside and outside the repository, verifies every finding, and runs the nearest checks with each failure attributed to the baseline before it is called new. The same four files generate the Codex custom agents.

## Hooks and guard

`hooks/hooks.json` is one file for both hosts, using only what both support: `SessionStart` and `SubagentStart` with `additionalContext`, `PreToolUse` with `permissionDecision`. `core-context.sh` injects the doctrine, prints nothing at `SessionStart` when the project's AGENTS.md or CLAUDE.md already carries the block, and honours `SNIPER_SUBAGENT_MATCHER` to narrow which subagents receive it. `guard.sh` denies `--no-verify`, force pushes, `reset --hard`, whole-tree discards, `clean -f` and `rm -rf` of the root, with 45 fixtures; any script error allows, so the guard never traps the user. Scripts are POSIX shell plus `python3`, no node, no jq.

## Detectors

Where a skill used to guess, a script answers from the repository, read-only, with no configuration: `checks.sh` (the project's own typecheck, lint, test and build commands), `tracker.sh` (forge, CLI and login from the origin remote), `consumers.sh` (the names a repository publishes and the sibling checkouts whose manifests name them), `tokens.sh` (the design tokens a UI tree defines), `repo-facts.sh` (layout, hot spots, authors, commit conventions, checks, and through `gh` the merged-PR cadence, reviewers and inline commenters), `debt.sh` (the `ceiling:` ledger), `pr-partition.py` (judgment versus mechanical diff). The skill still decides; the script removes the guess. Each was proven on real repositories of several stacks before it shipped.

## Asking

A question to the user goes through the host's question tool: `AskUserQuestion` on Claude Code, `request_user_input` on Codex where its collaboration mode allows it. One contract in `skills/scope/references/asking.md`: a twelve-character header, a one-sentence question carrying the why, the recommended option first and labelled. Numbered text is the fallback.

## Codex

`.codex-plugin/plugin.json` mirrors the Claude manifest and points at the same `skills/` and `hooks/hooks.json`. Codex cannot bundle agents, so `scripts/install-codex-agents.sh` generates `~/.codex/agents/sniper_{scout,worker,reviewer,integrator}.toml` from `agents/*.md`. Codex has no `disable-model-invocation`, and no sniper stage needs one; every sidecar allows implicit invocation so the loop can chain. Codex expands `${CLAUDE_PLUGIN_ROOT}` in `hooks/hooks.json` only, presents skills to the model as absolute roots, and shortens descriptions to about 45 characters when many plugins are installed: hence host-neutral paths and trigger-first descriptions, both enforced by `check.sh`.

## Evals

A prompt change is a hypothesis until a session proves it. `evals/run.py` runs each probe as a bare `claude -p` session in a seeded temp workspace, baseline against sniper (`--plugin-dir` plus the doctrine as an appended system prompt, since bare mode skips hooks), and scores the files left behind with stdlib-only scorers. Every scorer ships a good and a bad reference and `--selftest` must pass before a single call is spent; `check.sh` runs it. The trace-transfer probe tests the doctrine's own claim about canonical causes. Live runs need `ANTHROPIC_API_KEY`, since bare mode reads no login.

## Acceptance

`sh scripts/check.sh`: four `claude plugin validate --strict` targets, the guard fixtures, manifest JSON, doctrine sync, version parity, and the repository rules executed: skill bodies under 120 lines, references under 80, no host variable inside a skill or agent, every skill with a Codex sidecar, every file a skill names present, every script parsing, the detectors answering on this repository, the ledger answering, the evals selftest passing. After a change: bump both manifests, `claude plugin update sniper@sniper`, `codex plugin remove sniper` then `codex plugin add sniper@sniper`, and `scripts/install-codex-agents.sh` when an agent changed.

## Sources

`docs/sources.md` names every external plugin, skill and vendor guide this plugin took from, what was taken, and what was rejected with the reason.
