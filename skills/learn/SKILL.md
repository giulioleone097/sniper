---
name: learn
description: Use when a proven fix uncovered an invariant, trap or decision the code, tests and docs will not explain, or the user asks for a session retrospective. Writes at most three lines under Code Review Rules in the closest AGENTS.md or CLAUDE.md, or a short docs/solutions file; nothing when artifacts already explain themselves.
---

1. Name the candidate in one sentence: the invariant, trap, or decision this work uncovered. Only a fix that is already proven qualifies. When the user asked for a retrospective on the session rather than a rule about the code, the subject is the environment the next agent inherits: read `references/environment.md` and work its categories instead of steps 2 and 3, then rejoin at step 8.

2. Apply the counterfactual. Delete that sentence from the world: would the next engineer, reading the final code, tests, types, comments, and existing docs, repeat the mistake or redo the investigation? If no, print `nothing to record` and stop. Effort spent, diff size, and having been invoked do not qualify a learning.

3. Reject the candidate when it is advice true of software in general, a restatement of what the code already says, a one-off unlikely to recur, style a linter enforces, or something the target file already says. An existing entry that the work proved wrong is a rewrite of that entry, not a second one.

4. One learning per run. A session that produced several gets several runs, one at a time, so each keeps its own counterfactual.

5. Pick the target: the closest AGENTS.md or CLAUDE.md covering the changed path, nested file over root.

6. Three lines or fewer: the entry belongs under `## Code Review Rules` in that file, creating the section at the end of the file when it is missing. Shape each line `<invariant>. Safe path: <what to do instead>.` A rule without a concrete safe path is noise the next review has to ignore.

7. More than three lines: `docs/solutions/<slug>.md` instead, at most 40 lines, four headings in this order: symptom, cause, fix, how to recognize it next time. Slug names the symptom, not the fix, because the symptom is what the next engineer will search for.

8. Show the target path and the exact lines before touching the file, and write only after the user confirms in this session. No user to answer — a hands-off `flow` run, a non-interactive session — print `proposed (not written):` followed by that path and those lines, and stop.

9. Print what was written:

```
<path>
<the exact lines written>
```

   Nothing qualified: print `nothing to record` alone.

10. Stop after one learning, or after printing `nothing to record`. Never write both targets, never pad the entry to fill the budget.
