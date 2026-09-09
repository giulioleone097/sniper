---
name: build
description: Use when a goal card or a clear build request exists and code must change, or a failure has no known cause. Plans when complex, implements surgically at agreed seams, fixes the canonical cause, proves the change, and hands the diff to review. Not for reviewing.
argument-hint: "[goal card | what to build | the failure] [--tickets] [--no-review]"
---

1. Take the goal card from `scope` or from the argument when one exists; otherwise lock the goal per core in one line, stating any chosen reading. An issue number, a URL, an image, a handoff or grill file is scope's input, not a card: invoke `scope` with it (Skill tool `sniper:scope`, `$scope` on Codex) and stop here; its intake reads the source, emits the card and invokes `build` with it.

2. Route. A small understood change follows core's short path; finish it here, including local review and fixes, without another skill handoff. A failure with no known cause: read `<this skill>/references/debug.md` (`<this skill>` is the directory this file lives in). `Size: complex`, several owners, a change others depend on, or `--tickets` (publishes the plan's tasks): read `references/plan.md`. Load `references/fix.md`, `references/refactor.md` or `references/migrate.md` only for the applicable work, and `references/ui-taste.md` only when making visual design decisions.

3. Locate only what is still unknown. Start at named files or the relevant map entry; a bounded search is normally enough. Use a `sniper-scout` (Codex: `sniper_scout`) when discovery is substantial and independent of useful work you can continue locally.

4. Cut the work into slices (a plan's tasks, when one exists), each with an outcome, owned paths, and an acceptance check. Walk the core ladder before writing anything new: the reuse rung usually collapses a slice into a few lines.

5. A test that passes core's indispensability rule runs red before green: the failing run is the last chance to catch a wrong test. When the code already exists, run the red in a detached worktree of `HEAD` (`git worktree add --detach <dir> HEAD`, `<dir>` under `mktemp -d`, the test copied in, removed afterwards) rather than by reverting tracked files in place, which puts the tree's other edits at risk. Take expected values from the contract or a worked example; do not ask for routine test-design approval.

6. Implement the local slice or a trivial edit inline; keep independently assignable work available for economical delegation in the next step.

7. Delegate independently assignable slices to `sniper-worker` subagents (Codex: `sniper_worker`) under core's delegation rule, adding the slice's acceptance check to each contract. Parallel writers need disjoint paths; when their builds, generated files or test runs would collide in one tree, each gets its own `git worktree add --detach <dir> HEAD`, `<dir>` under `mktemp -d` so nothing leaks into the repository, seeded with the lead's uncommitted work including new files (`git add -A -N && git diff HEAD | git -C <dir> apply --index`; a clean tree needs no seed), with the project's install step run there when the proof needs ignored inputs such as `node_modules`, `.venv` or `target`. The lead integrates each result with `git -C <dir> add -N -- <owned paths> && git -C <dir> diff -- <owned paths> | git apply`, then `git worktree remove --force <dir>`. A worker that returns `blocked:` or `too-big:` is re-dispatched with something changed (the missing context, a more capable model, or a split), never the same contract to the same model twice, and never absorbed silently: the report names what changed.

8. Prove the acceptance check: run the proof command the card names exactly as written and capture its own exit status with the decisive output line (a trailing `| tail` reports tail's status, not the command's); when the card names none, `references/prove.md` chooses the check set.

9. Report:

```
<path> — <what changed>
proof: <command> — pass | fail | unavailable | reused
status: DONE | DONE_WITH_CONCERNS: <c> | BLOCKED: <b> | NEEDS_CONTEXT: <w>
follow-ups: <one line each, or "none">
```

Then invoke `review` on the actual task diff (Skill tool `sniper:review`, `$review` on Codex) unless the short path already completed local review or `--no-review` was given; the flag skips only that handoff, and the short path's local review still runs. Do not commit here; that is ship's step, and it runs when asked.
