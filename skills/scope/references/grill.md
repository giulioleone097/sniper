# Grill: settle an undecided design

Read when the request has open design branches: more than three questions survive, or a survivor is a decision rather than a missing fact.

1. Build the decision tree in your head, not on the page. Every decision hangs off the ones that must be settled before it can even be asked. The **frontier** is the set of decisions whose prerequisites are all settled: the questions answerable now without guessing at answers you have not heard.

2. Find the facts yourself, always. A frontier question that needs something the repository, the filesystem, or a command can answer is not a question for the user: one bounded search settles it inline; substantial discovery goes to one `atlas-scout` per fact (Codex: `atlas_scout`) while you keep going. A running lookup is an unsettled prerequisite: only the questions downstream of it wait, the rest of the frontier is asked now. Never ask the user for what you could read, and treat a statement about how the code behaves today as a fact to check there, not a settled premise: a contradiction, with its `path:line`, is the next question.

3. Cost each option by its reach, measured at HEAD since no diff exists yet. The domains it would touch and their entry points come from `docs/atlas/map.md` (Domini, Confini, Repository collegati) when the repository has a map, else from one bounded search; every shared contract the option would change (an exported symbol, a schema, an endpoint, a config key, a message) gets its consumers counted with `git grep -w`; the repositories outside this one come from `sh <plugin root>/scripts/consumers.sh` (`<plugin root>` is the parent of the `skills/` directory this file lives in), marked unread when not checked out; a code-graph server's impact query is used when the host exposes one and cited as the source. That reach is the option's cost clause in the round. A decision whose options touch the same code, or none (a name, a wording, a policy), gets no reach. A count is what was measured, never "should be fine"; a forecast is not evidence, so no ✅, ⚠️ or ❌ here: those belong to `ship`, which measures the real diff.

4. Ask the whole frontier in one round through the host's question tool, one entry per decision, shaped by `asking.md` beside this file, which also carries the per-call limits and the no-tool fallback.

5. Wait for the answers. The tool returns them keyed by question; never answer your own round, never continue to the next round on assumptions.

6. Each answer reshapes the tree: settled decisions push the frontier outward and unblock what depended on them. Recompute and ask the next round. A question whose answer depends on another still open in this round belongs to the next round, not this one. An answer that resolves a term of vocabulary, not just a decision, goes through `glossary.md` right there: it lands in the target repository's `CONTEXT.md` before the next round is asked, and a use of that term contradicting an existing entry becomes the next question instead of a settled premise.

7. Stop when the frontier is empty: every branch visited, nothing silently assumed. Then print the settled tree, one entry per decision with the reach and risk of what was chosen, and hand off. A reach or risk line with nothing to say is omitted. When the settled choices reach more than one domain, one map follows the tree in the grammar of `<plugin root>/skills/ship/references/shapes.md`, "The map": lanes as the reader's mental model, the nodes the work would change, the untouched neighbours that prove the reach; no per-domain diagram, since nothing has changed yet.

```
settled:
- <decision> -> <what was chosen>. rejected: <the alternative, and why>
  reach: <domain> (<entry path:line>) -> <contract> -> <n consumers at HEAD>; <linked repository> (<n> | unread)
  risk: <the consequence in plain words>
open (deliberately): <what the user chose to leave undecided, or "none">
map: <one flowchart, only when more than one domain is reached>
next: the goal card
```

`scope` reuses the reach lines for the card's Risk and Size while the contracts they name are unchanged at HEAD, so the reach is measured once.

8. Record the decisions that will outlive the session. A decision whose rejected alternative a future reader would otherwise re-litigate goes to ship's learn step when the work lands, not to a document nobody reads. Do not invent an architecture-decision-record directory the repository does not already keep.

9. Never write code, never start building, and never treat "the user stopped answering" as agreement. Grilling ends with a shared understanding or with the open branches named as open.
