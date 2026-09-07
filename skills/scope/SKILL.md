---
name: scope
description: Use when work arrives, as a task, an issue, a PR, a report or an idea, and before any code changes. Verifies the source, settles open design branches, locks a goal card and hands it to build. Not for implementing.
argument-hint: "[task | issue number | url | file | pasted text] [--card-only]"
---

1. Take the argument as the work. Empty: emit `blocked: task missing` and stop; that line is the only output allowed in place of the card.

2. Route by what arrived. An issue number, a URL, a work item, a pasted report or a transcript: read `<this skill>/references/intake.md` (`<this skill>` is the directory this file lives in) and come back here with what it established. A task whose outcome is genuinely undecided, with open design branches rather than missing facts: read `references/grill.md`, settle the tree with the user, and come back with the settled decisions. A task whose outcome, boundary and acceptance you could already write: continue.

3. Find the facts yourself: `docs/sniper/map.md` first when it exists, then the files, symbols, or commands the request names; when it names none, run one bounded search for the flow it describes. Never ask the user for something the repository can answer.

4. Draft the card from what you found. Resolve ambiguity per core, and put the chosen reading in the card as `Assuming <reading>.` inside Outcome.

5. Test every remaining unknown against one bar: would a different answer change which files change, what acceptance means, or whether the work is safe? Decide everything below that bar yourself and say nothing about it.

6. More than three survive, or a survivor is a design decision rather than a missing fact: `references/grill.md`. Otherwise ask the survivors, at most three, through the host's question tool with the recommended default first, contract in `references/asking.md`; one call carries all three, and one answer often settles the next.

7. Write Acceptance as a single check that fails when the outcome is absent. "Works correctly" is not a check; "GET /orders/9 returns 404 instead of 500" is.

8. Write Out of scope as the adjacent work being left alone: the neighbouring bug, the rename, the cleanup, the second reading rejected in step 4.

9. Name at most one material risk: data loss, authorization, a public contract, a migration, a concurrency window. None: write `none`.

10. Set Size. `surgical` = one file, one obvious edit, no new seam. `normal` = a few files under one owner. `complex` = four or more tasks, more than one owner, or a change others depend on (schema, interface, migration).

Emit exactly this:

```
Outcome: <observable state once the change lands; add "Assuming <reading>." when a reading was chosen>
Acceptance: <one check that passes only if the outcome holds>
Out of scope: <adjacent work left untouched>
Risk: <one material risk, or none>
Proof: <smallest command or exercise that would fail if the change were wrong>
Size: surgical | normal | complex
Source: <issue, PR, or "request">
```

Then invoke `build` with the card (Skill tool `sniper:build`, `$build` on Codex), unless `--card-only` was given or the user asked for the card alone. The loop does not wait to be told: a card that exists is a card that gets built.
