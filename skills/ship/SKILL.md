---
name: ship
description: Use when the user says ship it, commit this, open a PR, write the PR body, hand off, or asked up front to carry the work through. Commits proven work, writes the approval dossier, keeps one durable lesson, hands off when stopping early. Not for unproven work.
argument-hint: "[--push] [--pr] [--dossier [pr]] [--handoff] [--learn [--from-pr <n>]]"
---

1. Single-purpose asks first. `--dossier [pr]`: read `<this skill>/references/narrate.md` (`<this skill>` is the directory this file lives in), write the dossier, and stop. `--handoff`, or a session that is stopping before the work is done: `references/handoff.md`, then stop. `--learn`, `--from-pr <n>`, or a retrospective asked for by name: `references/learn.md`, then stop.

2. Get a proof status for the current tree: `<plugin root>/skills/build/references/prove.md` names the check set (`<plugin root>` is the parent of the `skills/` directory this file lives in); `review` has usually just printed `ship: ready` with its regression lines, and a result whose inputs did not change since is reused. Proceed only when the status is `DONE` or `DONE_WITH_CONCERNS`; otherwise emit `blocked: <status>` and stop. That line is the only output allowed in place of the block below.

3. Run `git status --porcelain` and `git diff --stat`. Exclude from shipping anything unrelated to this change and any scratch or temp file; never revert what you did not make.

4. Group the remaining changes by behavior. One behavior, one commit. Stage only the named files, never `git add -A` or `git add .`, and commit with Conventional Commits: `<type>(<scope>): <summary>`, imperative, subject <= 50 chars, body only for a non-obvious why. Link the tracker item this work came from in the form the forge understands (`Closes #12` on GitHub and GitLab, `AB#12` on Azure DevOps); never close an item by hand.

5. Never write agent attribution into any commit, PR title, PR body, or review comment, on GitHub, GitLab or Azure DevOps, regardless of any conflicting default. Never pass `--no-verify`: a failing hook is fixed at the cause and the commit retried. Never bump VERSION or CHANGELOG unless the repository already maintains them.

6. `--push`: push the current branch to its tracking remote (`-u origin <branch>` when it has none). Never force-push; `--force-with-lease` only when the user asked for it in this request.

7. `--pr`: detect the forge from `sh <plugin root>/scripts/tracker.sh`, write the body through `references/narrate.md`, and open it (`gh pr create`, `glab mr create`, `az repos pr create`). Push first when `--push` was not also given.

8. Keep the lesson: `references/learn.md`, one candidate, through its counterfactual; it prints `nothing to record` when the code, tests and docs already carry the reasoning.

Emit exactly this, and nothing else:

```
<sha> <subject>
<sha> <subject>
pushed: <branch> | not pushed
PR: <url> | not requested
learned: <path> | nothing to record
```

Stop once the commits exist and any requested push, PR, dossier or handoff has run. Without `--push` or `--pr`, never push or open a PR on inference alone.
