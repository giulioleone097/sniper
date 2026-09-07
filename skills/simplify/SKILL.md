---
name: simplify
description: Use when the user asks to simplify, shrink or de-slop code outside a review, or to audit a tree with --repo or --debt. Makes the code smaller without changing behavior through six rungs, per area, and proves nothing moved. Not for bugs or new behavior; the loop's review already shrinks what it reviews.
argument-hint: "[baseline | files] [--repo [path]] [--debt]"
---

1. Resolve scope. `--repo [path]` or `--debt`: read `<plugin root>/skills/review/references/audit.md` (`<plugin root>` is the parent of the `skills/` directory this file lives in) and stop there; both are read-only. Otherwise the code named: the files given; else `git diff <baseline>...HEAD` when a baseline was named or the branch has a merge-base; else `git diff HEAD`. Nothing named and no diff: ask which files through the host's question tool, do not guess.

2. Split into areas when the code spans more than one: `python3 <plugin root>/scripts/pr-partition.py BASE HEAD` gives the judgment bucket, grouped the way `docs/sniper/map.md` names the system when there is one. One area, or fewer than about 15 judgment files: do it here.

3. Shrink through `<plugin root>/skills/review/references/shrink.md`, the same rungs the loop's review applies. Two or more areas: dispatch one `sniper-reviewer` per area with lens `slop` in one message to propose (Codex: `sniper_reviewer`; not installed: walk the areas sequentially here), never more than six, and read the largest area yourself while they run. A proposal is a claim: verify the replacement covers the case before cutting.

4. Prove nothing moved. One area edited: run its nearest existing check, `sh <plugin root>/scripts/checks.sh <path>`, and report the exact result. Two or more areas edited, or a cut that crossed a boundary: one `sniper-integrator` pass (Codex: `sniper_integrator`) with the range, the proposals, `applied` set to every file you edited, the checks per area from `checks.sh`, the repositories that depend on this one from `sh <plugin root>/scripts/consumers.sh`, and `<plugin root>/skills/ship/scripts/pr-contracts.py` for the removed-symbol sweep. It attributes a failure to the baseline before calling it new, confirms no guard was thinned and no test weakened, and names any removed symbol something outside the area still consumes. Not installed: do that here, in that order, and say so. No check configured for an area: say that instead of implying one ran.

5. Print one line per cut, tag first:

```
path:line <tag> what was cut. what replaced it.
net: -<N> lines.
regression: <command> - pass | fail (also fails on baseline) | fail (new) | none configured
behavior: <file> - preserved | <what changed>
```

   Tags are the six rungs: `reuse:` `stdlib:` `native:` `delete:` `yagni:` `shrink:`. One `regression:` line per area check that ran; `behavior:` only where the integrator found something other than preserved. Nothing to cut in scope: `Lean already.` alone, then the regression lines.

Stop when the rungs find nothing left in scope and the proof has run. Do not widen to untouched files, do not hunt smaller wins in a second sweep, and do not invoke `review`: typed by name, this runs alone.
