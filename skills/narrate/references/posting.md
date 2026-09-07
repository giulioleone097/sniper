# Posting the dossier

Read only when `--out`, `--post` or `--walkthrough` was asked.

`--out <file>` writes the dossier, otherwise print it. `--post`: show it, then only after the user confirms in this session replace the PR body with `gh pr edit <n> -R OWNER/REPO --body-file <file>`; a body without the `<!-- sniper:narrate -->` marker is the author's text, say so and ask first. `--walkthrough`: write `comments.json` (one entry per decision, `path`, `line`, `body` of at most three lines saying why), run `python3 <this skill>/scripts/pr-walkthrough.py OWNER/REPO <n> comments.json -C <repo>` to validate and show the payload (`-C` reads the diff locally; `gh pr diff` refuses PRs above 300 files), then only after the user confirms add `--post`.
