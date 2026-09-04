---
name: narrate
description: Turns a diff or pull request into an approval dossier - executed evidence first (which suites ran at HEAD and what they returned), the blast radius across other domains (affected projects, removed contracts and their consumers, deleted modules), an explicit "not verified" list, then the reading guide (order, shape, decisions with rejected alternatives, walkthrough comments). Use when a PR body is needed, when a reviewer must approve without reading every file, or when a change may break domains it does not touch. Not for finding bugs (review) or shrinking code (simplify).
argument-hint: "[pr-number | pr-url | branch] [--out file] [--post] [--walkthrough] [--no-run]"
---

1. Resolve the range. A PR number or URL: `gh pr view <pr> --json number,url,headRefName,baseRefName,headRefOid`, then `git fetch origin +refs/heads/<base>:refs/remotes/origin/<base> +refs/pull/<n>/head:refs/remotes/origin/pr/<n>`; the range is `merge-base(origin/<base>, origin/pr/<n>)..origin/pr/<n>`. A branch or nothing: the current branch against the merge-base with the default branch. Record `OWNER/REPO`, `<n>`, `BASE`, `HEAD`, and the PR's `mergeable` state.

2. Partition before reading anything: `python3 ${CLAUDE_SKILL_DIR}/scripts/pr-partition.py -C <repo> BASE HEAD` (the `scripts/` folder beside this file). Its table is the `Size` line; the judgment list is the only code you read.

3. Blast radius, mechanical, before any judgment:
   - Affected projects from the workspace tool: `nx show projects --affected --base=BASE --head=HEAD` (turbo/bazel/`go list`/solution references elsewhere). Mark the ones the diff does not touch: those are pure dependents and each needs its own verified line in step 4.
   - `python3 ${CLAUDE_SKILL_DIR}/scripts/pr-contracts.py -C <repo> BASE HEAD`: exported symbols the diff removes with consumers outside the diff, and deleted files still referenced outside it. Judge each hit: a test asserting absence is fine, a live import is a break.
   - For every contract shared across domains that the diff changes (DTO, schema, socket event, endpoint, config key, bus message), name the consumers at HEAD with `git grep -w`, and whether the diff updated them or they absorb the change (show the line).

4. Verify, executed. Create a clean worktree at HEAD (`git worktree add --detach <path> HEAD`), then run the repository's own test target for every affected project, and build or typecheck for every pure dependent, mirroring CI's command (read the target in `project.json`, `package.json`, the CI workflow). Run long suites in the background and collect JUnit/TRX files; summarise with `python3 ${CLAUDE_SKILL_DIR}/scripts/test-summary.py <files>`. Record each command exactly as run with pass (count), FAIL (first failures), unavailable (missing env, secrets, time) or blocked. Reuse `prove` results only when they were produced on this HEAD. `--no-run` skips this step and the dossier says so in `Verified: nothing executed`. Never list a command you did not run.

5. Read the judgment bucket, entry points first: routes, handlers, CLI commands, public APIs, schema or contract files, then the flow inward. Up to 25 judgment files: read their diffs yourself. More than 25: dispatch one `sniper-scout` per directory in one message (Codex: `sniper_scout`; no agents: read the top files by churn) with the file list and the question "what does each file do now, and why did it change", and read only the `path:line` lines they return. Never read the whole diff top to bottom.

6. Reading order: at most 25 numbered entries, `path - what it does now, why it changed`, starting where a reviewer should start; above 25, list the files that carry the design and roll the rest up as `<dir> (N files): <one line>`.

7. At most two shape views, the smallest that make the change legible: pseudocode of the new control flow, a call tree of the main path, a shallow file tree of responsibilities, a Mermaid sequence only when the main path crosses three or more components, a before/after `diff` block for the key contract. Concrete names only.

8. Decision log: three to seven decisions a reviewer could disagree with, each with the alternative rejected, why, and `path:line`. No rejected alternative, no entry.

9. Risks: each one either points at the Verified line that covers it, or goes under Not verified with what a human would have to do. A risk with neither is not allowed.

10. Emit the dossier. Hard cap 150 lines, no section restating another, no adjectives about quality. `--out <file>` writes it, otherwise print it:

```
<!-- sniper:narrate -->
# <outcome in one sentence>
Range: <base>..<head> | Size: judgment +A/-D in F files | tests +A/-D | mechanical N | generated N | docs N | config N | mergeable: <state>

## Verified
<command as run> -> pass (N tests) | FAIL: <first failures> | unavailable: <why> | blocked: <why>

## Blast radius
affected projects: N (touched: ...; pure dependents: ... each -> its Verified line)
removed contracts: <symbol> (from <file>) -> consumers outside diff: 0 | <files>
deleted modules: <path> -> residual references: 0 | <files, judged>
shared contracts changed: <contract> -> <consumer:line absorbs | updated in diff | BREAK>

## Not verified
- <what> - <why> - <what a human must do>

## Read in this order
1. <path> - <what it does now, why it changed>

## Shape
<one or two views>

## Decisions
- <decision>. Rejected: <alternative>. Why: <reason>. (<path:line>)

## Risks
- <risk> -> Verified: <command> | Not verified: <see above>

## Follow-ups
- <adjacent finding left untouched, or none>
```

11. `--post`: show the dossier, then only after the user confirms in this session replace the PR body: `gh pr edit <n> -R OWNER/REPO --body-file <file>`. A body without the `<!-- sniper:narrate -->` marker is the author's text: say so and ask before overwriting it.

12. `--walkthrough`: write `comments.json` with one entry per decision (`path`, `line`, `body` of at most three lines saying why), run `python3 ${CLAUDE_SKILL_DIR}/scripts/pr-walkthrough.py OWNER/REPO <n> comments.json -C <repo>` to validate and show the payload (`-C` reads the diff locally; `gh pr diff` refuses PRs above 300 files), then only after the user confirms add `--post`. One review per run.

Stop when the dossier is printed or written and any confirmed post has run. Do not review for defects, do not edit product code, and do not narrate files outside the judgment bucket.
