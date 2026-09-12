# Map: the repository and the ones that depend on it

Read on setup, or when discovery needs a missing or outdated part of `docs/atlas/map.md`.

1. Read what exists first. The map and conventions carry `stamp: <commit> <last PR> <date>`. When relevant changes since that stamp invalidate facts needed now, inspect and refresh those facts only, then stop. Otherwise reuse them. An older ancestor or unchanged PR count alone proves neither freshness nor staleness. `--refresh` or a missing map uses the discovery steps below; do not rebuild for a routine edit.

2. Facts before judgment: `sh <plugin root>/scripts/repo-facts.sh <repo> 12 <N>` (`<plugin root>` is the parent of the `skills/` directory this file lives in; `N` from `--prs`, default 30) prints layout, languages, hot spots, authors, commit conventions, checks, merged-PR cadence, who reviews and who leaves inline comments. Add `sh <plugin root>/scripts/checks.sh` per top-level project, `scripts/tracker.sh` for the forge, `scripts/consumers.sh` for the repositories that depend on this one, `scripts/tokens.sh` on the UI tree when there is one, `scripts/debt.sh` for the declared shortcuts.

3. Enrich with what the host exposes, never with what it does not. A code-graph server (gitnexus: `list_repos`, then `context`, `route_map`, `group_list` on this repo) gives routes and clusters for the entry points; a symbol server (serena: `get_symbols_overview` on the entry files) gives the public shape of each; use them for the parts the scripts cannot see and cite them as sources. Indexing a repository is a state change: say it before doing it. None available: the map is built from git, the scripts and reading, and says so.

4. Read the reviewers, not just the code. Take the merged PRs in the window, weight the reviewers by review count, and read their inline comments and review bodies (`gh api repos/<slug>/pulls/<n>/comments` and `/reviews`; `glab mr view <n> --comments`; `az repos pr` equivalents). What a reviewer asks for three times is a convention whether or not a document says it; what they never mention is not. Group what they ask for by theme with the quote and the PR that carries it, and note the PR authors whose changes pass with few comments as the reference style.

5. Dispatch when the repository is large: one `atlas-scout` per top-level project or domain asking for entry points, the public surface, the tests that pin it and what reaches it from outside (Codex: `atlas_scout`); one scout for the reviewer comments when there are more than about forty. Read their `path:line` lines, not their prose.

6. Write `docs/atlas/map.md` in the repository, for a reader who has never opened it:

```
stamp: <commit> <last merged PR> <yyyy-mm-dd>
# <repo> - map
## Cosa fa, in una frase
## Domini            one line each: what it owns, entry point path:line, the check that proves it, who reaches it
## Flusso principale  the one call tree or sequence a newcomer has to know, real names
## Confini            contracts other domains or repositories consume, with the consumer
## Repository collegati   from consumers.sh: name, what it takes from here, unread when not checked out
## Controlli         the commands checks.sh named, per project
## Punti caldi       hot spots with why they churn
## Scorciatoie dichiarate   the `ceiling:` ledger from scripts/debt.sh, no-trigger rows first
## Persone           authors by area from git, reviewers by weight, in the window
## Fonti             scripts, servers and PRs this map was built from
```

   Note whether the repo keeps a `CONTEXT.md` or `CONTEXT-MAP.md` glossary; record its path under `Fonti` when present, or `none` when absent.

   And `docs/atlas/conventions.md`, same stamp: one theme per section, the rule in one sentence, the reviewer quotes with PR numbers that prove it, and the reference PRs. Conventions a linter enforces are named as enforced and not repeated as prose.

7. `--linked`: run steps 2 to 6 on each consumer repository that is checked out, writing its own `docs/atlas/` there, and add one line per linked repository to this map. Not checked out: named as unread.

8. Hand the durable part on. A convention that would change how a reviewer here judges code goes through `<plugin root>/skills/ship/references/learn.md` into the closest AGENTS.md as a Code Review Rule, three lines at most; the map itself is pointed at from AGENTS.md by the setup steps, never copied into it.

Print the two paths and the stamp, then stop. The map describes; it does not review, fix or refactor anything.
