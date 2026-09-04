---
name: flow
description: Runs the whole pipeline hands-off (scope, plan when needed, build, simplify, review, prove, ship, learn), taking the recommended option at every decision and stopping before push unless the argument says otherwise. Use when the user asks for a task to be carried end to end with no check-ins. Not for exploratory work, and not when a decision genuinely needs the user mid-run.
argument-hint: "[task description] [--push] [--pr]"
disable-model-invocation: true
---

You run autonomously: nobody can answer while the pipeline is moving. `grill` needs a human in the loop, so it never runs here; a request too fuzzy for `scope` to card stops the run instead. When the run is cut short by anything other than a finished pipeline, call `handoff` before stopping so the next session starts where this one died. Take the recommended option at every decision and record which one you took. Proceed on reversible actions; stop only for a destructive action or a genuine scope change.

Invoke each stage as a skill by name: `sniper:<name>` through the Skill tool in Claude Code, `$<name>` in Codex.

1. `scope` with the argument minus any flags. Answer each question it would ask with its own recommended default and keep those defaults in the card as assumptions. The card governs every later stage.
2. `plan` only when Size is `complex` or the card implies four or more tasks. Otherwise skip it and record `plan skipped: size <size>`.
3. `build` with the card and, when one exists, the plan path. Fan out only across the plan's disjoint owned paths.
4. `simplify` on the changed code, before review sees it.
5. `review` on the diff. Re-enter `build` once carrying every P0-P2 finding, then re-run only the checks a fix invalidated. One re-entry: anything still open becomes a follow-up, not a second loop.
6. `prove` and keep its verdict verbatim. `BLOCKED` or `NEEDS_CONTEXT` stops that branch, not the run: finish every stage that does not depend on it, then say exactly what is missing.
7. `ship`, commit only. Push only when the argument carries `--push`; open a PR only when it carries `--pr`, which implies a push because `ship` pushes the branch before opening the PR. Neither flag, no remote action.
8. `learn` only when the run produced a durable non-obvious learning that is absent from code, tests, and docs. Hands-off it writes nothing: put the lines it would append to CLAUDE.md or AGENTS.md in the report instead, for the user to accept. Otherwise record `learn skipped: nothing durable`.
9. Emit one report. When the last thing you wrote is a plan or a promise, that work is not done yet: do it now, then report.

Emit exactly this once, at the end:

```
<outcome in one line>
Commits: <sha> <subject>
Proof: <command> -> <result>
Status: <prove's status line verbatim>
Follow-ups: <one per line, or none>
Learning: <proposed lines, or none>
Skipped: <stage> - <why>
Blocked: <stage> - <what stopped it> - <what would unblock it>
```

Drop the `Skipped` line when nothing was skipped and the `Blocked` line when nothing blocked. Stop when `ship` has committed and the report is emitted, or when a destructive action or a genuine scope change needs the user; report the completed stages either way.
