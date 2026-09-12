# Narrate: the approval dossier

Read when a PR body is needed (`ship --pr`), or when the user asks for the dossier alone.

1. Resolve the range. A PR number or URL: per the forge `sh <plugin root>/scripts/tracker.sh` names (`<plugin root>` is the parent of the `skills/` directory this file lives in), `gh pr view <n> --json number,url,headRefName,baseRefName,headRefOid,mergeable`, `glab mr view <iid> --output json` (`source_branch`, `target_branch`, `sha`, `detailed_merge_status`) or `az repos pr show --id <n>` (`sourceRefName`, `targetRefName`, `lastMergeSourceCommit`, `mergeStatus`); then `git fetch origin +refs/heads/<base>:refs/remotes/origin/<base> +<head>:refs/remotes/origin/pr/<n>` with `<head>` = `refs/pull/<n>/head` on GitHub, `refs/merge-requests/<iid>/head` on GitLab, the `sourceRefName` on Azure DevOps (it publishes no head ref); range `merge-base(origin/<base>, origin/pr/<n>)..origin/pr/<n>`. A branch or nothing: current branch against the merge-base with the default branch. Record `OWNER/REPO` (tracker.sh's `repo=`), `<n>`, `BASE`, `HEAD` and the merge status field named above.

2. Audience, language, size. The reader approves and may not know this code: one idea per sentence, in words they would use, acronyms expanded once, no path or command in the prose - paths belong in the diagrams, the evidence lines and the collapsible blocks. Language: `--lang`, else that of the repository's recent PR descriptions and commits; the template's headings, verdict values, labels and fixed phrases are shown in Italian and follow that language too; only the `<!-- atlas:narrate -->` marker stays as written. Minimal: every line carries a fact the approver needs and none restates another; a section with nothing to say is omitted, not filled.

3. Partition: `python3 <plugin root>/scripts/pr-partition.py -C <repo> BASE HEAD`. The judgment list is the only code you read; group it into domains the reader already has a name for: the domains in `docs/atlas/map.md` when the repository has a map, else one per deployable unit, shared library, contract surface, or infrastructure layer, plus one per repository or project the diff reaches without touching. Domains are the reader's mental model, never the folder tree.

4. Blast radius, mechanical: affected projects from the workspace tool (`nx show projects --affected --base=BASE --head=HEAD`; turbo, bazel, `go list`, solution references elsewhere), pure dependents marked; `python3 <this skill>/scripts/pr-contracts.py -C <repo> BASE HEAD` (`<this skill>` is the skill directory above this `references/` folder) for removed exported symbols with consumers outside the diff and deleted files still referenced (judge each hit); for every shared contract the diff changes (DTO, schema, socket event, endpoint, config key, bus message, Helm value) name the consumers at HEAD with `git grep -w` and record the line that absorbs or breaks - that line is what the drill-down cites, not "should be fine". Then outside the repository: `sh <plugin root>/scripts/consumers.sh` names the sibling checkouts and workspace members that depend on this one; each gets the same `git grep -w` for the changed contracts and its own domain in the drill-down when it is reached, marked unread when it could not be read.

5. Verify, executed. Worktree at HEAD; run the repository's own test target for every affected project and build or typecheck for every pure dependent, mirroring CI; long suites in the background with JUnit/TRX summarised by `python3 <this skill>/scripts/test-summary.py`. Attribute every failure by running the same target on the merge-base in a second worktree. Then go after what tests do not reach: contract regeneration checks, the container build, a migration dry run against a fixture, and the end-to-end harness when the repository ships one or the change touches a UI flow: `<this skill>/references/evidence.md` runs it, records real screenshots and videos, and attaches them. Before writing "not verified" for anything, try three routes in order: run the check, find the existing test that covers it and cite it, or show the code path that makes it safe with `path:line`. Only when all three fail does it go to "outside this verification", with the reason and the owner (release runbook, nightly job, the author) - never the approver.

6. Read the judgment bucket per domain, entry points first; above 25 files dispatch one `atlas-scout` per domain in one message (Codex: `atlas_scout`) asking "what does each file do now, why did it change, what reaches it from outside, and what did NOT change around it", and read only their `path:line` lines. Every domain needs its before/after shape and its boundary list, so a scout that returns prose without call sites gets one follow-up, then you read the entry points yourself.

7. Draw before you write. Read `<this skill>/references/shapes.md`: the one map for the whole change, then one diagram per domain. A domain without a diagram is not narrated, it is summarised.

8. Write the dossier. A pull request template the repository keeps (`.github/PULL_REQUEST_TEMPLATE*`, `.gitlab/merge_request_templates/`, `.azuredevops/pull_request_template.md`) is the floor: its headings, fields and checklists stay and are filled, and the dossier sits under them. The first screen (verdict, plain words, map) fits in 20 lines; the drill-down is the body; file-level evidence sits in `<details>` blocks that GitHub, GitLab and Azure DevOps render collapsed:

```
<!-- atlas:narrate -->
## Verdetto: <mergeabile | mergeabile con condizioni | non mergeabile oggi>
<the one blocking reason and its fix, owner named; or "nulla blocca">

## Cosa cambia
- <3-5 bullets: what the user or operator gets, what disappears, what stays untouched>

## Mappa
<one map: lanes = runtimes or tiers, changed and unchanged nodes, the hero edge marked>

## Drill-down
### <n>. <domain, in plain words> - <✅ | ⚠️ | ❌> - <files changed, +lines/-lines>
<two or three sentences: the pressure that opened this domain and what runs differently now, in the order it runs>
<the domain's diagram>
- confine: <what leaves this domain> - <consumer at HEAD> - <the line that absorbs it or the test that pins it>
- prova: <what ran> - <result, counts, base attribution for a pre-existing failure> | <flow> - <e2e command> - <passed n/n> - <screenshot or video link>
- decisione: <chosen> over <rejected> - <the measured reason>
- rischio: <the consequence in plain words>
<details><summary>Dettaglio</summary> path:line per claim, what each entry point does now, what was deleted and why nothing calls it </details>

## Fuori dal perimetro
- <what> - <why it could not be verified here> - <who covers it and when: release runbook, nightly job, the author before merge>

<details><summary>Comandi eseguiti</summary> one line per command as run: result, counts, base comparison, worktree paths, range, date </details>
<details><summary>Ordine di lettura</summary> <= 25 `path - what it does now, why it changed`, follow-ups </details>
```

9. Rules. ✅ means executed evidence passes or the failures are proven pre-existing on the base branch; ⚠️ means evidence exists but a residual risk or an environment gap remains, named; ❌ means the PR itself prevents the check or a new failure is attributed to it. A `decisione` without a rejected alternative is a description: cut it; a `rischio` that is "none" is omitted, not written. The dossier contains no task for the approver: what the author must fix is in the verdict, what the release process covers is in "Fuori dal perimetro" with its owner. This is comprehension, not review: no bug list, no severity table, no security findings - `review` owns those. Numbers stay in the header, the `prova` lines and "N test verdi" form. A domain gets at most 25 lines outside its details block and one diagram, sized by `<this skill>/references/shapes.md`; the whole dossier at most 400. A domain that needs more is two domains merged; one that cannot fill its lines with mechanism, boundaries and named evidence did not need narrating.

10. `--out`, `--post` or `--walkthrough` asked: read `<this skill>/references/posting.md`; nothing is posted before the user confirms in this session.
Stop when the dossier is printed or written and any confirmed post has run. Do not review for defects, do not edit code, and do not narrate files outside the judgment bucket.
