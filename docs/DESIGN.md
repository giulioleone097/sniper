# sniper — design

One plugin for the whole development loop: lock the outcome, take the shortest safe path, prove only changed behavior, stop. Works in Claude Code (skills + subagents + hooks) and Codex (skills + sidecars). Everything here is deliberately small: the plugin itself must not be slop.

## Non-goals

- No PRD/architecture/tech-doc quintuplets, no 50 KB skills, no telemetry, no "instincts", no memory system, no MCP server.
- No per-language rule packs. Repository instructions (CLAUDE.md / AGENTS.md) own language conventions.
- No CHANGELOG/VERSION ceremony in `ship` unless the repository already has it.

## Layout

```
sniper/
  .claude-plugin/plugin.json        # Claude Code manifest
  .claude-plugin/marketplace.json   # marketplace "sniper", source "./"
  .codex-plugin/plugin.json         # Codex manifest ("skills": "./skills/")
  .agents/plugins/marketplace.json  # Codex marketplace
  core/SNIPER.md                    # doctrine, injected at SessionStart/SubagentStart
  skills/<name>/SKILL.md            # 12 skills, each <= 120 lines body
  skills/setup/scripts/upsert-agents.py  # idempotent AGENTS.md/CLAUDE.md upsert
  skills/narrate/scripts/*.py       # pr-partition.py, pr-contracts.py, test-summary.py, pr-walkthrough.py
  skills/<name>/references/*.md     # only when a branch is genuinely conditional
  skills/<name>/agents/openai.yaml  # Codex sidecar
  agents/sniper-scout.md            # sonnet, read-only locator
  agents/sniper-worker.md           # sonnet by default, bounded implementer
  agents/sniper-reviewer.md         # opus, read-only diff reviewer with a lens
  AGENTS.md                         # doctrine (verbatim) + repo rules, both hosts read this
  .claude/CLAUDE.md                 # @../AGENTS.md (root CLAUDE.md fails plugin validate --strict)
  hooks/hooks.json                  # shared: SessionStart, SubagentStart, PreToolUse(Bash)
  scripts/core-context.sh           # prints core as additionalContext JSON
  scripts/guard.sh                  # denies destructive git / rm commands
  scripts/test-guard.sh             # fixture suite for guard.sh
  scripts/install-codex-agents.sh   # generates ~/.codex/agents/*.toml from agents/*.md
  scripts/check.sh                  # one-command acceptance run
  docs/DESIGN.md, docs/sources.md, README.md, LICENSE (MIT)
```

Skills are invoked as `/sniper:<name>` in Claude Code and `$<name>` in Codex.

## The flow

```
scope ──► plan? ──► build ──► simplify ──► review ──► prove ──► narrate ──► ship ──► learn?
  ▲                   │
  └──── debug ◄───────┘ (when a real failure appears)
```

- `plan` only when the work has 4+ steps or more than one owner. Otherwise `scope` hands straight to `build`.
- `simplify` runs on the changed code before `review`, so review sees the lean diff.
- `review` findings go back to `build`; one exact-diff pass, recheck only what a fix touched.
- `learn` runs only when the solved problem's reasoning is absent from code, tests, and docs.
- `flow` runs the pipeline end to end hands-off (scope → plan? → build → simplify → review → prove → ship → learn?) and stops before push/PR unless told otherwise.

## Skill contracts

Every SKILL.md: frontmatter `name`, `description` (third person, front-loaded trigger, what it does + when to use, <= 600 chars), optional `argument-hint`, `allowed-tools` only when the skill needs a grant. Body: imperative, numbered steps, one output format block, explicit stop condition. No preamble, no philosophy sections, no "you are an expert". Hard cap 120 lines; push a genuinely conditional branch into `references/<branch>.md` and point at it with one line.

