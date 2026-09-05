---
name: build
description: Use when a goal card, plan task or clear build request exists and code must change. Detects the mode (feature, fix, refactor, migrate), edits surgically, tests only at agreed seams, proves the change, hands the diff to simplify. Not for an unexplained failure, which debug owns.
argument-hint: "[what to build, a plan task, or the goal card from scope]"
---

1. Take the goal card from `scope` when this session has one. Otherwise write a one-line card: observable outcome, the check that proves it, what stays out. When the wording is ambiguous, implement the reading the request and the surrounding code most directly support, state that assumption in one line, and build nothing else.

2. Detect the mode from the request: `feature` (behavior that does not exist yet), `fix` (behavior that is wrong), `refactor` (structure changes, behavior identical), `migrate` (schema, data, API, protocol, config, or dependency transition). `feature` is the default and runs on these steps alone. Read `references/<mode>.md` when the mode is `fix`, `refactor`, or `migrate`. Read `references/ui-taste.md` before writing any UI code when the change touches components, styles, or templates.

3. Locate the code. `docs/sniper/map.md` names the entry points and checks per domain when the repository has one; skip this step when the files are already named or already read. Otherwise dispatch one `sniper-scout` with the entry point or the symptom, and read only the `path:line` candidates it returns. On Codex spawn the custom agent `sniper_scout` (installed by `scripts/install-codex-agents.sh`); without it, locate inline with grep.

4. Cut the work into slices, each with an outcome, owned paths, and an acceptance check. Walk the core ladder before writing anything new: the reuse rung usually collapses a slice into a few lines.

5. Name the seams you will test before writing any test. A seam is the public boundary where the behavior is observable; confirm the list when the goal card did not already fix it. When to add a test at all is per core. Then work one seam, one test, one implementation, next slice.
   Run each new test before the code that satisfies it and watch it fail: a test that passes on its first run proves nothing yet, and the failure message is the last chance to notice it is testing the wrong thing.
   Reject three shapes: a test that mocks internal collaborators or asserts private state; an assertion that recomputes the expected value the way the code does; all tests written up front before any implementation (horizontal slicing). Expected values come from a known-good literal, a worked example, or the spec.

6. Implement inline. This is the normal path: most work is a handful of edits and belongs in this session.

7. Fan out only when two or more slices own disjoint paths and each is more than a handful of tool calls. Dispatch `sniper-worker` through the Agent tool, passing `model: opus` only for a genuinely complex slice, and give each one: outcome, owned paths (touch nothing else), acceptance, the proof to run, and the checkpoint. Keep implementing your own slice while they run. Delegation limits are per core. On Codex spawn one `sniper_worker` custom agent per slice (installed by `scripts/install-codex-agents.sh`); when custom agents are not installed, run the slices sequentially in this session.

8. Implement every behavior the request asks for, completely. Adjacent findings stay untouched and become follow-ups, per core.

9. Prove the acceptance check: invoke `sniper:prove` with the Skill tool, or `$prove` on Codex. Report its verdict as it came back.

10. Report:

```
<path> — <what changed>
proof: <command> — pass | fail | unavailable | reused
status: DONE | DONE_WITH_CONCERNS: <c> | BLOCKED: <b> | NEEDS_CONTEXT: <w>
follow-ups: <one line each, or "none">
```

11. Hand the diff to `simplify`.

Stop when the acceptance check passes and the report is written; do not review, commit, or extend the work here.
