---
name: simplify
description: Use when the user asks to simplify, shrink or de-slop code outside a review, or to audit a tree with --repo, --debt or --rules. Makes the code smaller without changing behavior through six rungs, per area, and proves nothing moved. Not for bugs or new behavior; the loop's review already shrinks what it reviews.
argument-hint: "[baseline | files] [--repo [path]] [--debt] [--rules]"
---

1. Resolve scope. `--repo [path]`, `--debt` or `--rules`: read `<plugin root>/skills/review/references/audit.md` (`<plugin root>` is the parent of the `skills/` directory this file lives in) and stop there. Otherwise the files given; else the task's actual diff: the changes since the named baseline or the branch's merge-base with the default branch, plus the staged, unstaged and new files, so a committed-only range does not hide the work just written. Nothing named and no diff: ask which files through the host's question tool, do not guess.

2. Split into areas when the code spans more than one, grouped the way `docs/sniper/map.md` names the system when there is one; for a committed range `python3 <plugin root>/scripts/pr-partition.py BASE HEAD` gives the judgment bucket. Trace generated changes to their source instead of cutting them.

3. Shrink through `<plugin root>/skills/review/references/shrink.md`. Work locally unless substantial independent areas justify `sniper-reviewer` subagents with lens `slop` (Codex: `sniper_reviewer`), each given `<plugin root>/skills/review/references/slop.md` with the diff.

4. Prove nothing moved with the smallest decisive existing check or real exercise; `sh <plugin root>/scripts/checks.sh <path>` locates commands when needed. Reuse still-valid results. Integrate locally unless several reports have substantial cross-area interactions; then use `sniper-integrator` (Codex: `sniper_integrator`) with the task diff, proposals, applied edits, proof and the `consumers` list or `none`. Sweep consumers only when a changed contract warrants it. Report unavailable proof and attribute failures before calling them regressions.

5. Print one line per cut, tag first:

```
path:line <tag> what was cut. what replaced it.
net: -<N> lines.
regression: <command> - pass | fail (also fails on baseline) | fail (new) | none configured
behavior: <file> - <what changed>
```

   The tag is the rung that held. One `regression:` line per area check that ran. `behavior:` only where a cut changed something; omit it when everything is preserved. Nothing to cut in scope: `Lean already.` then the regression lines, and nothing else; the per-rung reasoning stays out of the report.

Stop when the rungs find nothing left in scope and the proof has run. Do not widen to untouched files, do not hunt smaller wins in a second sweep, and do not invoke `review`: typed by name, this runs alone.
