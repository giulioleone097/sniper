---
name: review
description: Use when a diff needs review and repair, or reviewers left comments on a PR. Verifies and fixes defects within the requested outcome, using local review for bounded changes and subagents when useful. Not for unrelated improvements; explicit read-only requests and repository audits do not edit.
argument-hint: "[baseline] [--fix] [--read-only] [--pr] [--address <pr>] [--repo [path]] [--debt] [--no-simplify]"
---

1. Resolve scope first. `--repo` or `--debt`: read `<this skill>/references/audit.md` (`<this skill>` is the directory this file lives in) and stop there. Otherwise use the task's actual diff: the requested commit/PR range, or the in-scope staged, unstaged and new files, including work just produced by build. Preserve pre-existing edits; do not let a committed-only range hide the changes under review. Clean tree and nothing named: on a branch, `git diff <default branch>...HEAD`. Empty: say so and stop. `--read-only` or an explicit no-edit request applies no cut or fix. Otherwise repair is the default; `--fix` states that same intent explicitly.

2. Load the rules: the `## Code Review Rules` section of the closest AGENTS.md or CLAUDE.md covering the changed paths, nested file over root, the entries under `docs/solutions/` whose symptom or paths match the change (ship's learn step writes them there), and `docs/sniper/conventions.md` when the repository has one; what its reviewers ask for is a rule here, cited with the theme. No section and no map means no custom rules; ordinary defect finding still applies.

3. A bounded change stays local. For a broad committed range, `python3 <plugin root>/scripts/pr-partition.py BASE HEAD` (`<plugin root>` is the parent of the `skills/` directory this file lives in) helps group independent areas. Read tests with their behavior and review instructions or contracts even when stored in Markdown. Trace generated changes to their source; avoid line-by-line review of mechanical output.

4. Shrink within scope, unless `--no-simplify`: read `references/shrink.md` and tag each cut with its rung (`reuse:`, `stdlib:`, `native:`, `delete:`, `yagni:`, `shrink:`); read-only prints each cut as a proposal and its `net:` line as `net: -<N> lines possible.`, as `--repo` does. Apply only cuts that remove complexity introduced or directly exercised by this change while preserving required behavior. Do not widen into adjacent cleanup or remove a useful boundary just because it has one implementation.

5. Cover correctness, unnecessary complexity and safety. Prefer economical `sniper-reviewer` subagents (Codex: `sniper_reviewer`) for independently assignable areas or risks, with the exact diff, area or lens, outcome, exclusions and rules; a `slop` reviewer also gets `references/slop.md`. Require a reachable trigger or violated contract; imagined future uses are not defects.

6. Verify reports against code and dedupe shared causes. Integrate locally unless several reports have substantial cross-area interactions; then use `sniper-integrator` (Codex: `sniper_integrator`) with the exact diff, reports, applied edits, existing proof and the `consumers` list or `none`. Use `sh <plugin root>/scripts/checks.sh <area path>` when commands are unknown. Only changed external contracts justify `sh <plugin root>/scripts/consumers.sh` and `<plugin root>/skills/ship/scripts/pr-contracts.py`; check actual consumers, not hypothetical repositories.

7. Fix verified P0-P2 defects within the requested outcome unless read-only; P3 only when requested. Resolve in-scope compiler or check failures without turning them into review nits. Inspect each repair and verify it with the smallest decisive check.

8. Print:

```
path:line <tag> what was cut. what replaced it.
path:line P<n> <area> <lens>: problem. fixed: <repair> | remaining: <reason>, fix: <proposal>.
cross-area: path:line consumer path:line - absorbs | breaks.
cross-repo: <repo> path:line consumes <symbol> - absorbs | breaks | unread.
net: -<N> lines.
regression: <command> - pass | fail (also fails on baseline) | fail (new) | none configured
behavior: <file> - <what changed>
follow-ups:
path:line problem.
ship: ready | not ready: <what blocks>
```

   Cut lines first, findings worst severity first. `path:line` names the line in the reviewed diff, before repair. Omit `cross-area:`, `cross-repo:`, `behavior:` (when everything is preserved) and `follow-ups:` when there are none; `regression:` always prints, one per area check; an unread consumer prints as `unread`, never as clean. Nothing cut and nothing found: `Lean already.` and `CLEAN`, then the regression lines and the `ship:` line.

9. `--pr`: one thread per verified finding at its line plus one summary, `references/pr.md`. `--address <pr>`: the reviewers' threads answered from the code, same reference; it runs instead of steps 3 to 8.

Stop when in-scope repairs and their proof are complete, or name the concrete blocker. Recheck only what a fix invalidates. `ship: ready` is the hand-off: ship runs only when authorized.