| skill | invoke | what | output | stop when |
|---|---|---|---|---|
| `setup` | user | `scripts/upsert-agents.py` installs or refreshes the doctrine block in the project's `AGENTS.md` between `sniper:core` markers and makes `CLAUDE.md` (or `.claude/CLAUDE.md`) import it; the skill then fills the proof commands from what the repo declares. `SessionStart` skips injection when the block is present in the project. | two status lines | files written |
| `scope` | model+user | Lock outcome, acceptance check, exclusions, material risk, proof, size (surgical / normal / complex). Ask at most 3 questions, one at a time, only when different answers change the work. | Goal card (<= 10 lines) | card accepted or answered |
| `plan` | model+user (scope's Next: plan, flow) | Tasks with owned paths (disjoint when parallel), acceptance, proof, test seams. Chat brief for < 4 tasks, `docs/plans/<yyyy-mm-dd>-<slug>.md` otherwise. | brief or plan file | plan written; never implements |
| `build` | model+user | Implement under the goal card. Modes `feature` / `fix` / `refactor` / `migrate` auto-detected; each mode is a short reference. Tests at pre-agreed seams only. Fan out `sniper-worker` only for disjoint owned paths. | changed files + proof line | acceptance passes; hands to `simplify` |
| `debug` | model+user | Build a tight pass/fail signal first, then rank hypotheses, inspect the nearest boundary, instrument after two uninformative attempts. | cause in one line + evidence + fix (only if authorized) | mechanism proven |
| `review` | model+user | Exact `baseline..HEAD` or working-tree diff. Three lenses run as parallel `sniper-reviewer` calls: correctness, slop (ponytail format), safety/silent-failure. Reviewers report everything with confidence 0–100; the lead keeps >= 80 and P0–P2. Applies repository `## Code Review Rules`. `--fix` applies findings; `--pr` posts one comment via `gh` after confirmation. | `path:line P<n> <lens>: problem. fix.` lines, `net: -N lines possible`, or `CLEAN` | one pass done |
| `simplify` | model+user | Behavior-preserving elision of the changed code through six rungs that are also the output tags: `reuse:` `stdlib:` `native:` `delete:` `yagni:` `shrink:` (shared with the review slop lens). `--repo [path]` = read-only audit ranked by git hot spots. Never clever. | shorter diff or `Lean already.` | no finding left or scope exhausted |
| `prove` | model+user | Translate acceptance into the smallest decisive check set; run it; reuse still-valid results. | exact commands + `DONE` / `DONE_WITH_CONCERNS` / `BLOCKED` / `NEEDS_CONTEXT` | proof complete |
| `narrate` | model+user; `ship --pr` uses it for the body | Approval dossier. Mechanical first: `scripts/pr-partition.py` splits the diff into judgment / tests / mechanical / generated / docs / config; the workspace tool lists affected projects and which are pure dependents; `scripts/pr-contracts.py` finds exported symbols the diff removes with consumers outside the diff and deleted files still referenced. Then executed evidence: a worktree at HEAD, the repository's own test target per affected project, build/typecheck per pure dependent, results summarised by `scripts/test-summary.py`; failures are attributed by running the same target on the merge-base. Written for the approver in the PR's language: verdict, plain-words change list, then one drill-down per affected domain or repository (why touched, what the change does, kind of change, who it reaches and the line that absorbs it, executed evidence with base attribution, residual risk, technical detail folded); before anything is declared outside the verification the skill must try to run the check, cite the existing test, or show the code path, and what remains names its owner (release runbook, nightly job, the author), never the approver. Commands and the engineer's reading guide sit in collapsible `<details>` blocks. `--post` replaces the PR body after confirmation; `--walkthrough` posts one review of inline why-comments via `scripts/pr-walkthrough.py` after confirmation. | dossier (<= 150 lines) | dossier written or posted |
| `ship` | user, or from flow | Atomic behavior-named commits (Conventional Commits, subject <= 50, body only for non-obvious why), PR body (what / why / proof / follow-ups). No attribution trailers. Push and PR only on explicit ask. | commit shas, PR url | committed (and pushed if asked) |
| `learn` | user; model after non-obvious fix | Capture one durable learning: <= 3 lines under `## Code Review Rules` in the closest AGENTS.md/CLAUDE.md, or a `docs/solutions/<slug>.md` when it needs more. Write nothing when the reasoning is already in code/tests/docs. Prints the proposed lines and writes only after the user confirms; inside `flow` it reports the proposal instead of writing. | file path or "nothing to record" | one learning or none |
| `flow` | user | Run the pipeline hands-off; auto-choose the recommended option at every decision; stop before push. | final report | pipeline done or blocked |

Shared output discipline for every skill: first line is the outcome, then only what a reader who did not watch needs. No "Great question", no bullet praise, no restating the request.

## Agent contracts

`agents/sniper-scout.md` — `model: sonnet`, `tools: Read, Grep, Glob, Bash`. Read-only locator. Returns `path:line — symbol — note` lines plus the 3–8 files worth reading, or `No match.` Never suggests fixes.

`agents/sniper-worker.md` — `model: sonnet` (the caller passes `model: opus` for genuinely complex slices), all tools. Receives an owner contract: outcome, owned paths (touch nothing else), acceptance, proof, checkpoint. Returns one terminal message: changed files, proof run with results, blockers, follow-ups. Never widens scope, never reviews its own work twice.

`agents/sniper-reviewer.md` — `model: opus`, `tools: Read, Grep, Glob, Bash`. Input: baseline, lens (`correctness` | `slop` | `safety`), goal card if any. Reports every finding it sees with confidence 0–100 and severity P0–P3 (coverage stage; the lead filters). No fixes, no praise, no style nits that tooling already enforces.

These same three files also generate the Codex custom agents (see Codex below): `scripts/install-codex-agents.sh` reads `agents/*.md` directly, so there is one agent definition per role for both hosts.

## Hooks

`hooks/hooks.json` is one file shared by Claude Code and Codex (both support `SessionStart`/`SubagentStart` with `additionalContext` and `PreToolUse` with `permissionDecision`; Codex sets `PLUGIN_ROOT` natively and this hooks file also gets `CLAUDE_PLUGIN_ROOT` for compatibility). On Codex the user trusts the three hooks once in `/hooks` before they fire.
- `SessionStart` (matcher `startup|resume|clear|compact`) and `SubagentStart` → `scripts/core-context.sh`, which (for `SessionStart` only) prints nothing when the session's `cwd` has an `AGENTS.md` or `CLAUDE.md` carrying `<!-- sniper:core:start -->`, and otherwise prints `{"hookSpecificOutput":{"hookEventName":"<event>","additionalContext":"<core/SNIPER.md>"}}`. `SubagentStart` has no matcher on purpose: every subagent gets the doctrine; narrow with `sniper:.*`.
- `PreToolUse` matcher `Bash` → `scripts/guard.sh`. Denies: `--no-verify` (as a token alongside `git`), `git push --force` / `-f` / a `+refspec` (allows `--force-with-lease`), `git reset --hard`, `git checkout ... .` in any form, `git restore ... .` in any form unless staged-only, `git clean -f*`, `rm -rf` of `/`, `~`, `$HOME`, `${HOME}`, `.`, `..`, `*` (with or without a trailing `/` or `/*`). Everything else passes. Deny output: `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"..."}}`. Any script error → allow (never trap the user).

Scripts are POSIX shell + `python3 -c` for JSON parsing (no node, no jq).

## Codex

`.codex-plugin/plugin.json` mirrors name/version/description, points `"skills": "./skills/"`, and sets `"hooks": "./hooks/hooks.json"` — the same file Claude Code uses. Codex plugins cannot bundle agent definitions, so `scripts/install-codex-agents.sh` generates `~/.codex/agents/{sniper_scout,sniper_worker,sniper_reviewer}.toml` from `agents/*.md` (hyphens → underscores, `model` → `model_reasoning_effort`, no Edit/Write tools → `sandbox_mode = "read-only"`); `build` and `review` spawn those when installed, else fall back to inline/sequential. Each skill also ships `agents/openai.yaml`; Codex has no `disable-model-invocation`, so `policy.allow_implicit_invocation` plays that role and is `false` only for `flow`. Without hooks, the doctrine is reachable via `AGENTS.md` (copy the block) or a `@/path/to/sniper/core/SNIPER.md` import in `CLAUDE.md`.

## Model prompting rules baked in

From Anthropic's Fable 5.1 / Opus 5 / Sonnet 5 guidance:
- Scope discipline snippet (don't fix adjacent bugs, one focused test per stated behavior, scratch checks not committed) → `core` and `build`.
- "Finish the whole task; don't stop on a plan" → `flow`, `build`.
- Batch independent tool calls; lead keeps working while subagents run → `build`, `review`.
- Surgical edits over whole-file rewrites → `core`.
- Progress cadence: one line before the first tool call, updates only on direction change, outcome first at the end → `core`, every skill's output block.
- Delegate only large independent work; never to double-check yourself → `core`, `build`.
- Review harness: reviewers report everything with confidence, a separate filter stage ranks → `review`.
- Frontend anti-slop (no Inter/Roboto/system fonts, no purple gradients, no cookie-cutter layouts) → `build` reference `ui-taste.md`, used only when UI files change.

## Sources

See docs/sources.md.

## Ownership for implementation

| owner | paths |
|---|---|
| W1 (opus) | `skills/scope`, `skills/plan`, `skills/flow` |
| W2 (opus) | `skills/build` (+ references `fix.md`, `refactor.md`, `migrate.md`, `ui-taste.md`), `skills/debug` |
| W3 (opus) | `skills/review`, `skills/simplify`, `skills/learn`, `agents/sniper-reviewer.md` |
| W4 (sonnet) | `skills/prove`, `skills/ship`, `agents/sniper-scout.md`, `agents/sniper-worker.md` |
| W5 (sonnet) | manifests (`.claude-plugin/*`, `.codex-plugin/*`, `.agents/*`), `hooks/`, `scripts/`, `LICENSE`, `docs/sources.md`, `README.md` |

Each skill owner also writes that skill's `agents/openai.yaml`. Lead owns `core/SNIPER.md`, this file, final README pass, validation, review, install.

## Acceptance

- `sh scripts/check.sh` passes (four `claude plugin validate --strict` targets, guard fixtures, manifest JSON, doctrine sync, version parity).
- `claude plugin details sniper` lists 15 skills, 4 agents, 3 hook events, and the projected token cost stays under ~2.5k tokens at session start (core + skill descriptions).
- `scripts/guard.sh` denies the listed commands and allows `git push --force-with-lease`, `rm -rf node_modules` (checked with fixture JSON on stdin).
- Every SKILL.md body <= 120 lines; no skill references a file that does not exist.
- Installed from the local marketplace and `/sniper:scope` resolves in a fresh session.
- `sh scripts/install-codex-agents.sh` writes three TOML files and `codex` lists them.

## Executable primitives (0.13)

Where a skill used to say "run the nearest check" or "read the tracker", a script now answers from the repository: `scripts/checks.sh`, `scripts/tracker.sh`, `scripts/tokens.sh`, `scripts/consumers.sh`, `scripts/pr-partition.py`. The skill still decides; the script removes the guess. Paths inside skills are host-neutral (`<this skill>`, `<plugin root>`) because Codex expands no variable in a skill body.
