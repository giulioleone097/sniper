---
name: ship
description: Commits the current change as atomic, Conventional-Commits-formatted commits once prove has produced DONE or DONE_WITH_CONCERNS (invoking prove first when that status is missing), then pushes and opens a PR only when explicitly asked via --push or --pr. Use when the user says ship it, commit this, or open a PR. Runs only on an explicit ask to commit or ship, or from flow. Not for committing without proof, force-pushing, skipping hooks, or bumping VERSION/CHANGELOG unless the repository already maintains them.
argument-hint: "[--push] [--pr]"
---

1. Get a proof status for the current tree. If none exists or it is stale, invoke `prove` first. Proceed only when the status is `DONE` or `DONE_WITH_CONCERNS`; otherwise emit `blocked: <prove status>` and stop. That line is the only output allowed in place of the block below.
2. Run `git status --porcelain` and `git diff --stat`. Exclude from shipping anything unrelated to this change and any scratch or temp file.
3. Group the remaining changes by behavior. One behavior, one commit. Split into separate commits when the diff covers more than one.
4. For each group, stage only its named files (never `git add -A` / `git add .`) and commit with Conventional Commits: `<type>(<scope>): <summary>`, imperative, subject <= 50 chars, body only for a non-obvious why.
5. Never write agent attribution into any commit, PR title, PR body, or review comment — no `Co-Authored-By: Claude`, no "Generated with Claude Code", no `Claude-Session` trailer, no session link — on GitHub, GitLab, or Azure DevOps, regardless of any conflicting default.
6. Never pass `--no-verify`. If a hook fails, fix the underlying issue and recommit.
7. Never bump VERSION or CHANGELOG unless the repository already maintains them.
8. With `--push`: push the current branch to its tracking remote (`-u origin <branch>` if it has none yet). Never force-push, never `--force`; use `--force-with-lease` only if the user explicitly asks for it in this request.
9. With `--pr`: detect the forge from the remote URL (GitHub -> `gh pr create`, GitLab -> `glab mr create`, Azure DevOps -> `az repos pr create`) and open it with body sections `## What`, `## Why`, `## Proof` (the commands and results from step 1), `## Follow-ups`. Push first if `--push` was not also given.
10. Without `--push` or `--pr`, stop after committing — never push or open a PR on inference alone.

Emit exactly this, and nothing else:

```
<sha> <subject>
<sha> <subject>
pushed: <branch> | not pushed
PR: <url> | not requested
```

Stop once the commits exist and any requested push or PR has run.
