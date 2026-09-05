---
name: debug
description: Use when a failure or unexplained behavior has no known cause. Builds a tight pass/fail signal, instruments the nearest boundary instead of guessing, fixes the canonical cause, and proves it with the same signal. Not for known changes, which build owns.
argument-hint: "[failure, error text, failing test path, or the command that reproduces it]"
---

1. Write the symptom exactly as observed: expected value, actual value, exact trigger, environment. Keep it separate from any cause you already suspect.

2. Build a tight pass/fail signal before reading code for a theory. Tight means red-capable on this exact symptom (not "runs without erroring"), deterministic, seconds not minutes, and runnable unattended. Ways to build one, cheapest first:
   1. A failing test at whatever seam reaches the bug.
   2. A curl or HTTP script against the running service.
   3. A CLI invocation on a fixture input, diffed against known-good output.
   4. A headless browser script asserting on DOM, console, or network.
   5. A replay of a captured payload, trace, or event log through the path in isolation.

   Otherwise invent the cheapest thing that goes red on this symptom (bisection, differential run, fuzz loop).

3. Tighten it: faster setup, an assertion on the exact symptom, determinism (pin time, seed randomness, isolate filesystem and network). For an intermittent failure the target is a higher reproduction rate, not a clean repro: loop the trigger, parallelize, narrow the timing window until it is debuggable.

4. When no signal can be built, stop and say so: list what you tried, and ask for environment access, a captured artifact, or permission to add temporary instrumentation. Hypothesizing without a signal is the failure this skill exists to prevent.

5. Minimise the reproduction: cut inputs, config, callers, and steps one at a time, re-running the signal after each cut, until every remaining element is load-bearing.

6. Rank three to five hypotheses by evidence and by how cheaply each can be falsified. Each one states its prediction: "if X is the cause, then changing Y makes the symptom disappear." A hypothesis with no prediction is a vibe — sharpen it or drop it.

7. Inspect the nearest boundary where the hypotheses diverge: the closest place showing correct state on one side and the symptom on the other. Change one variable per probe.

8. After two uninformative attempts, instrument that boundary instead of guessing again. A debugger or REPL breakpoint beats ten logs; tag every temporary log with one unique prefix (`[DBG-a4f2]`) so removal is a single grep. For a slow path, measure a baseline and bisect — logs mislead on performance.

9. Keep credentials in environment variables, and write `<REDACTED>` in place of any token, header, or connection string in output you quote.

10. Done when the causal chain from trigger to symptom is stated with no gaps and every step carries `file:line` evidence. "Somehow X leads to Y" is a gap, not a chain.

11. Fix only when the request authorizes a fix. Repair at the point every caller routes through, per core; add a regression test only at a seam that reproduces the real bug pattern, and report the absence as a finding when no such seam exists. Then remove all instrumentation (grep the tag) and invoke `sniper:prove` with the Skill tool, or `$prove` on Codex.

12. Report:

```
cause: <one line>
evidence: <path:line> — <what it shows>
fix: <changed files> | diagnosis only
regression: <command> — pass | fail | no correct seam (<why>)
```

Stop when the mechanism is proven and reported; do not widen into adjacent defects or refactors.
