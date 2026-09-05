---
name: scope
description: Use when a request has no stated outcome or an unclear boundary, before build or plan. Locks it into a goal card: outcome, acceptance check, exclusions, material risk, proof, size; asks at most three questions, only where answers change the work. Not for designing or implementing.
argument-hint: "[task description]"
---

1. Take the argument as the task. When it is empty, emit `blocked: task missing` and stop. That line is the only output allowed in place of the card.
2. Find the facts yourself: read the files, symbols, or commands the request names; when it names none, run one bounded search for the flow it describes. Never ask the user for something the repository can answer.
3. Draft the card from what you found. Resolve ambiguity per core, and put the chosen reading in the card as `Assuming <reading>.` inside Outcome.
4. Test every remaining unknown against one bar: would a different answer change which files change, what acceptance means, or whether the work is safe? Decide everything below that bar yourself and say nothing about it.
5. More than three survive, or a survivor is a design decision rather than a missing fact: the request is not ready for a card. Say so in one line and invoke `grill`, which settles the tree in rounds and hands the request back. Otherwise ask the survivors one at a time, at most three, each with a recommended default the user can accept in one word. Recompute after each answer, since one answer often settles the next question. When nothing survives step 4, emit the card with no questions at all.
6. Write Acceptance as a single check that fails when the outcome is absent. "Works correctly" is not a check; "GET /orders/9 returns 404 instead of 500" is.
7. Write Out of scope as the adjacent work being left alone: the neighbouring bug, the rename, the cleanup, the second reading rejected in step 3.
8. Name at most one material risk: data loss, authorization, a public contract, a migration, a concurrency window. When there is none, write `none` rather than inventing one.
9. Set Size. `surgical` = one file, one obvious edit, no new seam. `normal` = a few files under one owner. `complex` = four or more tasks, more than one owner, or a change others depend on (schema, interface, migration).
10. Set Next: `build` for surgical and normal, `plan` for complex. The next skill reads this card verbatim, so every line must stand on its own.

Emit exactly this, and nothing else:

```
Outcome: <observable state once the change lands; add "Assuming <reading>." when a reading was chosen>
Acceptance: <one check that passes only if the outcome holds>
Out of scope: <adjacent work left untouched>
Risk: <one material risk, or none>
Proof: <smallest command or exercise that would fail if the change were wrong>
Size: surgical | normal | complex
Next: build | plan
```

Stop when the card is emitted and every question asked has an answer. Do not implement, do not design the solution, do not decompose it into tasks.
