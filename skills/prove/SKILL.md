---
name: prove
description: Translates the acceptance check from a goal card or request into the smallest decisive proof set, runs it, and reports one of DONE, DONE_WITH_CONCERNS, BLOCKED, or NEEDS_CONTEXT. Use before claiming work complete, before committing or shipping, or when acceptance needs independent verification. Reuses still-valid results instead of rerunning. Not for editing product code beyond an explicitly requested fix, and not for adding tests.
---

1. Take the acceptance check from the goal card if one exists; otherwise read the request and state the check that would fail if the change were wrong.
2. Build the smallest decisive set per core's proof ladder: typecheck/lint, then the targeted test for the changed behavior, then one real exercise of the path (curl, CLI run, script) only when no test can reach it. Take the commands from the repository, not from memory: `sh <plugin root>/scripts/checks.sh <changed path>` (`<plugin root>` is the parent of the `skills/` directory this file lives in) prints the project's own typecheck, lint, test and build commands, or `none=1`. Narrow the test command to the changed behavior where the runner allows it. Stop adding checks once the set would catch a wrong change.
3. Before running a command, check whether a prior run already proves it for the current tree: same command, no file it depends on changed since. Reuse that result and mark it `reused` instead of rerunning.
4. Run every remaining command exactly as written. Capture exit status and the decisive line of output, not the full log.
5. Do not edit product code — unless the request explicitly asked for fixes, in which case fix the canonical cause per core and rerun only the checks that fix invalidated.
6. Do not add tests here. A missing seam is a gap to report, not a gap to fill.
7. Classify the result:
   - `DONE` — every command in the set passed.
   - `DONE_WITH_CONCERNS: <concern>` — passed, but state the residual risk.
   - `BLOCKED: <blocker>` — a command could not run, or failed for a reason outside this change's scope.
   - `NEEDS_CONTEXT: <what>` — the acceptance check itself is unclear or has no reachable proof.

Emit exactly this, and nothing else:

```
<command> — pass | fail | unavailable | reused
<command> — pass | fail | unavailable | reused
DONE | DONE_WITH_CONCERNS: <concern> | BLOCKED: <blocker> | NEEDS_CONTEXT: <what>
```

Stop once the status line is emitted.
