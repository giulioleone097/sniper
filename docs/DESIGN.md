# atlas — design

One plugin for the whole development loop, on Claude Code, Codex, Devin and Cursor: read the repository once, take work in from wherever it arrives, lock the outcome, take the shortest safe path, prove only changed behavior, hand the reviewer a dossier, ship, and keep what was learned. Everything here is deliberately small: the plugin itself must not be slop.

## Non-goals

- No PRD/architecture/tech-doc quintuplets, no 50 KB skills, no telemetry, no MCP server, no modes or intensity levels: one doctrine.
- No per-language rule packs. Repository instructions (AGENTS.md / CLAUDE.md) own language conventions.
- No memory outside the repository. What a session learns goes into `docs/atlas/` and AGENTS.md, where the next session and the next person read it.
- No dependency on any other plugin, server or registry. Every detector reads git, the filesystem and the CLIs the repository already uses.
- No CHANGELOG/VERSION ceremony in `ship` unless the repository already has it.

## Layout

```
atlas/
  .claude-plugin/plugin.json, marketplace.json   Claude Code manifest and marketplace ("atlas", source "./")
  .codex-plugin/plugin.json, .agents/plugins/marketplace.json   Codex manifest and marketplace
  .devin-plugin/plugin.json       Devin manifest (highest manifest precedence there)
  .cursor-plugin/plugin.json      Cursor manifest; declares hooks/cursor-hooks.json
  core/ATLAS.md                    the doctrine, injected at SessionStart and SubagentStart
  rules/atlas-core.mdc             Cursor rule: doctrine verbatim + alwaysApply (check.sh keeps it in sync)
  skills/<stage>/SKILL.md           5 stages and 9 named entry points (atlasme, simplify, handoff, optimize, intel, question, howto, prototype, improve), each under 120 lines
  skills/<stage>/references/*.md    the branches, read only when their case applies, under 80 lines each
  skills/<stage>/agents/openai.yaml Codex sidecar, one per stage
  skills/setup/scripts/upsert-agents.py          doctrine block and map pointer in AGENTS.md
  skills/ship/scripts/*.py          pr-contracts, pr-walkthrough, test-summary (the dossier's evidence)
  agents/atlas-{scout,worker,reviewer,integrator}.md   one definition per role for all hosts (tools:, allowed-tools:, readonly: union)
  hooks/hooks.json                  Claude Code + Codex: SessionStart, SubagentStart, PreToolUse(Bash)
  hooks.json                        Devin (plugin-root convention): PreToolUse(exec|write_to_process)
  hooks/cursor-hooks.json           Cursor: beforeShellExecution; doctrine comes via the .mdc rule
  scripts/core-context.sh, guard.sh, test-guard.sh   the hooks and the guard fixtures
  scripts/checks.sh, tracker.sh, consumers.sh, tokens.sh, repo-facts.sh, debt.sh, pr-partition.py   detectors
  scripts/install-codex-agents.sh, install-devin.sh, install-cursor.sh, check.sh   per-host user-level installers, one-command acceptance
  evals/run.py, tasks.py            the agentic benchmark
  docs/atlas/map.md, conventions.md   the plugin's own map, built by its own setup
  AGENTS.md, .claude/CLAUDE.md      doctrine verbatim plus repo rules; CLAUDE.md imports it
  docs/DESIGN.md, docs/sources.md, README.md, LICENSE (MIT)
```

Stages are invoked as `/atlas:<stage>` in Claude Code and Devin, `$<stage>` in Codex, `/atlas-<stage>` in the script-installed user-level copies, and by each other through the host's skill tool.

## The flow

```
setup? ──► scope ──► build ──► review ──► ship
             │          │          │
       intake, grill  plan, debug  shrink, reviewers,
       goal card      prove        integrator
```

