# Read-only audits

Read only when `--repo` or `--debt` was asked. Neither edits anything.

## `--debt`

Run `sh <plugin root>/scripts/debt.sh <repo>` (`<plugin root>` is the parent of the `skills/` directory this file lives in). Print its rows as they come with the `no-trigger` ones first, end with its count line, and stop: a `ceiling:` comment that names no upgrade trigger is the one that rots.

## `--repo [path]`

Read-only audit of the tree, applying nothing. Rank attention by hot spots first, so the files that keep changing get read first:

   `git log --oneline -n 300 --name-only --pretty=format: | sort | uniq -c | sort -rn | head -30`

   Then walk those files down the six rungs of `shrink.md` beside this file, biggest cut first.

Print the same finding lines as the default path, ranked biggest cut first, and end at `net: -<N> lines possible.`; there is no `regression:` line because nothing changed.
