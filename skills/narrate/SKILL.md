---
name: narrate
description: Turns a diff or pull request into a reading guide for human reviewers - partition by bucket, reading order, shape views, decision log, risk map, and inline walkthrough comments at the lines where decisions live. Use when a PR body is needed, when a change is too large to read as one diff, or when a reviewer asks where to start. Not for finding bugs (review) or shrinking code (simplify).
argument-hint: "[pr-number | pr-url | branch] [--out file] [--post] [--walkthrough]"
---

1. Resolve the range. A PR number or URL: `gh pr view <pr> --json number,url,headRefName,baseRefName,headRefOid`, then `git fetch origin +refs/heads/<base>:refs/remotes/origin/<base> +refs/pull/<n>/head:refs/remotes/origin/pr/<n>`; the range is `merge-base(origin/<base>, origin/pr/<n>)..origin/pr/<n>`. A branch or nothing: the current branch against the merge-base with the default branch. Record `OWNER/REPO`, `<n>`, `BASE`, `HEAD`.

2. Partition before reading anything: `python3 ${CLAUDE_SKILL_DIR}/scripts/pr-partition.py -C <repo> BASE HEAD` (the script lives in `scripts/` beside this file). Keep its table: it is the `Size` line of the guide, and the judgment list is the only code you read. Generated, mechanical, docs, and config are named in one line each and never narrated file by file.

3. Read the judgment bucket, entry points first: routes, handlers, CLI commands, public APIs, schema or contract files, then the flow inward. Up to 25 judgment files: read their diffs yourself. More than 25: take the `judgment by directory` list, dispatch one `sniper-scout` per directory in one message (Codex: `sniper_scout`; no agents: read the top files by churn per directory) with the file list and the question "what does each file do now, and why did it change", and read only the `path:line` lines they return. Never read the whole diff top to bottom.

4. Write the reading order: at most 25 numbered entries, one line each, `path - what it does now, why it changed`. Start where a reviewer should start. Below 25, list every judgment file; above, list the files that carry the design and roll the rest up as `<dir> (N files): <one line>`.

5. Pick at most two shape views, the smallest that make the change legible: pseudocode of the new control flow; a call tree of the main path; a shallow file tree of responsibilities; a Mermaid sequence only when the main path crosses three or more components; a before/after `diff` block for the key contract (type, schema, endpoint). Concrete names and paths only, no boxes labelled "service".

6. Write the decision log: three to seven decisions a reviewer could disagree with. Each line: the decision, the alternative rejected, why, and the `path:line` evidence. A decision without a rejected alternative is not a decision; drop it.

7. Write the risk map: each risk with the exact command or manual exercise that proves it safe, or `unverified` when nothing proves it. Reuse `prove` results from this session when they are current.

8. Emit the guide. Hard caps: 120 lines, no section restating another, no adjectives about quality. `--out <file>` writes it, otherwise print it:

```
<!-- sniper:narrate -->
# <outcome in one sentence>
Verify: <command>; <command>
Size: judgment +A/-D in F files | tests +A/-D | mechanical N files | generated N files | docs N | config N

## Read in this order
1. <path> - <what it does now, why it changed>

## Shape
<one or two views>

## Decisions
- <decision>. Rejected: <alternative>. Why: <reason>. (<path:line>)

## Risks
- <risk> -> <proof command | unverified>

## Follow-ups
- <adjacent finding left untouched, or none>
```

9. `--post`: show the guide, then only after the user confirms in this session replace the PR body with it: `gh pr edit <n> -R OWNER/REPO --body-file <file>`. A body without the `<!-- sniper:narrate -->` marker is the author's text: say so and ask before overwriting it.

10. `--walkthrough`: write `comments.json` with one entry per decision (`path`, `line`, `body` of at most three lines saying why, not what), run `python3 ${CLAUDE_SKILL_DIR}/scripts/pr-walkthrough.py OWNER/REPO <n> comments.json -C <repo>` to validate and show the payload (`-C` reads the diff from the local checkout; `gh pr diff` refuses PRs above 300 files), then only after the user confirms add `--post`. One review per run; never re-post an unchanged walkthrough.

Stop when the guide is printed or written and any confirmed post has run. Do not review for defects, do not edit code, and do not narrate files outside the judgment bucket.
