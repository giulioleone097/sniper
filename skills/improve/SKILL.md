---
name: improve
description: Use when improving codebase health beyond one diff through structural deepening, simplification, measured optimization or audit.
argument-hint: "[what to make healthier: a direction, a subsystem or a planned change]"
---

1. Classify the ask, then run exactly one branch. A shrinking or de-slop ask invokes `simplify` on what the user named (Skill tool `atlas:simplify`, `$simplify` on Codex). A measured-number ask - latency, size, cost, a score - invokes `optimize` the same way (Skill tool `atlas:optimize`, `$optimize` on Codex). An audit ask invokes `review` in the mode it names: a slop report or repo health `review --repo`, debt `review --debt`, repo rules `review --rules` (Skill tool `atlas:review`, `$review` on Codex). A structural ask - "how could this be easier to change", "what shape is it in", "how can we make <planned change> easy" - is this skill's own job: read `<this skill>/references/deepen.md` (`<this skill>` is the directory this file lives in) and run the survey. An ask that fits several branches or none: ask one question through the host's question tool, the classes as options with the recommendation first, contract in `<plugin root>/skills/scope/references/asking.md` (`<plugin root>` is the parent of the `skills/` directory this file lives in), then follow the answer.

2. A dispatch ends there: the invoked skill owns its report. A survey ends as deepen.md directs: report written, then the picked card handed to `atlasme` (Skill tool `atlas:atlasme`, `$atlasme` on Codex). Either way print:

```
dispatch: <the ask in a few words> -> simplify | optimize | review --repo | --debt | --rules | deepen survey - <the signal that decided it>
report: <path - survey only>
card: <the pick> -> atlasme | none picked - <survey only>
```

Stop when the one dispatch has run or the survey report is printed and its pick handed to `atlasme`. One dispatch or one survey per run, and never an edit: the deepening a card names lands later through `scope` -> `build`.
