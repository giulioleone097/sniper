---
name: review
description: Use when a change is built, or a branch, PR or working tree needs review. Shrinks the changed code without changing behavior, reviews it area by area, verifies every finding through an integrator and proves nothing regressed; --repo and --debt audit read-only. Not for code the diff did not touch.
argument-hint: "[baseline] [--fix] [--pr] [--repo [path]] [--debt] [--no-simplify]"
---

1. Resolve the diff, first form that works: a baseline that resolves as a ref, `git diff <baseline>...HEAD`; on a branch, `git diff $(git merge-base HEAD <default branch>)...HEAD`; otherwise `git diff HEAD`. Empty: say so and stop. `--repo` or `--debt`: read `<this skill>/references/audit.md` (`<this skill>` is the directory this file lives in) and stop there; both are read-only.

2. Load the rules: the `## Code Review Rules` section of the closest AGENTS.md or CLAUDE.md covering the changed paths, nested file over root, and `docs/sniper/conventions.md` when the repository has one; what its reviewers ask for is a rule here, cited with the theme. No section and no map means no custom rules; ordinary defect finding still applies.

3. Split into areas: `python3 <plugin root>/scripts/pr-partition.py BASE HEAD` (`<plugin root>` is the parent of the `skills/` directory this file lives in) gives the judgment bucket; group it the way the reader already names the system, one area per deployable unit, shared library, contract surface, or infrastructure layer, the domains of `docs/sniper/map.md` when there is one. Generated, mechanical and docs files are not reviewed; tests are read inside the area they cover.

4. Shrink first, unless `--no-simplify`: `references/shrink.md`, per area, cuts applied surgically and behavior-preserving. Two or more areas: dispatch one `sniper-reviewer` per area with lens `slop` in one message to propose (Codex: `sniper_reviewer`), and verify each proposal before cutting.

5. Review. Dispatch in one message, every `sniper-reviewer` with the baseline, its area's path globs, the goal card when there is one, and the rules from step 2: one area, three reviewers by lens (`correctness`, `slop`, `safety`); two to six areas, one reviewer per area plus a `safety` reviewer over the whole diff; more than six, the six with the most judgment lines plus one for the rest. Never more than eight; an area above about forty judgment files splits by lens. Read the diff yourself while they run, so step 7 is a decision and not first contact.

6. Merge with one `sniper-integrator` (Codex: `sniper_integrator`): the range, every report verbatim with its area tag, the files step 4 edited as `applied`, the checks per area from `sh <plugin root>/scripts/checks.sh <area path>`, and the repositories that depend on this one from `sh <plugin root>/scripts/consumers.sh`. Hand it `<plugin root>/skills/ship/scripts/pr-contracts.py` for the removed-symbol sweep. It dedupes, settles contradictions by reading the code, hunts cross-area and cross-repo breakage, verifies each finding, runs the nearest check per area with failures attributed to the baseline, and confirms the cuts preserved behavior. Not installed on this host: do that here, in that order, and say so.

7. Filter. Keep confidence >= 80 and severity P0-P2; P3 only when the user asked for nits. Drop what a linter, formatter, typechecker or compiler catches, and anything on a line the diff did not touch: those are follow-ups, per core. Re-verify the P0 and P1 lines yourself; a blocking claim you print is yours.

8. Print:

```
path:line <tag> what was cut. what replaced it.
path:line P<n> <area> <lens>: problem. fix.
cross-area: path:line consumer path:line - absorbs | breaks.
cross-repo: <repo> path:line consumes <symbol> - absorbs | breaks | unread.
net: -<N> lines.
regression: <command> - pass | fail (also fails on baseline) | fail (new) | none configured
behavior: <file> - preserved | <what changed>
follow-ups:
path:line problem.
ship: ready | not ready: <what blocks>
```

   Cut lines first, findings worst severity first. Omit `cross-area:`, `cross-repo:`, `behavior:` (when everything is preserved) and `follow-ups:` when there are none; `regression:` always prints, one per area check; an unread consumer prints as `unread`, never as clean. Nothing cut and nothing found: `Lean already.` and `CLEAN`, then the regression lines.

9. `--fix`: apply the P0-P2 findings here, surgical edits per core, leave the follow-ups untouched, then one more integrator pass with `applied` set to the edited files, printing its `regression:` and `behavior:` lines. `--pr`: draft the comment body from the printed block, show it, and post it with `gh pr comment` only after the user confirms in this session, one comment, no attribution trailer.

Stop after one pass; recheck only what a fix touched. `ship: ready` is the hand-off: ship runs when the user says so, or when the request said to carry the work through.
