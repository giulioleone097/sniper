# Read-only audits

Read only when `--repo`, `--debt` or `--rules` was asked. None edits anything.

## `--debt`

Run `sh <plugin root>/scripts/debt.sh <repo>` (`<plugin root>` is the parent of the `skills/` directory this file lives in). Print its rows as they come with the `no-trigger` ones first, end with its count line, and stop: a `ceiling:` comment that names no upgrade trigger is the one that rots.

## `--repo [path]`

Read-only audit of the tree, applying nothing. Rank attention by hot spots first, so the files that keep changing get read first:

   `git log --oneline -n 300 --name-only --pretty=format: | sort | uniq -c | sort -rn | head -30`

   Then walk those files down the six rungs of `shrink.md` beside this file, biggest cut first.

Print the same finding lines as the default path, ranked biggest cut first, and end at `net: -<N> lines possible.`; there is no `regression:` line because nothing changed.

## `--rules`

Dedup and promotion audit of the project's rule-bearing files — the `## Code Review Rules` and sibling sections `learn` appends to, in every AGENTS.md and CLAUDE.md in the tree — against the skills and references that already own each subject. For every rule found, one line:

```
path:line <rule in a few words> -> keep | delete (already carried by <file>) | promote (into <skill's reference>)
```

`keep` is the default; `delete` when a skill, reference or another rules file already carries the same invariant; `promote` when the rule governs how one skill behaves and would be found sooner inside it — promotions are proposed here, never applied: the move itself goes through `learn`'s target pick the next time the rule is touched, or by hand. Rules sections that stay free of what skills already say cost their tokens once, like the doctrine.
