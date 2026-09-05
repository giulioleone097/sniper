---
name: review
description: Use when a change, branch, PR or working tree needs review, or right after a build slice. One reviewer per area or lens, then an integrator that merges, settles contradictions, catches cross-area and cross-repo breakage, verifies each finding and runs the nearest checks. Not for code the diff did not touch.
argument-hint: "[baseline] [--fix] [--pr]"
---

1. Resolve the diff, first form that works:
   - a baseline argument that resolves as a ref: `git diff <baseline>...HEAD`
   - on a branch: `git diff $(git merge-base HEAD <default branch>)...HEAD`
   - otherwise: `git diff HEAD`

   Confirm the diff is non-empty before spending an agent on it. Empty diff: say so and stop.

2. Load the `## Code Review Rules` section from the closest AGENTS.md or CLAUDE.md covering the changed paths, nested file over root, and `docs/sniper/conventions.md` when the repository has one: what its reviewers ask for is a rule here, cited with the theme. No section and no map means no custom rules; ordinary defect finding still applies.

3. Split into areas. `python3 <plugin root>/scripts/pr-partition.py BASE HEAD` (`<plugin root>` is the parent of the `skills/` directory this file lives in) gives the judgment bucket; group it the way the reader already names the system - one area per deployable unit, shared library, contract surface, or infrastructure layer. Generated, mechanical and docs files are not reviewed; tests are read inside the area they cover.

4. Dispatch, all in one message, per the table. Every `sniper-reviewer` gets the baseline, the exact path globs of its area, the goal card when the session has one, and the rules from step 2 (Codex: `sniper_reviewer`; not installed: run the lenses sequentially here with `agents/sniper-reviewer.md` as the brief).

   | Diff | Dispatch |
   |---|---|
   | one area | three reviewers, one per lens: `correctness`, `slop`, `safety` |
   | two to six areas | one reviewer per area, all three lenses, plus a fourth lens-`safety` reviewer over the whole diff |
   | more than six areas | one reviewer per area for the six areas with the most judgment lines, one reviewer for the remainder together, same safety sweep |

   Never more than eight in one pass. An area larger than about 40 judgment files splits by lens instead, and its reviewers say which lens they hold.

5. Read the diff yourself while they run, entry points first, so step 7 is a decision and not first contact.

6. Merge with one `sniper-integrator` (Codex: `sniper_integrator`): pass the range, every area report verbatim with its area tag, the empty `applied` list, the checks the repository uses for the affected areas (`sh <plugin root>/scripts/checks.sh <area path>` per area), and the repositories that depend on this one (`sh <plugin root>/scripts/consumers.sh`: sibling checkouts and workspace members whose manifests name this repo). Hand it `<plugin root>/skills/narrate/scripts/pr-contracts.py` for the removed-symbol sweep. It dedupes, settles contradictions by reading the code, hunts the cross-area breakages no single reviewer could see, verifies each finding, and runs the nearest check per affected area with failures attributed to the baseline. Not installed on this host: do that merge and that verification here, in this order, and say you did.

7. Filter what the integrator returns. Keep confidence >= 80 and severity P0-P2; keep P3 only when the user asked for nits. Drop anything a linter, formatter, typechecker, or compiler catches, and anything on a line the diff did not touch: those move to the follow-ups list, per core. Slop findings keep their tag - `reuse:` `stdlib:` `native:` `delete:` `yagni:` `shrink:` - the same six rungs `simplify` uses. Re-verify the P0 and P1 lines yourself; a blocking claim you print is yours.

8. Print the surviving findings, worst severity first:

```
path:line P<n> <area> <lens>: problem. fix.
cross-area: path:line consumer path:line - absorbs | breaks.
cross-repo: <repo> path:line consumes <symbol> - absorbs | breaks | unread.
net: -<N> lines possible.
regression: <command> - pass | fail (also fails on baseline) | fail (new) | none configured
follow-ups:
path:line problem.
```

   The `net:` line comes from the slop lens; omit it when that lens found nothing to cut. Omit `cross-area:`, `cross-repo:` and `follow-ups:` when there are none; a consumer repository that exists but could not be read prints as `unread`, never as clean. The `regression:` lines always print, one per area check that ran. Nothing survives the filter and every check passes: print `CLEAN` and the regression lines.

9. `--fix`: apply the P0-P2 findings here, surgical edits per core - not by handing each one to `build`. Leave the follow-ups untouched. Then one `sniper-integrator` pass with `applied` set to the edited files: it re-runs the checks for the touched areas, attributes any failure, and confirms each hunk preserved behavior - no guard thinned, no test weakened or skipped, no silent fallback added. Print its `regression:` and `behavior:` lines under the findings. Findings you did not fix stay printed as they were.

10. `--pr`: draft the comment body from the printed block, show it, and post it with `gh pr comment` only after the user confirms in this session. One comment, no attribution trailer.

11. Stop after one pass. Recheck only what a fix touched; never add a pass to raise confidence in findings already printed.
