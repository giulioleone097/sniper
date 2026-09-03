---
name: review
description: Reviews the exact diff through three parallel lenses (correctness, over-engineering, silent-failure safety), verifies each finding against the code, and prints one line per surviving issue. Use when the user asks to review a change, branch, PR, or working tree, or right after a build slice lands. Not for auditing code the diff did not touch; simplify --repo does that.
argument-hint: "[baseline] [--fix] [--pr]"
---

1. Resolve the diff, first form that works:
   - a baseline argument that resolves as a ref: `git diff <baseline>...HEAD`
   - on a branch: `git diff $(git merge-base HEAD <default branch>)...HEAD`
   - otherwise: `git diff HEAD`

   Confirm the diff is non-empty before spending an agent on it. Empty diff: say so and stop.

2. Load the `## Code Review Rules` section from the closest AGENTS.md or CLAUDE.md covering the changed paths, nested file over root. No section means no custom rules; ordinary defect finding still applies.

3. Launch three `sniper-reviewer` Agent calls in one message, one per lens: `correctness`, `slop`, `safety`. Give each the baseline, its lens, the goal card when the session has one, and the rules from step 2. Keep working while they run: read the diff yourself so step 6 is verification and not first contact. On Codex spawn three `sniper_reviewer` custom agents the same way (installed by `scripts/install-codex-agents.sh`); when they are not installed, run the three lenses sequentially in this session with `agents/sniper-reviewer.md` as the brief for each.

4. Filter what comes back. Keep confidence >= 80 and severity P0-P2; keep P3 only when the user asked for nits. Drop anything a linter, formatter, typechecker, or compiler catches, and anything on a line the diff did not touch: those move to the follow-ups list, per core.

   Slop findings arrive tagged `reuse:` `stdlib:` `native:` `delete:` `yagni:` `shrink:` — the same six rungs `simplify` uses. Keep the tag in the problem clause.

5. Dedupe. Two lenses reporting the same defect at the same location is one line; keep the phrasing that names the fix most exactly, and keep the higher severity.

6. Verify every surviving finding against the code before printing it. Read the lines, follow the caller, check the claim. Drop the ones the code disproves and say nothing about them. A reviewer's confidence is its own estimate, not evidence.

7. Print the surviving findings, worst severity first:

```
path:line P<n> <lens>: problem. fix.
net: -<N> lines possible.
follow-ups:
path:line problem.
```

   The `net:` line comes from the slop lens; omit it when that lens found nothing to cut. Omit the `follow-ups:` block when there are none. Nothing survives the filter: print `CLEAN` alone.

8. `--fix`: apply the P0-P2 findings here, surgical edits per core — not by handing each one to `build`. Leave the follow-ups untouched. Run the nearest existing check once when the edits are done and report its exact result. Then re-review only the files the fixes touched, one pass, same three lenses. Findings you did not fix stay printed as they were.

9. `--pr`: draft the comment body from the printed block, show it, and post it with `gh pr comment` only after the user confirms in this session. One comment, no attribution trailer.

10. Stop after one pass. Recheck only what a fix touched; never add a pass to raise confidence in findings already printed.
