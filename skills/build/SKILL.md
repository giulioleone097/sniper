---
name: build
description: Use when a goal card or a clear build request exists and code must change, or a failure has no known cause. Plans when complex, implements surgically at agreed seams, fixes the canonical cause, proves the change, and hands the diff to review. Not for reviewing.
argument-hint: "[goal card | what to build | the failure] [--no-review]"
---

1. Take the goal card from `scope` when this session has one. Otherwise write a one-line card: observable outcome, the check that proves it, what stays out. When the wording is ambiguous, implement the reading the request and the surrounding code most directly support, state that assumption in one line, and build nothing else.

2. Route. A failure or unexplained behavior with no known cause: read `<this skill>/references/debug.md` (`<this skill>` is the directory this file lives in) and continue here once the mechanism is proven. Size `complex`, four or more tasks, several owners, or a change others depend on: read `references/plan.md`, write the plan, then continue task by task. Otherwise detect the mode: `feature` (behavior that does not exist yet) runs on these steps alone; `fix`, `refactor` and `migrate` read `references/<mode>.md`; any change touching components, styles or templates reads `references/ui-taste.md` before the first line of UI code.

3. Locate the code. `docs/sniper/map.md` names the entry points and checks per domain when the repository has one; skip this step when the files are already named or already read. Otherwise dispatch one `sniper-scout` with the entry point or the symptom, and read only the `path:line` candidates it returns (Codex: `sniper_scout`; without it, locate inline with grep).

4. Cut the work into slices, each with an outcome, owned paths, and an acceptance check. Walk the core ladder before writing anything new: the reuse rung usually collapses a slice into a few lines.

5. Name the seams you will test before writing any test. A seam is the public boundary where the behavior is observable; confirm the list when the goal card did not already fix it. When to add a test at all is per core. Then work one seam, one test, one implementation, next slice. Run each new test before the code that satisfies it and watch it fail: a test that passes on its first run proves nothing yet, and the failure message is the last chance to notice it is testing the wrong thing. Reject three shapes: a test that mocks internal collaborators or asserts private state; an assertion that recomputes the expected value the way the code does; all tests written up front before any implementation. Expected values come from a known-good literal, a worked example, or the spec.

6. Implement inline. This is the normal path: most work is a handful of edits and belongs in this session.

7. Fan out only when two or more slices own disjoint paths and each is more than a handful of tool calls. Dispatch `sniper-worker` through the Agent tool (Codex: `sniper_worker`), passing `model: opus` only for a genuinely complex slice, and give each one: outcome, owned paths (touch nothing else), acceptance, the proof to run, and the checkpoint. Keep implementing your own slice while they run; without custom agents, run the slices sequentially here.

8. Implement every behavior the request asks for, completely. Adjacent findings stay untouched and become follow-ups, per core.

9. Prove the acceptance check: `references/prove.md`. Report its verdict as it came back.

10. Report:

```
<path> — <what changed>
proof: <command> — pass | fail | unavailable | reused
status: DONE | DONE_WITH_CONCERNS: <c> | BLOCKED: <b> | NEEDS_CONTEXT: <w>
follow-ups: <one line each, or "none">
```

Then invoke `review` on the diff (Skill tool `sniper:review`, `$review` on Codex) unless `--no-review` was given. Do not commit here; that is ship's step, and it runs when asked.