- The loop chooses its path: a small understood change uses direct implement, review, fix and prove; broader or uncertain work goes through `scope`, `build` and `review`, with each stage invoking the next. `ship` runs on the user's word (ship, commit, PR) or when the request said to carry the work through. A question or a described problem gets an assessment, not the loop.
- `scope` routes by what arrived: a tracker item, an image or a handoff/atlasme file goes through intake (forge and CLI from `tracker.sh` for every item, pasted included; read or transcribe, reproduce, already-done and already-rejected checks, proven lines reused, decided lines honoured; `--reply` posts the result back on the item after confirmation), an undecided design through grill (rounds through the host's question tool), a clear task straight to the card, whose Source line carries intake's provenance; a touched contract's consumers are counted (`git grep -w`, `consumers.sh`) before Risk and Size are written, and no argument and no request in the conversation offers the latest handoff to resume. `atlasme` typed on a document or item reads it through intake first and grills only what it leaves open; each option is costed by its reach at HEAD (domains and entry points from the map, consumers via `git grep -w` and `consumers.sh`, a code-graph impact query when the host exposes one) and the settled tree carries `reach:` and `risk:` per decision plus one map when more than one domain is reached, which the card's Risk and Size reuse; card only, stop or `--out` writes the settled tree to disk.
- `build` routes by the card: a non-card argument (an issue, URL, image, handoff or atlasme file) goes back through `scope`, complex size plans first (a brief in chat, or `docs/plans/` for four or more tasks, several owners or a risk surface; `--tickets` publishes), an unknown cause debugs first, then the mode reference (fix, refactor, migrate; UI taste when a visual design decision is made), then implementation at seams, an indispensable test run red in a detached worktree of `HEAD` before green, parallel workers in their own worktrees under a temp dir (seeded with the lead's uncommitted work, integrated back as a diff) when their builds or tests would collide, and the card's proof command run as written, else the proof set from the repository's own commands, a real picture for a UI change; `--no-review` skips only the handoff to review.
- `review` takes the task's diff (staged, unstaged and new files included; a clean tree on a branch reviews `git diff <default branch>...HEAD`), shrinks within scope (`slop.md` catalogs the patterns, the rung that cuts each and the case where it stays), then reviews locally or with economical subagents when independently assignable areas justify them. `--pr` posts one thread per finding at its line in the PR head (the current branch's PR unless one is named; a finding on an unchanged line goes into the summary) and one summary, or `drafted: <path> - <reason>` when there is no PR, CLI or login; `--address <pr>` checks out the PR's head when the tree is clean, stops when another branch has local changes, and answers the reviewers' threads from the code, fixed at the shared cause (the `fixed in <sha>` replies wait for `ship --push`), rebutted with `path:line` evidence, or recorded as follow-ups, never resolving a thread the reviewer opened. It verifies reports and fixes real in-scope defects by default, with `--read-only` preserving an explicit no-edit request (cuts and fixes printed as proposals, `net: -<N> lines possible.`); integration is used when several reports interact. It sweeps consumers inside and outside the repository when external contracts change and runs checks with failures attributed to the baseline. `--repo` and `--debt` are read-only audits.
- `ship` commits proven work in the language of the repository's recent commits (a commit scope only when they carry one; the proof rerun from a worktree at `HEAD` when a file left out of the commits feeds it), writes the dossier as the PR body (`--pr` on the default branch first creates `<type>/<slug>`; an open PR for the branch is reused, its body refreshed only when it carries the `<!-- atlas:narrate -->` marker), waits for CI after `--pr` with each failure attributed to the base branch or to the PR, keeps one lesson (`proposed (not written)` on a hands-off run), deletes the handoff or atlasme file the work resumed from so a bare `scope` no longer offers finished work, and closes its block with `proof:`, `learned:` and `left:`, the paths kept out of the commits; a session stopping early calls `handoff` instead. The dossier is minimal: a verdict, plain words, one map, then one diagram per domain with `confine`, `prova`, `decisione` and `rischio` lines only where they carry a fact, headings and labels in the dossier's language (`--lang`, else the repository's; only the marker is fixed), and real end-to-end screenshots or videos from the repository's own harness (`evidence.md`: Playwright and Cypress recording switches, GitLab uploads, Azure DevOps PR attachments, GitHub only where the repository already keeps evidence files); `--dossier [pr]` resolves the range on GitHub, GitLab and Azure DevOps, `--post` replaces the body on all three (on Azure DevOps the description carries the first screen alone, the drill-down as closed threads), `--walkthrough` is GitHub-only. `setup` installs the doctrine on the user's invocation and builds or refreshes the map on anyone's.
- `atlasme`, `simplify`, `handoff`, `optimize`, `intel`, `question`, `howto`, `prototype` and `improve` are entry points typed by name, not stages: atlasme interrogates an idea before any card exists (typed bare, it asks what to grill), costs every option by its reach at HEAD as a forecast rather than a verdict, and ends by asking whether to build, card only, or stop; simplify shrinks code nobody asked to review (the files named, else the diff since the baseline or merge-base plus staged, unstaged and new files) and never runs review; handoff writes where the work stands, extra worktrees and conversation-only decisions included, to `--out <file>` or `docs/handoff-<yyyy-mm-dd>-<slug>.md` for the next session, which resumes it by passing the file to `scope` (intake reads it, reuses what is proven, verifies what is assumed, honours what is decided), and `ship` deletes the file once the work is committed; optimize pushes one measured number toward a target. Atlasme and simplify are thin routers into scope's `grill.md` and review's `shrink.md`, so the logic lives once; handoff and optimize carry their own procedure, since no stage shares it.
- `optimize` is the keep/discard loop with parallel worlds: one metric command that starts what it measures from the checkout (a number read from a process started elsewhere is refused) plus `--guard` metrics with a maximum they must not exceed, owned paths from `--paths` or the request, else asked for, a profile of the metric naming the families when the stack has a profiler, a baseline measured three times (five or seven when the band is too wide for the target) with its noise band in a detached worktree of `HEAD` that stays as the champion tree and is re-measured each round as that round's baseline (what it shows a fresh checkout lacks, every hypothesis worktree receives), rounds of `--parallel` hypotheses from distinct families, each in its own detached `git worktree` and `atlas-worker`, every report re-measured by the lead before a keep, at most one keep per round committed on a scaffolding branch `optimize/<slug>` that later rounds fork from (a branch left by a stopped run blocks a new run until landed or deleted), a runner-up that beat the baseline on files disjoint from the champion's replayed on it as the next round's first hypothesis, a ledger rewritten after every round with every measured value so nothing is retried and a stopped run leaves a record, and a stop when the target is met, two consecutive rounds of untried families kept nothing, the budget is spent or no new hypothesis exists. The champion lands as an applied merge-base diff (`git diff HEAD...optimize/<slug> | git apply`, so commits the main tree took meanwhile survive), the branch is deleted, and `review` takes the diff, a review edit re-measured on the main tree with the `kpi:` lines reprinted; ship commits it when asked. Being faster and wrong, or narrowing what the metric measures, is a discard, and the owned paths never widen to reach the target.

## Doctrine

`core/ATLAS.md` is the one text every session and every subagent gets, about 1.3k tokens: precedence (user over skill, and a blocking skill names itself), the goal lock (stated even when a skill's steps already fix its three parts), the map read before discovery, the reuse ladder with the never-add and never-remove lists, the operational bug rule (grep every caller, guard the shared function once), elision with `ceiling:` comments for deliberate shortcuts, indispensable-only tests with optional TDD, proof reported exactly, in-scope fixes and adjacent follow-ups, surgical edits and evidence before state changes, economical delegation with results read as claims, and a stop that closes every stated intention and reports for a reader who did not watch.

It is written against the current guidance of both vendors and re-audited when either publishes a new model guide. From Anthropic's Claude Fable 5.1 guidance: goals and constraints rather than step choreography, sub-agents for parallel work, progress grounded in tool results, an assessment rather than a fix when the user asks a question, evidence before a state-changing command, a final report written outcome first for someone who was not there, no anti-formatting rules and no numeric word caps. From OpenAI's GPT-6 Astra and Codex guides: user instructions outrank a skill, bias to action with every intention closed before the turn ends, tests calibrated to the change, delegation stated explicitly, and descriptions that open with the trigger because Codex shortens them to about 45 characters when many plugins are installed. From both: no pressure language, prohibitions only where the failure is real and the reason stated, exact commands only for fragile bridges.

## Skills

Every SKILL.md: frontmatter `name`, `description` opening with `Use when`, under 70 words, ending with what it is not for; body imperative, one output block, the stop condition last, under 120 lines; every branch in `references/<branch>.md` under 80 lines, read only when its case applies; paths written as `<this skill>/…` or `<plugin root>/…` because neither host expands a variable in a skill body. Each stage ships `agents/openai.yaml` for Codex and is model-invocable, so the loop can chain; `setup` alone distinguishes the user's invocation (installs the doctrine) from the model's (`--map`, refreshes the map only).

| stage | branches | ends when |
|---|---|---|
| `setup` | `map.md` | files written, map current |
| `scope` | `intake.md` (issues, PRs, reports, images, handoff and atlasme files), `grill.md`, `asking.md` | card emitted and handed to build; no argument and no request in the conversation offers the latest handoff |
| `build` | `plan.md`, `debug.md`, `prove.md`, `fix.md`, `refactor.md`, `migrate.md`, `ui-taste.md` | acceptance proven and handed to review |
| `review` | `shrink.md`, `slop.md`, `platform-native.md`, `audit.md`, `pr.md` | one pass printed with `ship: ready` or what blocks; `--address` when every reviewer thread has its line |
| `ship` | `narrate.md`, `shapes.md`, `evidence.md`, `posting.md`, `learn.md`, `environment.md` | commits exist and any requested push, PR (with its CI awaited) or dossier ran; the block names `proof:`, `learned:` (or `proposed (not written)`) and `left:` |
| `atlasme` | scope's `intake.md` for a document subject, `grill.md`, `asking.md`, ship's `shapes.md` for the map | settled tree with reach and risk per decision, and the map when more than one domain is reached, printed and, on card only, stop or `--out`, written to disk; chosen next step run |
| `simplify` | review's `shrink.md`, `slop.md`, `audit.md`, `platform-native.md` | nothing left to cut in scope, proof run |
| `handoff` | none | file written, path printed |
| `optimize` | scope's `asking.md` | block printed, review run on the kept diff or declined |

## Agents

`atlas-scout` (sonnet, or `gpt-5.6-luna` on Codex, read-only) locates code and returns `path:line` lines. `atlas-worker` (sonnet, opus on request; `gpt-5.6-luna` / `gpt-5.6-terra` on Codex) implements one owned slice under a contract and reports changed files, proof, blockers. `atlas-reviewer` and `atlas-integrator` use opus (or Terra on Codex), remain read-only, and are used only when their independent analysis or integration adds value. Reviewers report defects; the lead verifies and repairs them. Astra/Fable coordinate scope, decisions, and integration. The same four files generate the Codex custom agents.

## Hooks and guard

One hooks file per host family — the events and output shapes differ, so no file is shared across families: `hooks/hooks.json` for Claude Code and Codex (`SessionStart`, `SubagentStart` with `additionalContext`, `PreToolUse` with `permissionDecision`), `hooks.json` at the plugin root for Devin (`PreToolUse` on `exec`/`write_to_process`; Devin has no `SubagentStart` and its doctrine arrives via the plugin's always-on `AGENTS.md`), `hooks/cursor-hooks.json` for Cursor (`beforeShellExecution`; the doctrine arrives via `rules/atlas-core.mdc`, and Cursor's `subagentStart` answers `permission` only, so it is not wired).

`core-context.sh` injects the doctrine, prints nothing at either event when an AGENTS.md or CLAUDE.md from the session directory up to the root already carries the block (non-fork subagents receive those files too), when a host-global rules file (`~/.config/devin/AGENTS.md`, `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`) carries it — Cursor payloads are recognised by their fields and skip that check since Cursor reads none of those files — and honours `ATLAS_SUBAGENT_MATCHER` (with `SNIPER_SUBAGENT_MATCHER` still read as fallback) to narrow which subagents receive it. Its payload carries both `hookSpecificOutput.additionalContext` (Claude, Codex, Devin) and top-level `additional_context` (Cursor); each host reads the field it knows.

`guard.sh` denies `--no-verify`, force pushes, `reset --hard`, whole-tree discards, `clean -f` and `rm -rf` of the root, with 45 fixtures; any script error allows, so the guard never traps the user. It reads the command from `tool_input.command` (Claude, Codex, Devin `exec`), `tool_input.text_input`/`bytes_input` (Devin `write_to_process`) or top-level `command` (Cursor), and answers with the union of the hosts' deny shapes: `hookSpecificOutput.permissionDecision: deny`, `decision: block` + `reason`, `permission: deny` + `user_message`/`agent_message`. Scripts are POSIX shell plus `python3`, no node, no jq.

The user-level installers exist for hosts whose plugin manager is unavailable or unwanted: `install-devin.sh` writes `~/.config/devin/` (skills as `atlas-<stage>` with `atlas:` references rewritten to `atlas-`, agents verbatim, the doctrine block in the global `AGENTS.md`, and merged `config.json` hooks — SessionStart kept as a self-healing path whose dedup makes it a no-op while the block stands); `install-cursor.sh` writes `~/.cursor/` (same skills treatment, agents with `model:` reset to `inherit`, merged `hooks.json` carrying `sessionStart` + `beforeShellExecution`). Both are idempotent, preserve foreign entries, prune removed stages, and revert with `--remove`.

## Detectors

Where a skill used to guess, a script answers from the repository, read-only, with no configuration: `checks.sh` (the project's own typecheck, lint, test and build commands), `tracker.sh` (forge, CLI and login from the origin remote, with gh and glab probed for hosts under another name), `consumers.sh` (the names a repository publishes and the sibling checkouts whose manifests name them), `tokens.sh` (the design tokens a UI tree defines), `repo-facts.sh` (layout, hot spots, authors, commit conventions, checks, and through `gh` the merged-PR cadence, reviewers and inline commenters), `debt.sh` (the `ceiling:` ledger), `pr-partition.py` (judgment versus mechanical diff). The skill still decides; the script removes the guess. Each was proven on real repositories of several stacks before it shipped.

## Asking

A question to the user goes through the host's question tool: `AskUserQuestion` on Claude Code, `request_user_input` on Codex where its collaboration mode allows it. One contract in `skills/scope/references/asking.md`: a twelve-character header, a one-sentence question carrying the why, the recommended option first and labelled. Numbered text is the fallback.

## Codex

`.codex-plugin/plugin.json` mirrors the Claude manifest and points at the same `skills/` and `hooks/hooks.json`. Codex cannot bundle agents, so `scripts/install-codex-agents.sh` generates `~/.codex/agents/atlas_{scout,worker,reviewer,integrator}.toml` from `agents/*.md`. Codex has no `disable-model-invocation`, and no atlas stage needs one; every sidecar allows implicit invocation so the loop can chain. Codex expands `${CLAUDE_PLUGIN_ROOT}` in `hooks/hooks.json` only, presents skills to the model as absolute roots, and shortens descriptions to about 45 characters when many plugins are installed: hence host-neutral paths and trigger-first descriptions, both enforced by `check.sh`.

## Devin

`.devin-plugin/plugin.json` takes manifest precedence over the Claude one on Devin and carries metadata only — `skills/` is the default and `AGENTS.md` loads as the always-on rule, so the doctrine needs no hook there. `agents/*.md` load as `atlas:<name>` custom subagents in the CLI and Devin Desktop (not cloud sessions); their `allowed-tools` list is the Devin field, kept next to Claude's `tools:` so each host reads its own — `readonly:` is Cursor's. The root `hooks.json` is Devin's only plugin hooks convention; its command uses `${CLAUDE_PLUGIN_ROOT:-.}` — ceiling: if a Devin build expands neither `${CLAUDE_PLUGIN_ROOT}` nor runs hooks from the plugin root, the guard fails open and the doctrine still loads via the rule; upgrade trigger: a documented Devin plugin-root variable for hook commands. Plugin hooks are best-effort and fail open on Devin; the user-level installer is the dependable path for the guard.

## Cursor

`.cursor-plugin/plugin.json` declares `skills`, `rules`, `agents` and `hooks` explicitly so no convention file is needed beyond it — `hooks/hooks.json` stays Claude-shaped for its own hosts and Cursor never parses it as its own. `rules/atlas-core.mdc` is the doctrine verbatim between the same markers `AGENTS.md` uses, `alwaysApply: true`; `check.sh` keeps it in sync with `core/ATLAS.md`. Agent files carry `readonly: true` for the read-only roles; `model:` values are Claude/Devin names Cursor may not resolve, so the user-level installer rewrites them to `inherit` and the plugin bundle leaves them to fall back.

## Evals

A prompt change is a hypothesis until a session proves it. `evals/run.py` runs five probes as bare `claude -p` sessions in seeded temp workspaces, comparing baseline, current atlas, and optionally a preserved previous plugin directory, and scores the files left behind with stdlib-only scorers. Every scorer ships a good and a bad reference and `--selftest` must pass before a single call is spent; `check.sh` runs it. Cost, duration, and turns report medians over available cells with `available/total` coverage, so missing or partial metrics are not treated as zero. Live runs need `ANTHROPIC_API_KEY`, since bare mode reads no login; no gain claim is made without live comparison results.

## Acceptance

`sh scripts/check.sh`: four `claude plugin validate --strict` targets, the guard fixtures, manifest JSON, doctrine sync across `AGENTS.md` and `rules/atlas-core.mdc`, version parity across the four plugin manifests, per-host hook event rules (each hooks file may name only events its host fires, and the three installers plus the `.mdc` must exist), and the repository rules executed: skill bodies under 120 lines, references under 80, no host variable inside a skill or agent, every skill with a Codex sidecar, every file a skill names present, every script parsing, the detectors answering on this repository, the ledger answering, the evals selftest passing, the doctrine under 9,000 bytes (hook `additionalContext` is cut at 10,000 characters on Claude Code and near 2,500 tokens on Codex). After a change: bump all four manifests, `claude plugin update atlas@atlas`, `codex plugin remove atlas` then `codex plugin add atlas@atlas`, `devin plugins update atlas` or reinstall on Cursor, re-run `scripts/install-*.sh` where they were used, and `scripts/install-codex-agents.sh` when an agent changed.

## Sources

`docs/sources.md` names every external plugin, skill and vendor guide this plugin took from, what was taken, and what was rejected with the reason.
