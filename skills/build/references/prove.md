# Prove: the smallest decisive check set

Read at the end of a build whose card names no proof command, and from ship before committing.

1. Take the acceptance check from the goal card if one exists; otherwise read the request and state the check that would fail if the change were wrong.
2. Choose the smallest decisive existing check or real exercise of the path (curl, CLI run, script); typecheck, lint and tests are options, not a mandatory sequence. A UI change is proven by a real picture of the changed flow: the end-to-end harness recording through `<plugin root>/skills/ship/references/evidence.md`, or a screenshot of the dev server exercising it; typecheck and unit tests alone do not prove what the user sees. Take commands from the repository: `sh <plugin root>/scripts/checks.sh <changed path>` (`<plugin root>` is the parent of the `skills/` directory this file lives in) lists available checks. Run required checks and narrow others to the changed behavior. Stop adding checks once the relevant failure would be caught.
3. Before running a command, check whether a prior run already proves it for the current tree: same command, no file it depends on changed since. Reuse that result and mark it `reused` instead of rerunning.
4. Run every remaining command exactly as written. Capture exit status and the decisive line of output, not the full log.
5. Fix verified in-scope failures per core, then rerun only the checks the repair invalidated. Do not add a test merely to produce proof.
6. Classify the result:
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
