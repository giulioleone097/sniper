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
  skills/<name>/SKILL.md            16 skills, each under 120 lines
  skills/<name>/agents/openai.yaml  Codex sidecar, one per skill
  skills/<name>/references/*.md     a genuinely conditional branch, under 80 lines
  skills/setup/scripts/upsert-agents.py          doctrine block and map pointer in AGENTS.md
  skills/narrate/scripts/*.py       pr-contracts, pr-walkthrough, test-summary
  agents/sniper-{scout,worker,reviewer,integrator}.md   one definition per role for both hosts
  hooks/hooks.json                  shared: SessionStart, SubagentStart, PreToolUse(Bash)
  scripts/core-context.sh, guard.sh, test-guard.sh   the hooks and the guard fixtures
  scripts/checks.sh, tracker.sh, consumers.sh, tokens.sh, repo-facts.sh, debt.sh, pr-partition.py   detectors
  scripts/install-codex-agents.sh, check.sh      Codex agents generation, one-command acceptance
  evals/run.py, tasks.py            the agentic benchmark
  docs/sniper/map.md, conventions.md   the plugin's own map, built by its own skill
  AGENTS.md, .claude/CLAUDE.md      doctrine verbatim plus repo rules; CLAUDE.md imports it
  docs/DESIGN.md, docs/sources.md, README.md, LICENSE (MIT)
```

Skills are invoked as `/sniper:<name>` in Claude Code and `$<name>` in Codex.

## The flow

```
map? ──► intake? ──► grill? ──► scope ──► plan? ──► build ──► simplify ──► review ──► prove ──► narrate ──► ship ──► learn?
                                                                        handoff (any time the session ends early)
  ▲                   │
  └──── debug ◄───────┘ (when a real failure appears)
```

- `map` once per repository, refreshed only for what moved since its stamp; every later skill reads it before discovering.
- `intake` when the work arrives as an issue, PR, work item or pasted report; `grill` when the design is genuinely undecided; both hand a request to `scope`.
- `plan` only for four or more tasks, several owners, or a change others depend on. Otherwise `scope` hands straight to `build`.
- `simplify` runs on the changed code before `review`, so review sees the lean diff. Both split by area and end in the integrator.
- `review` findings go back to `build`; one exact-diff pass, recheck only what a fix touched.
- `narrate` writes the dossier `ship --pr` uses as the PR body. `learn` runs only when the reasoning would otherwise be lost, or on the comments a PR received.
- `flow` runs the pipeline hands-off, taking the recommended option at every decision and stopping before push unless told otherwise; it never calls `grill`, and calls `handoff` when it stops early.

## Doctrine

`core/SNIPER.md` is the one text every session and every subagent gets, about 1.3k tokens: precedence (user over skill, and a blocking skill names itself), the goal lock, the map read before discovery, the reuse ladder with the never-add and never-remove lists, the operational bug rule (grep every caller, guard the shared function once), elision with `ceiling:` comments for deliberate shortcuts, test discipline including one runnable check for non-trivial logic where none exists, proof reported exactly, adjacent findings as follow-ups, surgical edits and evidence before state changes, delegation of parallel work with results read as claims, and a stop that closes every stated intention and reports for a reader who did not watch.

It is written against the current guidance of both vendors and re-audited when either publishes a new model guide. From Anthropic's Claude Fable 5.1 guidance: goals and constraints rather than step choreography, sub-agents for parallel work, progress grounded in tool results, an assessment rather than a fix when the user asks a question, evidence before a state-changing command, a final report written outcome first for someone who was not there, no anti-formatting rules and no numeric word caps. From OpenAI's GPT-6 Astra and Codex guides: user instructions outrank a skill, bias to action with every intention closed before the turn ends, tests calibrated to the change, delegation stated explicitly, and descriptions that open with the trigger because Codex shortens them to about 45 characters when many plugins are installed. From both: no pressure language, prohibitions only where the failure is real and the reason stated, exact commands only for fragile bridges.

## Skills

Every SKILL.md: frontmatter `name`, `description` opening with `Use when`, under 70 words, ending with what it is not for; body imperative, one output block, the stop condition last, under 120 lines; a genuinely conditional branch in `references/<branch>.md` under 80 lines; paths written as `<this skill>/…` or `<plugin root>/…` because neither host expands a variable in a skill body. Each skill ships `agents/openai.yaml` for Codex.

| skill | does | ends when |
|---|---|---|
| `setup` | doctrine block into AGENTS.md, CLAUDE.md import, map pointer, then `map` | files written |
| `map` | `repo-facts.sh` facts, reviewers' comments on the last merged PRs, optional code-graph or symbol server, `docs/sniper/map.md` and `conventions.md` with a stamp; `--linked` for consumer repositories | paths and stamp printed |
| `intake` | item read through the tracker the repo has, claim reproduced, already-implemented and already-rejected checked, card through `scope`; `--reply` after confirmation | card or what is missing |
| `grill` | decision tree in rounds through the host's question tool, facts looked up by a scout, settled tree handed to `scope` | frontier empty |
| `scope` | goal card: outcome, acceptance, exclusions, risk, proof, size; at most three questions through the question tool | card emitted |
| `plan` | tasks with owned paths, acceptance, proof, test seams; brief or `docs/plans/` file; `--tickets` publishes them | plan written |
| `build` | mode detected, code located from the map, slices with seams, one runnable check where no test exists, proof through `prove`, diff to `simplify` | acceptance passes |
| `debug` | pass/fail signal, boundary instrumented, canonical cause fixed and proven | mechanism proven |
| `simplify` | six rungs per area with the platform lookup, `ceiling:` on kept limits, integrator proves nothing moved; `--repo` audits, `--debt` prints the ledger | nothing left in scope |
| `review` | one reviewer per area or lens with the repository's conventions, integrator merges, catches cross-area and cross-repo breakage, runs the checks; `--fix`, `--pr` | one pass printed |
| `prove` | smallest decisive set from `checks.sh`, results reused, status reported | status line |
| `narrate` | partition, blast radius in and out of the repository, executed evidence attributed to the baseline, dossier with a map and a per-domain drill-down; `--post`, `--walkthrough` | dossier written |
| `handoff` | where the work stands, proven versus believed, open work, artifacts pointed at, secrets redacted | file written |
| `ship` | atomic commits, tracker item linked, push or PR only when asked, body from `narrate` | commits exist |
| `learn` | one durable rule into Code Review Rules or `docs/solutions`, from a fix, a PR's reviewers (`--from-pr`), or a session retrospective | one learning or none |
| `flow` | the pipeline hands-off | done or blocked |

## Agents

`sniper-scout` (sonnet, read-only) locates code and returns `path:line` lines. `sniper-worker` (sonnet, opus on request) implements one owned slice under a contract and reports changed files, proof, blockers. `sniper-reviewer` (opus, read-only) reviews one area or lens and reports every finding with severity and confidence; its slop lens carries the six rungs plus `taste:` on UI diffs and never flags the one runnable check. `sniper-integrator` (opus, read-only) merges the per-area reports, settles contradictions by reading the code, sweeps consumers inside and outside the repository, verifies every finding, and runs the nearest checks with each failure attributed to the baseline before it is called new. The same four files generate the Codex custom agents.

## Hooks and guard

`hooks/hooks.json` is one file for both hosts, using only what both support: `SessionStart` and `SubagentStart` with `additionalContext`, `PreToolUse` with `permissionDecision`. `core-context.sh` injects the doctrine, prints nothing at `SessionStart` when the project's AGENTS.md or CLAUDE.md already carries the block, and honours `SNIPER_SUBAGENT_MATCHER` to narrow which subagents receive it. `guard.sh` denies `--no-verify`, force pushes, `reset --hard`, whole-tree discards, `clean -f` and `rm -rf` of the root, with 45 fixtures; any script error allows, so the guard never traps the user. Scripts are POSIX shell plus `python3`, no node, no jq.

## Detectors

Where a skill used to guess, a script answers from the repository, read-only, with no configuration: `checks.sh` (the project's own typecheck, lint, test and build commands), `tracker.sh` (forge, CLI and login from the origin remote), `consumers.sh` (the names a repository publishes and the sibling checkouts whose manifests name them), `tokens.sh` (the design tokens a UI tree defines), `repo-facts.sh` (layout, hot spots, authors, commit conventions, checks, and through `gh` the merged-PR cadence, reviewers and inline commenters), `debt.sh` (the `ceiling:` ledger), `pr-partition.py` (judgment versus mechanical diff). The skill still decides; the script removes the guess. Each was proven on real repositories of several stacks before it shipped.

## Asking

A question to the user goes through the host's question tool: `AskUserQuestion` on Claude Code, `request_user_input` on Codex where its collaboration mode allows it. One contract in `skills/scope/references/asking.md`: a twelve-character header, a one-sentence question carrying the why, the recommended option first and labelled. Numbered text is the fallback.

## Codex

`.codex-plugin/plugin.json` mirrors the Claude manifest and points at the same `skills/` and `hooks/hooks.json`. Codex cannot bundle agents, so `scripts/install-codex-agents.sh` generates `~/.codex/agents/sniper_{scout,worker,reviewer,integrator}.toml` from `agents/*.md`. Codex has no `disable-model-invocation`; the sidecar's `policy.allow_implicit_invocation` is `false` only for `flow` and `setup`. Codex expands `${CLAUDE_PLUGIN_ROOT}` in `hooks/hooks.json` only, presents skills to the model as absolute roots, and shortens descriptions to about 45 characters when many plugins are installed: hence host-neutral paths and trigger-first descriptions, both enforced by `check.sh`.

## Evals

A prompt change is a hypothesis until a session proves it. `evals/run.py` runs each probe as a bare `claude -p` session in a seeded temp workspace, baseline against sniper (`--plugin-dir` plus the doctrine as an appended system prompt, since bare mode skips hooks), and scores the files left behind with stdlib-only scorers. Every scorer ships a good and a bad reference and `--selftest` must pass before a single call is spent; `check.sh` runs it. The trace-transfer probe tests the doctrine's own claim about canonical causes. Live runs need `ANTHROPIC_API_KEY`, since bare mode reads no login.

## Acceptance

`sh scripts/check.sh`: four `claude plugin validate --strict` targets, the guard fixtures, manifest JSON, doctrine sync, version parity, and the repository rules executed: skill bodies under 120 lines, references under 80, no host variable inside a skill or agent, every skill with a Codex sidecar, every file a skill names present, every script parsing, the detectors answering on this repository, the ledger answering, the evals selftest passing. After a change: bump both manifests, `claude plugin update sniper@sniper`, `codex plugin remove sniper` then `codex plugin add sniper@sniper`, and `scripts/install-codex-agents.sh` when an agent changed.

## Sources

`docs/sources.md` names every external plugin, skill and vendor guide this plugin took from, what was taken, and what was rejected with the reason.
