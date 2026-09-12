# Deepen: survey for shallow modules

Read when the ask is structural: how the codebase could be easier to change, what shape it is in, or how a planned change could be made easy. A deep module hides a lot behind a small interface; a shallow one leaks its implementation through an interface nearly as complex as the code beneath it. The survey finds the shallow ones and proposes, per candidate, the deepening that fixes it.

1. Scope before scanning. A direction the user named - a module, a subsystem, a pain point, a planned change: take it and skip the inference. Otherwise rank the hot spots, the files that keep changing:

   `git log --oneline -n 300 --name-only --pretty=format: | sort | uniq -c | sort -rn | head -30`

   A deepening pays off only by making future changes easier, so one in untouched code is never cashed in: let the hot paths pull attention first. History scattered, no hot spot: widen the net.

2. Read `CONTEXT.md` at the repository root and `docs/atlas/map.md` when they exist, and let their nouns name things from here on: "the Order intake module", never the class name, and the architecture words module, interface, depth, seam, locality, leverage - not "service" or "boundary". Decisions a `docs/adr/` already records are settled, not re-litigated.

3. Walk the scoped paths and note where reading them costs friction; a broad tree goes to one `atlas-scout` per area (Codex: `atlas_scout`) while you keep reading the hottest files yourself. Hunt shallowness in its three forms: functions extracted only for testability while the real bugs live in how they are called (no locality); modules leaking across their seams, each reaching into another's internals; and one concept that takes five open files to understand. Code that is hard to test through its interface is a symptom of the same shallowness, not a fourth form.

4. Apply the DELETION TEST to every suspect: would removing this module concentrate complexity behind a smaller interface, or just spread it around? Only "concentrates" earns a card; a "spreads" drops without a line, since a report of move-it-around refactors is generic cleanup advice.

5. Write the report to wherever the repository already keeps this kind of note (an existing `docs/improve-*` or the convention `docs/atlas/map.md` names), else `docs/improve-<yyyy-mm-dd>-<slug>.md`. One card per candidate, strongest first:

```
# Improve: <subject>
next: <the top recommendation> - call `atlasme` with this card

## <candidate, in domain nouns>
files: <the files involved>
friction: <why the current shape hurts, in plain words>
deepening: <what would change, in plain English; the new interface is not designed here>
benefit: <the locality and leverage gained, and how testing through the new interface improves>
strength: strong | worth exploring | speculative
```

6. Ask which card to take further through the host's question tool, shaped by `<plugin root>/skills/scope/references/asking.md` (`<plugin root>` is the parent of the `skills/` directory this file lives in): the recommended card first, one option per card plus stop. On a pick, hand that card to `atlasme` - constraints, dependencies, the shape of the deepened module and what sits behind the seam are its tree to work. On stop, the report stands alone.

7. Print the report path. Never change code and never design the interface here: the deepening lands later through `scope` -> `build`, once `atlasme` has settled the shape.
