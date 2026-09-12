# Debug: a failure with no known cause

Read when the request is a failure or unexplained behavior whose cause is not yet known; build continues once the mechanism is proven.

1. Write the symptom exactly as observed: expected value, actual value, exact trigger, environment. Keep it separate from any cause you already suspect.

2. Build a tight pass/fail signal before reading code for a theory. Tight means red-capable on this exact symptom (not "runs without erroring"), deterministic, seconds not minutes, and runnable unattended. Ways to build one, cheapest first:
   1. A failing test at whatever seam reaches the bug.
   2. A curl or HTTP script against the running service.
   3. A CLI invocation on a fixture input, diffed against known-good output.
   4. A headless browser script asserting on DOM, console, or network — or the repo's e2e harness itself run with recording on (`<plugin root>/skills/ship/references/evidence.md` step 2 names the switches) when the symptom lives in a UI flow.
   5. A replay of a captured payload, trace, or event log through the path in isolation.

   Otherwise invent the cheapest thing that goes red on this symptom (bisection, differential run, fuzz loop).

3. Tighten it: faster setup, an assertion on the exact symptom, determinism (pin time, seed randomness, isolate filesystem and network). For an intermittent failure the target is a higher reproduction rate, not a clean repro: loop the trigger, parallelize, narrow the timing window until it is debuggable.

4. When no signal can be built, stop and say so: list what you tried, and ask for environment access, a captured artifact, or permission to add temporary instrumentation. Hypothesizing without a signal is the failure this skill exists to prevent.

5. Minimise the reproduction: cut inputs, config, callers, and steps one at a time, re-running the signal after each cut, until every remaining element is load-bearing.

6. Rank three to five hypotheses by evidence and by how cheaply each can be falsified. Each one states its prediction: "if X is the cause, then changing Y makes the symptom disappear." A hypothesis with no prediction is a vibe — sharpen it or drop it.

7. Inspect the nearest boundary where the hypotheses diverge: the closest place showing correct state on one side and the symptom on the other. Change one variable per probe.

8. After two uninformative attempts, instrument that boundary instead of guessing again. Live tools that can answer the hypothesis directly — a debugger or REPL breakpoint, a devtools MCP server attached to the running app — beat adding logs; instrument only what they cannot reach. When logging, write structured lines to a per-run timestamped file in a scratch dir (`debug-<slug>-<ts>.log`), keep the last three to five runs and prune older — a file you can diff across runs beats a console you scroll, and you analyze the file, never the transcript. Tag every temporary log with one unique prefix per run and ranked hypothesis (`[DBG-a4f2:H1:checkout]`) so each line maps to the hypothesis under test and removal is a single grep. When the failing surface is a browser whose console cannot be read, run a tiny local HTTP endpoint that appends to the run's log file and have the frontend POST debug events fire-and-forget with `keepalive` — never rely on copy-pasted console output. For a slow path, measure a baseline and bisect — logs mislead on performance. After two instrument-and-analyze cycles without a confirmed cause, escalate to the user with the collected log evidence instead of cycling a third time.

9. Keep credentials in environment variables, and write `<REDACTED>` in place of any token, header, or connection string in output you quote.

10. Done when the causal chain from trigger to symptom is stated with no gaps and every step carries `file:line` evidence. "Somehow X leads to Y" is a gap, not a chain.

11. Fix only when the request authorizes a fix. Repair at the point every caller routes through, per core; add a regression test only at a seam that reproduces the real bug pattern, and report the absence as a finding when no such seam exists. Then remove all instrumentation (grep the tag) and return to `build`, which proves the fix through `references/prove.md`.

12. Report:

```
cause: <one line>
evidence: <path:line> — <what it shows>
fix: <changed files> | diagnosis only
regression: <command> — pass | fail | no correct seam (<why>)
```

Stop when the mechanism is proven and reported; do not widen into adjacent defects or refactors.
