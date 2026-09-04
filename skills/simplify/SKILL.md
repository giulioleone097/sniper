---
name: simplify
description: Makes the changed code smaller without changing behavior - reuse what already exists, use the stdlib or platform, delete dead flexibility, shrink - area by area when the change spans several, then one integrator that proves no behavior moved. Use when a slice is built and before review, or with --repo to audit a whole tree read-only, ranked by git hot spots. Not for fixing bugs or adding behavior; build and debug own that.
argument-hint: "[baseline | files] [--repo [path]]"
---

1. Resolve scope. `--repo [path]` means the read-only audit: go to step 7. Otherwise the changed code: `git diff <baseline>...HEAD` when the caller named a baseline or the branch has a merge-base, else `git diff HEAD`. No diff and no files named: ask which files, do not guess.

2. Split into areas when the change spans more than one: `python3 <plugin root>/scripts/pr-partition.py BASE HEAD` (`<plugin root>` is the parent of the `skills/` directory this file lives in) for the judgment bucket, grouped per deployable unit, shared library, or contract surface. One area, or fewer than about 15 judgment files: skip to step 4 and do it here.

3. Two or more areas: dispatch one `sniper-reviewer` per area in one message, lens `slop`, with the area's path globs (Codex: `sniper_reviewer`; not installed: walk the areas sequentially here). They propose, tagged and ranked; they never edit. Never more than six in one pass. Read the largest area yourself while they run.

4. Read the changed code and trace the flow it touches end to end before cutting anything, per core. The ladder shortens the solution, never the reading.

5. Walk the checklist per hunk in order, stop at the first rung that holds. Each rung is one output tag:

   1. `reuse:` a helper, type, or pattern already in this repo does it. Call that instead.
   2. `stdlib:` the standard library or an already-installed dependency does it. Name it and use it.
   3. `native:` a platform feature or a database constraint does it. Name it and use it.
   4. `delete:` dead code, an unused flag, config nobody sets. Remove it and the tests that exist only for it.
   5. `yagni:` an abstraction with one implementation, a wrapper that only delegates, a layer with one caller, or anything else on the never-add list, per core. Collapse it into its one caller.
   6. `shrink:` same logic, fewer lines. Rename or flatten only where it lowers the cost of reading that function, never as a sweep across the diff.

   Apply the edits directly, surgical and behavior-preserving. A proposal from step 3 is a claim: verify the replacement really covers the case before cutting. Skip any cut whose behavior preservation you cannot establish, and never thin the guards core lists as never-remove. Boring over clever: a shorter line that takes longer to read is not a win.

6. Prove nothing moved. One area edited: run its nearest existing check (`sh <plugin root>/scripts/checks.sh <path>`) and report the exact result. Two or more areas edited, or a cut that crossed a boundary: one `sniper-integrator` pass (Codex: `sniper_integrator`) with the range, the per-area proposals, `applied` set to every file you edited, and the checks for those areas from `sh <plugin root>/scripts/checks.sh <area path>`. It runs each check, attributes a failure to the baseline before calling it new, confirms no guard was thinned and no test weakened, skipped or deleted, and names any exported symbol a cut removed that something outside the area still consumes. Not installed: do that here, in that order, and say you did. No check configured for an area: say that instead of implying one ran.

7. `--repo [path]`: read-only audit of the tree, applying nothing. Rank attention by hot spots first, so the files that keep changing get read first:

   `git log --oneline -n 300 --name-only --pretty=format: | sort | uniq -c | sort -rn | head -30`

   Then hunt the same six rungs across those files, biggest cut first.

8. Print one line per finding, tag first:

```
path:line <tag> what was cut. what replaced it.
net: -<N> lines.
regression: <command> - pass | fail (also fails on baseline) | fail (new) | none configured
behavior: <file> - preserved | <what changed>
```

   Tags are the six rung names: `reuse:` `stdlib:` `native:` `delete:` `yagni:` `shrink:`. Print one `regression:` line per area check that ran, and a `behavior:` line only where the integrator found something other than preserved. `--repo` prints the same finding lines ranked biggest cut first, ends at `net: -<N> lines possible.`, and has neither line because it changed nothing. Nothing to cut in scope: print `Lean already.` alone.

9. Stop when the checklist finds nothing left in scope and the proof has run. Do not widen to untouched files, and do not run a second sweep hunting smaller wins.
