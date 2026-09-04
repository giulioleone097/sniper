---
name: narrate
description: Turns a diff or pull request into an approval dossier for the person who approves - verdict, what changes in plain words, then a drill-down per affected domain or repository that says why it was touched, what the change does, what kind of change it is, who it reaches, and the executed evidence that it holds - followed by what is outside this verification and who covers it. Never hands the approver a checklist. Use when a PR body is needed, when a reviewer must approve without reading every file, or when a change reaches domains it does not touch. Not for finding bugs (review) or shrinking code (simplify).
argument-hint: "[pr-number | pr-url | branch] [--out file] [--post] [--walkthrough] [--no-run] [--lang it|en]"
---

1. Resolve the range. A PR number or URL: `gh pr view <pr> --json number,url,headRefName,baseRefName,headRefOid,mergeable`, then `git fetch origin +refs/heads/<base>:refs/remotes/origin/<base> +refs/pull/<n>/head:refs/remotes/origin/pr/<n>`; range `merge-base(origin/<base>, origin/pr/<n>)..origin/pr/<n>`. A branch or nothing: current branch against the merge-base with the default branch. Record `OWNER/REPO`, `<n>`, `BASE`, `HEAD`, `mergeable`.

2. Audience and language first. The reader approves and may not know this code: sentences under 20 words, acronyms expanded once, no path or command outside the collapsible blocks. Language: `--lang`, else the language of the repository's recent PR descriptions and commits.

3. Partition: `python3 ${CLAUDE_SKILL_DIR}/scripts/pr-partition.py -C <repo> BASE HEAD` (the `scripts/` folder beside this file). The judgment list is the only code you read; group it by domain: one domain per deployable unit, shared library, contract surface, or infrastructure layer the diff touches, plus one per repository or project the diff reaches without touching.

4. Blast radius, mechanical: affected projects from the workspace tool (`nx show projects --affected --base=BASE --head=HEAD`; turbo, bazel, `go list`, solution references elsewhere), pure dependents marked; `python3 ${CLAUDE_SKILL_DIR}/scripts/pr-contracts.py -C <repo> BASE HEAD` for removed exported symbols with consumers outside the diff and deleted files still referenced (judge each hit); for every shared contract the diff changes (DTO, schema, socket event, endpoint, config key, bus message, Helm value) name the consumers at HEAD with `git grep -w` and show the line that absorbs or breaks.

5. Verify, executed. Worktree at HEAD; run the repository's own test target for every affected project and build or typecheck for every pure dependent, mirroring CI; long suites in the background with JUnit/TRX summarised by `python3 ${CLAUDE_SKILL_DIR}/scripts/test-summary.py`. Attribute every failure by running the same target on the merge-base in a second worktree. Then go after what tests do not reach: contract regeneration checks, the container build, a local end-to-end harness if the repository ships one (look for `localstack`, `e2e`, `docker-compose` under the touched projects), a migration dry run against a fixture. Before writing "not verified" for anything, try three routes in order: run the check, find the existing test that covers it and cite it, or show the code path that makes it safe with `path:line`. Only when all three fail does it go to "outside this verification", with the reason and the owner (release runbook, nightly job, the author) - never the approver.

6. Read the judgment bucket per domain, entry points first; above 25 files dispatch one `sniper-scout` per domain in one message (Codex: `sniper_scout`) asking "what does each file do now, why did it change, and what reaches it from outside", and read only their `path:line` lines.

7. Write the dossier. The first screen (verdict, plain-words change list) fits in 25 lines; the drill-down is the body; technical evidence sits in `<details>` blocks that GitHub, GitLab and Azure DevOps render collapsed:

```
<!-- sniper:narrate -->
## Verdetto: <mergeabile | mergeabile con condizioni | non mergeabile oggi>
<the single blocking reason and its fix, owner named; or "nothing blocks it">

## Cosa cambia, in parole semplici
- <3-6 bullets: what the user or operator gets, what disappears, what stays untouched>

## Drill-down per dominio
### <n>. <domain or repository, in plain words> - <✅ | ⚠️ | ❌>
Perché è toccato: <one or two sentences>
Cosa fa la modifica: <two to four sentences, mechanism in plain words>
Tipo di modifica: <behavior | contract | refactor without behavior change | removal | dependency | infrastructure>, <user-visible: yes/no>
Chi raggiunge: <the other domains, repositories, services or clients that consume this, and how each absorbs it>
Prova: <the executed evidence, with counts and base attribution; the existing test names or the code path when no run covers it>
Rischio residuo: <a consequence in plain words, or "nessuno individuato">
<details><summary>Dettaglio tecnico</summary> file-level: path:line per claim, decisions with the rejected alternative </details>

## Fuori dal perimetro di questa verifica
- <what> - <why it could not be verified here> - <who covers it and when: release runbook, nightly job, the author before merge>

## Rischi accettati dall'autore
1. <consequence for users> - <mitigation in place or explicit acceptance, with path:line>

<details><summary>Comandi eseguiti e numeri</summary> one line per command as run: result, counts, base comparison, worktree paths, range, date </details>
<details><summary>Guida di lettura per chi rivede il codice</summary> order (<= 25 `path - what it does now, why it changed`), at most two shape views, follow-ups </details>
```

8. Rules. ✅ means executed evidence passes or the failures are proven pre-existing on the base branch; ⚠️ means evidence exists but a residual risk or an environment gap remains, named; ❌ means the PR itself prevents the check or a new failure is attributed to it. Every "Chi raggiunge" line names a consumer and its proof, never "should be fine". The dossier contains no task for the approver: what the author must fix is in the verdict, what the release process covers is in "Fuori dal perimetro" with its owner. Numbers stay in table cells or "N test verdi" form; the drill-down for a domain is at most 12 lines outside its details block; the whole dossier at most 250 lines.

9. `--out <file>` writes the dossier, otherwise print it. `--post`: show it, then only after the user confirms in this session replace the PR body with `gh pr edit <n> -R OWNER/REPO --body-file <file>`; a body without the `<!-- sniper:narrate -->` marker is the author's text, say so and ask first. `--walkthrough`: write `comments.json` (one entry per decision, `path`, `line`, `body` of at most three lines saying why), run `python3 ${CLAUDE_SKILL_DIR}/scripts/pr-walkthrough.py OWNER/REPO <n> comments.json -C <repo>` to validate and show the payload (`-C` reads the diff locally; `gh pr diff` refuses PRs above 300 files), then only after the user confirms add `--post`.

Stop when the dossier is printed or written and any confirmed post has run. Do not review for defects, do not edit code, and do not narrate files outside the judgment bucket.
