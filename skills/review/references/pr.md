# Pull request threads: findings inline, reviewers answered

Read when `--pr` or `--address <pr>` was given. Nothing is posted before the user confirms the drafts in this session, unless posting was authorized up front. No agent attribution in any post: the forge already records the author.

## `--pr`: one thread per finding

1. `sh <plugin root>/scripts/tracker.sh` names the forge and whether its CLI is logged in (`<plugin root>` is the parent of the `skills/` directory this file lives in). The PR is the current branch's unless the user named one; its number and head SHA `<sha>`: `gh pr view --json number,headRefOid`; `glab mr view -F json` (`iid`, `diff_refs.head_sha`, plus `.base_sha` and `.start_sha` for the thread position); `az repos pr list --source-branch <branch>` (`pullRequestId`, `lastMergeSourceCommit`). No PR for the branch, or `cli=none` / `auth=missing`: say which and draft only.
2. One thread per verified finding at its line in the head SHA, not in the repaired local tree (`git show <sha>:<p>` is the pushed file; shrink and fixes have already shifted the local one). A finding on a line the PR did not change goes into the summary: GitHub and GitLab refuse it inline. Body `P<n> <lens>: problem. fixed: <repair> | fix: <proposal>`; one summary comment with the cut lines, `net:`, the `regression:` lines and `ship: ready | not ready`.
3. Post, per forge:
   - GitHub: `gh api repos/{owner}/{repo}/pulls/<n>/comments -f body=<b> -f commit_id=<sha> -f path=<p> -F line=<l> -f side=RIGHT`; summary `gh pr comment <n> --body-file <f>`.
   - GitLab: `glab api projects/:id/merge_requests/<iid>/discussions -f body=<b> -f "position[position_type]=text" -f "position[base_sha]=<base>" -f "position[start_sha]=<start>" -f "position[head_sha]=<sha>" -f "position[new_path]=<p>" -F "position[new_line]=<l>"`; summary `glab mr note <iid> -m <b>`.
   - Azure DevOps: `az rest --method post --uri "https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo}/pullRequests/<n>/threads?api-version=7.1" --body '{"comments":[{"content":"<b>"}],"status":"active","threadContext":{"filePath":"/<p>","rightFileStart":{"line":<l>,"offset":1},"rightFileEnd":{"line":<l>,"offset":1}}}'`.
4. Print `posted: <n> threads, 1 summary`, or `drafted: <path> - <reason>` when posting was not authorized, the branch has no PR, or the CLI is missing or logged out.

## `--address <pr>`: the reviewers' comments

1. Work on the PR's head branch: not checked out and `git status --porcelain` empty, `gh pr checkout <n>`, `glab mr checkout <iid>` or `az repos pr checkout --id <n>`; local changes on another branch: name both branches and stop before any edit. Fetch every thread: GitHub `gh api repos/{owner}/{repo}/pulls/<n>/comments` and `gh pr view <n> --comments`; GitLab `glab api projects/:id/merge_requests/<iid>/discussions`; Azure DevOps `az rest` on `.../pullRequests/<n>/threads`. Skip bots, resolved or outdated threads, and your own.
2. Group by cause: several comments on one defect are one repair. Decide each group from the code, not the tone:
   - a verified defect within the PR's outcome: fix at the shared cause, prove with the nearest check, reply `fixed in <sha>: <what changed> - <check> pass`;
   - not a defect: reply with the evidence, `path:line` and the test or contract that pins the behavior, one or two sentences, no argument;
   - real but outside this PR: reply `follow-up: <issue or handoff line>` and record it there.
3. Reply on the thread itself: GitHub `gh api repos/{owner}/{repo}/pulls/<n>/comments/<id>/replies -f body=<b>`; GitLab `glab api projects/:id/merge_requests/<iid>/discussions/<id>/notes -f body=<b>`; Azure DevOps `az rest --method post` on `.../threads/<id>/comments`. Never resolve a thread the reviewer opened, never change the PR state, never commit or push from here: once the user confirms the drafts and the push (or authorized both up front), `ship --push` (Skill tool `atlas:ship`, `$ship` on Codex) lands the repairs and the `fixed` replies take its sha; until then they stay drafted.
4. Print one line per thread, `<url> - fixed <sha> | drafted: <path> | rebutted: <evidence> | follow-up: <where>`, then the regression lines for the repairs.

Stop when every thread has its line and the confirmed posts have run.
