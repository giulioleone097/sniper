---
name: wayfinder
description: Use when an effort is too big for one session, a loose idea in fog with more open decisions than one grill pass can close. Charts the decisions as a map of nodes with blocking edges, resolves the frontier one node at a time by running grill on it, and updates the map file so a later session resumes mid-map. Not for a subject grill alone can settle.
argument-hint: "[the effort to chart] [--out <file>]"
---

1. Take the argument as the subject. Empty: look for the most recent `docs/wayfinder-*.md`; found, offer through the host's question tool to resume it, start something else, or stop, and continue with the answer; none, ask what to chart in one line and stop. A file whose first line is `# Wayfinder:`: read it, take its unsettled nodes as the frontier and its `next:` line as where to resume, then skip to step 4.

2. A subject whose outcome, boundary and acceptance you could already write, or whose open decisions `<plugin root>/skills/scope/references/grill.md` would close in one pass (three or fewer questions, none blocked on another), is not wayfinder's job: say so in one line, invoke `grill` on it directly (Skill tool `sniper:grill`, `$grill` on Codex), and stop. Wayfinder is the layer above grill for what one pass cannot settle, not a replacement for it.

3. Chart the map breadth-first, without resolving anything yet: read `<plugin root>/skills/scope/references/grill.md` far enough to enumerate the decision tree's nodes, one per decision, each carrying the list of nodes that must settle first (its blocking edges). A question not yet sharp enough to state precisely, only sensed as coming, is not a node: name the destination it clarifies instead and let it graduate into a node once a resolved neighbour sharpens it. Work that sits beyond the destination is not a node either: name it under Out of scope and move on.

4. The frontier is every unsettled node whose blocking nodes are all settled. An empty frontier with unsettled nodes still on the map means the map is wrong (a cycle, or a node that will never sharpen on its own): say so and stop. An empty frontier with none left: the way is clear, go to step 6.

5. Resolve exactly one frontier node this session, unless a second is a fact one bounded search settles outright: invoke `grill` on that node's question alone (Skill tool `sniper:grill`, `$grill` on Codex; its question-tool contract lives in `<plugin root>/skills/scope/references/asking.md`, its reach-costing in `<plugin root>/skills/scope/references/grill.md`). Take its settled tree as the answer, mark the node settled on the map, and recompute the frontier. A resolution that sharpens a previously vague area turns that area into new nodes added to the map, not resolved in the same session.

6. Write the map to `--out <file>` when given, otherwise `docs/wayfinder-<yyyy-mm-dd>-<slug>.md`, reusing the file just read in step 1 once one exists rather than starting a second map for the same subject. Head it `# Wayfinder: <subject>` and print the path.

```
# Wayfinder: <subject>
next: <the next frontier node to resolve, or "clear - hand to scope"> - call `grill` on it

## Destination
<what reaching the end of this map looks like, one or two lines>

## Nodes
- [x] <node> -> <what was chosen>. blocked by: <node, ... | none>
- [ ] <node> - blocked by: <node, ... | none>

## Out of scope
- <node or area ruled out, and why>
```

7. Stop once the file is written and its path printed, whether the frontier is empty or not. Do not resolve a second node in the same session, and do not start building: an empty frontier hands off to `scope` on the settled map (Skill tool `sniper:scope`, `$scope` on Codex) only once the user asks to proceed.
