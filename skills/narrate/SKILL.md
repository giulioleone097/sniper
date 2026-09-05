---
name: narrate
description: Use when a PR needs a body or a reviewer must approve without reading every file. Writes the approval dossier: verdict, plain-words changes, a map, then per domain the before/after shape, boundaries crossed with their consumers, decisions with rejected alternatives, executed evidence. Not for finding bugs.
argument-hint: "[pr-number | pr-url | branch] [--out file] [--post] [--walkthrough] [--no-run] [--lang it|en]"
---

1. Resolve the range. A PR number or URL: `gh pr view <pr> --json number,url,headRefName,baseRefName,headRefOid,mergeable`, then `git fetch origin +refs/heads/<base>:refs/remotes/origin/<base> +refs/pull/<n>/head:refs/remotes/origin/pr/<n>`; range `merge-base(origin/<base>, origin/pr/<n>)..origin/pr/<n>`. A branch or nothing: current branch against the merge-base with the default branch. Record `OWNER/REPO`, `<n>`, `BASE`, `HEAD`, `mergeable`.

2. Audience and language first. The reader approves and may not know this code: one idea per sentence, in words they would use, acronyms expanded once, no path or command in the prose - paths belong in the shapes, the boundary lines and the collapsible blocks. Language: `--lang`, else the language of the repository's recent PR descriptions and commits.

3. Partition: `python3 <plugin root>/scripts/pr-partition.py -C <repo> BASE HEAD`. Paths: `<plugin root>` is the parent of the `skills/` directory this file lives in; `scripts/` beside this file holds `pr-contracts.py`, `pr-walkthrough.py` and `test-summary.py`. The judgment list is the only code you read; group it into domains the reader already has a name for: one per deployable unit, shared library, contract surface, or infrastructure layer, plus one per repository or project the diff reaches without touching. Domains are the reader's mental model, never the folder tree.

4. Blast radius, mechanical: affected projects from the workspace tool (`nx show projects --affected --base=BASE --head=HEAD`; turbo, bazel, `go list`, solution references elsewhere), pure dependents marked; `python3 <this skill>/scripts/pr-contracts.py -C <repo> BASE HEAD` for removed exported symbols with consumers outside the diff and deleted files still referenced (judge each hit); for every shared contract the diff changes (DTO, schema, socket event, endpoint, config key, bus message, Helm value) name the consumers at HEAD with `git grep -w` and record the line that absorbs or breaks - that line is what the drill-down cites, not "should be fine". Then outside the repository: `sh <plugin root>/scripts/consumers.sh` names the sibling checkouts and workspace members that depend on this one; each gets the same `git grep -w` for the changed contracts and its own domain in the drill-down when it is reached, marked unread when it could not be read.

5. Verify, executed. Worktree at HEAD; run the repository's own test target for every affected project and build or typecheck for every pure dependent, mirroring CI; long suites in the background with JUnit/TRX summarised by `python3 <this skill>/scripts/test-summary.py`. Attribute every failure by running the same target on the merge-base in a second worktree. Then go after what tests do not reach: contract regeneration checks, the container build, a local end-to-end harness if the repository ships one (look for `localstack`, `e2e`, `docker-compose` under the touched projects), a migration dry run against a fixture. Before writing "not verified" for anything, try three routes in order: run the check, find the existing test that covers it and cite it, or show the code path that makes it safe with `path:line`. Only when all three fail does it go to "outside this verification", with the reason and the owner (release runbook, nightly job, the author) - never the approver.

6. Read the judgment bucket per domain, entry points first; above 25 files dispatch one `sniper-scout` per domain in one message (Codex: `sniper_scout`) asking "what does each file do now, why did it change, what reaches it from outside, and what did NOT change around it", and read only their `path:line` lines. Every domain needs its before/after shape and its boundary list, so a scout that returns prose without call sites gets one follow-up, then you read the entry points yourself.

7. Draw before you write, twice per domain. Read `<this skill>/references/shapes.md`. One map for the whole change; then, for every domain, its **own** map - that domain's pieces plus the neighbours it touches on either side, the ones that did not change included, with the edge this domain exists to serve marked - **and** a before/after shape of the mechanism inside it. The domain map answers "where does this sit and who does it talk to", the shape answers "what runs differently now". A domain with neither is not narrated, it is summarised.

