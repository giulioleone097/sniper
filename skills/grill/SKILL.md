---
name: grill
description: Interrogates a fuzzy request until the design is settled - a decision tree worked in rounds, every open question asked with your recommended answer, facts looked up rather than asked - and ends by handing scope a request that no longer has holes. Use before scope when the outcome is genuinely undecided, when a design has open branches, or when the user asks to have their thinking stress-tested. Not for a request whose shape is already clear: scope's three questions cover that. Never writes code.
argument-hint: "[the idea, plan, or design to grill]"
---

1. Take the argument as the subject. Empty: ask what to grill and stop there.

2. Decide whether this needs grilling at all. A request whose outcome, boundary and acceptance you could already write is not fuzzy: say so in one line, name the reading you would take, and hand it to `scope` instead. Grilling a settled request manufactures decisions nobody needed.

3. Build the decision tree in your head, not on the page. Every decision hangs off the ones that must be settled before it can even be asked. The **frontier** is the set of decisions whose prerequisites are all settled: the questions answerable now without guessing at answers you have not heard.

4. Find the facts yourself, always. A frontier question that needs something the repository, the filesystem, or a command can answer is not a question for the user: dispatch one `sniper-scout` per fact (Codex: `sniper_scout`) and keep going. A running lookup is an unsettled prerequisite: only the questions downstream of it wait, the rest of the frontier is asked now. Never ask the user for what you could read.

5. Ask the whole frontier in one round, numbered, each with the answer you recommend and the one-clause reason. A recommendation the user can accept with one word is the difference between an interview and an interrogation.

```
Q1 <title>: <the question, and the options if there are options>
   -> <your recommended answer>. <why, in one clause>
Q2 <title>: ...
```

6. Wait for the answers. Never answer your own round, never continue to the next round on assumptions. This skill needs a human in the loop, so `flow` and any hands-off run must not call it.

7. Each answer reshapes the tree: settled decisions push the frontier outward and unblock what depended on them. Recompute and ask the next round. A question whose answer depends on another still open in this round belongs to the next round, not this one.

8. Stop when the frontier is empty: every branch visited, nothing silently assumed. Then print the settled tree, one line per decision, and hand off:

```
settled:
- <decision> -> <what was chosen>. rejected: <the alternative, and why>
open (deliberately): <what the user chose to leave undecided, or "none">
next: scope
```

9. Record the decisions that will outlive the session. A decision whose rejected alternative a future reader would otherwise re-litigate goes to `learn` when the work lands, not to a document nobody reads. Do not invent an architecture-decision-record directory the repository does not already keep.

10. Never write code, never start building, and never treat "the user stopped answering" as agreement. Grilling ends with a shared understanding or with the open branches named as open.
