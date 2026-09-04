---
name: narrate
description: Turns a diff or pull request into an approval dossier written for the person who approves - verdict first, what changes in plain words, a traffic-light table of what was actually verified at HEAD, what the reviewer still has to check, risks - with commands, evidence and the engineer's reading guide folded into collapsible sections. Use when a PR body is needed, when a reviewer must approve without reading every file, or when a change may break domains it does not touch. Not for finding bugs (review) or shrinking code (simplify).
argument-hint: "[pr-number | pr-url | branch] [--out file] [--post] [--walkthrough] [--no-run] [--lang it|en]"
---

1. Resolve the range. A PR number or URL: `gh pr view <pr> --json number,url,headRefName,baseRefName,headRefOid,mergeable`, then `git fetch origin +refs/heads/<base>:refs/remotes/origin/<base> +refs/pull/<n>/head:refs/remotes/origin/pr/<n>`; the range is `merge-base(origin/<base>, origin/pr/<n>)..origin/pr/<n>`. A branch or nothing: the current branch against the merge-base with the default branch. Record `OWNER/REPO`, `<n>`, `BASE`, `HEAD`, `mergeable`.

2. Pick the audience and the language before writing anything. The reader is the person who approves, who may not know this code: sentences under 20 words, no file path, command or count in the first screen, every acronym expanded once. Language: `--lang`, else the language of the repository's recent PR descriptions and commit messages (Italian on the Coesia side).

3. Partition: `python3 ${CLAUDE_SKILL_DIR}/scripts/pr-partition.py -C <repo> BASE HEAD` (the `scripts/` folder beside this file). Its table feeds the size line; the judgment list is the only code you read.

4. Blast radius, mechanical: affected projects from the workspace tool (`nx show projects --affected --base=BASE --head=HEAD`; turbo/bazel/`go list`/solution references elsewhere) with the pure dependents the diff does not touch marked; `python3 ${CLAUDE_SKILL_DIR}/scripts/pr-contracts.py -C <repo> BASE HEAD` for removed exported symbols with consumers outside the diff and deleted files still referenced (judge each: a test asserting absence is fine, a live import is a break); for every shared contract the diff changes (DTO, schema, event, endpoint, config key, bus message) name the consumers at HEAD with `git grep -w` and whether they absorb it.

5. Verify, executed. Worktree at HEAD (`git worktree add --detach <path> HEAD`); run the repository's own test target for every affected project and build or typecheck for every pure dependent, mirroring CI's command; long suites in the background with JUnit/TRX output, summarised by `python3 ${CLAUDE_SKILL_DIR}/scripts/test-summary.py <files>`. Every failure is attributed by running the same target on the merge-base in a second worktree: identical failing set means pre-existing, a new name means the PR. Record pass / fail / pre-existing / environment / blocked / not run. `--no-run` skips this step and the table says "nothing executed". Never list a command you did not run.

6. Read the judgment bucket, entry points first. Up to 25 files: read the diffs yourself. More: dispatch one `sniper-scout` per directory in one message (Codex: `sniper_scout`; no agents: read the top files by churn) asking "what does each file do now, and why did it change", and read only their `path:line` lines.

7. Write the dossier in this order and shape. First screen (verdict, plain words, table, checklist) fits in 40 lines; everything technical goes inside `<details>` blocks, which GitHub, GitLab and Azure DevOps render collapsed:

```
<!-- sniper:narrate -->
## Verdetto: <mergeable | non mergeabile oggi | mergeabile con condizioni>
<one sentence with the single blocking reason and the fix, or "nothing blocks it">

## Cosa cambia, in parole semplici
- <3-6 bullets: what the user or operator gets, what disappears, what stays untouched; no file names>

## Cosa è stato verificato
| Area | Esito | In breve |
|---|---|---|
| <suite or area in plain words> | ✅ / ⚠️ pre-esistente / ⚠️ ambiente / ❌ bloccato / ⏸ non eseguito | <one sentence, numbers only as "N test verdi"> |

## Impatto sugli altri domini
- <projects reached but not touched, and the proof they still build and pass>
- <public contracts removed or changed, and who uses them: "nessuno" or the absorbing consumer>

## Cosa devi ancora controllare tu
- [ ] <one line each, only what no test here could cover; say what to do, not why>

## Rischi residui
1. <plain-language consequence for users> - <covered by: verified line | left to the checklist>

<details><summary>Come è stato verificato: comandi, numeri, attribuzione</summary>
<one line per command as run: result, counts, base comparison, worktree paths, range>
</details>

<details><summary>Guida di lettura per chi rivede il codice</summary>
Read in this order (<= 25 `path - what it does now, why it changed`), at most two shape views, decisions with the rejected alternative and `path:line`, follow-ups.
</details>
```

8. Rules for the first screen: the table has one row per suite or area, not per command; ⚠️ pre-esistente means the same failures exist on the base branch; ⚠️ ambiente means the failure is the machine, not the code; ❌ bloccato means the PR itself prevents the check; ⏸ non eseguito means nobody ran it. The checklist contains only what a human must do because no test here can. Risks name a consequence, not a mechanism.

9. Decisions inside the reading guide: three to seven, each with the alternative rejected, why, and `path:line`. No rejected alternative, no entry.

10. `--out <file>` writes the dossier, otherwise print it. `--post`: show it, then only after the user confirms in this session replace the PR body: `gh pr edit <n> -R OWNER/REPO --body-file <file>`; a body without the `<!-- sniper:narrate -->` marker is the author's text, say so and ask before overwriting. `--walkthrough`: write `comments.json` (one entry per decision: `path`, `line`, `body` of at most three lines saying why), run `python3 ${CLAUDE_SKILL_DIR}/scripts/pr-walkthrough.py OWNER/REPO <n> comments.json -C <repo>` to validate and show the payload (`-C` reads the diff locally; `gh pr diff` refuses PRs above 300 files), then only after the user confirms add `--post`.

Stop when the dossier is printed or written and any confirmed post has run. Do not review for defects, do not edit code, and do not narrate files outside the judgment bucket.