8. Write the dossier. The first screen (verdict, plain-words list, map) fits in 30 lines; the drill-down is the body and is where the depth goes; file-level evidence sits in `<details>` blocks that GitHub, GitLab and Azure DevOps render collapsed:

```
<!-- sniper:narrate -->
## Verdetto: <mergeabile | mergeabile con condizioni | non mergeabile oggi>
<the single blocking reason and its fix, owner named; or "nothing blocks it">

## Cosa cambia, in parole semplici
- <3-6 bullets: what the user or operator gets, what disappears, what stays untouched>

## Mappa del cambiamento
<one map, lanes = runtimes or tiers, changed and unchanged nodes, the hero edge marked>

## Drill-down per dominio
### <n>. <domain, in plain words> - <✅ | ⚠️ | ❌>
**Perché è toccato** <one or two sentences: the pressure that forced this domain open>
**Dove sta** <this domain's own map: its pieces, the neighbours on both sides, unchanged ones included, the edge it exists to serve marked>
**Cosa fa la modifica** <three to five sentences: the mechanism, in plain words, in the order it runs>
**Com'era, com'è** <the before/after shape: a diff of the control flow, the call tree, the file tree or the component tree>
**Confini attraversati** <one line per boundary: what leaves this domain, who consumes it at HEAD, and the line that absorbs it or the test that pins it. Unchanged consumers count.>
**Decisioni** <one line per decision: what was chosen, the alternative rejected, and the reason - measured, not asserted>
**Prova** <the executed evidence: what ran, the counts, the base attribution, the named test that pins each headline behavior; the code path when no run covers it>
**Rischio residuo** <a consequence in plain words, or "nessuno individuato">
**Peso** <files changed, added, deleted, lines in and out - so the reader knows how much of the diff this domain is>
<details><summary>Dettaglio tecnico</summary> file-level: path:line per claim, what each entry point does now, what was deleted and why nothing calls it </details>

## Fuori dal perimetro di questa verifica
- <what> - <why it could not be verified here> - <who covers it and when: release runbook, nightly job, the author before merge>

## Rischi accettati dall'autore
1. <consequence for users> - <mitigation in place or explicit acceptance, with path:line>

<details><summary>Comandi eseguiti e numeri</summary> one line per command as run: result, counts, base comparison, worktree paths, range, date </details>
<details><summary>Guida di lettura per chi rivede il codice</summary> order (<= 25 `path - what it does now, why it changed`), follow-ups </details>
```

9. Rules. ✅ means executed evidence passes or the failures are proven pre-existing on the base branch; ⚠️ means evidence exists but a residual risk or an environment gap remains, named; ❌ means the PR itself prevents the check or a new failure is attributed to it. Every "Confini attraversati" line names a consumer and its proof. Every "Decisioni" line names the rejected alternative; a decision without one is a description, cut it. The dossier contains no task for the approver: what the author must fix is in the verdict, what the release process covers is in "Fuori dal perimetro" with its owner. This is comprehension, not review: no bug list, no severity table, no security findings - `review` owns those. Numbers stay in the evidence lines, the weight line or "N test verdi" form. A domain gets at most 45 lines outside its details block, its map at most 10 nodes and its shape at most 16; the whole dossier at most 900. A domain that cannot fill those lines with mechanism, boundaries and named evidence is two domains merged, or one that did not need narrating.

10. `--out <file>` writes the dossier, otherwise print it. `--post`: show it, then only after the user confirms in this session replace the PR body with `gh pr edit <n> -R OWNER/REPO --body-file <file>`; a body without the `<!-- sniper:narrate -->` marker is the author's text, say so and ask first. `--walkthrough`: write `comments.json` (one entry per decision, `path`, `line`, `body` of at most three lines saying why), run `python3 <this skill>/scripts/pr-walkthrough.py OWNER/REPO <n> comments.json -C <repo>` to validate and show the payload (`-C` reads the diff locally; `gh pr diff` refuses PRs above 300 files), then only after the user confirms add `--post`.

Stop when the dossier is printed or written and any confirmed post has run. Do not review for defects, do not edit code, and do not narrate files outside the judgment bucket.
