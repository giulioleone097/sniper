# Grill: settle an undecided design

Read when the request has open design branches: more than three questions survive, or a survivor is a decision rather than a missing fact.

1. Build the decision tree in your head, not on the page. Every decision hangs off the ones that must be settled before it can even be asked. The **frontier** is the set of decisions whose prerequisites are all settled: the questions answerable now without guessing at answers you have not heard.

2. Find the facts yourself, always. A frontier question that needs something the repository, the filesystem, or a command can answer is not a question for the user: one bounded search settles it inline; substantial discovery goes to one `sniper-scout` per fact (Codex: `sniper_scout`) while you keep going. A running lookup is an unsettled prerequisite: only the questions downstream of it wait, the rest of the frontier is asked now. Never ask the user for what you could read, and treat a statement about how the code behaves today as a fact to check there, not a settled premise: a contradiction, with its `path:line`, is the next question.

3. Ask the whole frontier in one round through the host's question tool, one entry per decision, shaped by `asking.md` beside this file, which also carries the per-call limits and the no-tool fallback.

4. Wait for the answers. The tool returns them keyed by question; never answer your own round, never continue to the next round on assumptions.

5. Each answer reshapes the tree: settled decisions push the frontier outward and unblock what depended on them. Recompute and ask the next round. A question whose answer depends on another still open in this round belongs to the next round, not this one.

6. Stop when the frontier is empty: every branch visited, nothing silently assumed. Then print the settled tree, one line per decision, and hand off:

```
settled:
- <decision> -> <what was chosen>. rejected: <the alternative, and why>
open (deliberately): <what the user chose to leave undecided, or "none">
next: the goal card
```

7. Record the decisions that will outlive the session. A decision whose rejected alternative a future reader would otherwise re-litigate goes to ship's learn step when the work lands, not to a document nobody reads. Do not invent an architecture-decision-record directory the repository does not already keep.

8. Never write code, never start building, and never treat "the user stopped answering" as agreement. Grilling ends with a shared understanding or with the open branches named as open.
