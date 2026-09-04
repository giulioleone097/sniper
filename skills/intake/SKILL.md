---
name: intake
description: Turns whatever the work arrived as - an issue, a pull request, a work item, a bug report, a chat transcript, a paragraph from a colleague - into a verified goal card, reading the item from whichever tracker the repository actually has, checking the claim against the code before anyone plans around it, and saying plainly when it is already implemented, already rejected, or too thin to act on. Use at the start of work that came from outside this session. Not for work already carded, and not for reporting back to a reviewer, which narrate owns.
argument-hint: "[issue number | url | file | pasted text] [--reply]"
---

1. Read the source. `sh <plugin root>/scripts/tracker.sh` (`<plugin root>` is the parent of the `skills/` directory this file lives in) names the forge, the CLI and whether it is authenticated. A bare number or a URL is then fetched with the CLI the script named:

   | forge | item | pull request |
   |---|---|---|
   | github | `gh issue view <n> --comments` | `gh pr view <n> --comments`, `gh pr diff <n>` |
   | gitlab | `glab issue view <n> --comments` | `glab mr view <n> --comments` |
   | azure | `az boards work-item show --id <n>` | `az repos pr show --id <n>` |
   | none, or `auth=missing` | the file the argument names, or `docs/tickets/<n>.md` | the local diff |

   The CLI is missing or logged out: say which one and what it needs, then work from what the user pasted. Never invent the item's content, and never install a tool to read it.

2. A pull request is an item with code attached: read the diff too, and everything below applies to it unchanged.

3. Reproduce before believing. A bug gets the reporter's steps run against the code as it stands: the failing command, the request, the input. Report what happened - reproduced, did not reproduce, or could not tell and why. An unreproduced bug is not a fixed bug and not a wrong reporter; it is a missing detail, and step 6 asks for it.

4. Check the two things that make the work vanish before doing any of it:
   - **Already implemented.** Search by the domain concept the item describes, not by its wording; the feature may exist under another name. Found: say where it lives and stop.
   - **Already decided against.** Read the repository's own record of rejected work when it keeps one (a decisions or out-of-scope directory, closed items the CLI can list). Found: say which decision, and let the user reopen it deliberately rather than by accident.

5. Emit the card. Everything the item says becomes one of: outcome, acceptance, out of scope, risk. Where the item is precise, quote it; where it is vague, resolve it per core and mark the reading as an assumption. Then invoke `scope` with what you have so the card comes out in its shape - `scope` decides the size and what comes next.

6. Too thin to act on: name exactly what is missing, as questions the reporter can answer, and never as "please provide more information". Say what you established yourself so nobody redoes it. Several open design branches rather than missing facts: that is `grill`, not a question list.

7. `--reply` posts what you found back on the item - reproduction result, what already exists, or the questions - after showing the text and getting the user's confirmation in this session. One comment, no attribution trailer, and never a state change (no close, no label, no assignment) unless the user asked for that specific change.

```
source: <forge>#<n> | <path> | pasted
claim: reproduced (<command>) | not reproduced (<what happened>) | not testable (<why>)
already: implemented at <path:line> | rejected in <path> | new
missing: <question> | none
next: scope | grill | stop (<why>)
```

Stop once the card exists, or once you have said what is missing. Do not plan, do not write code, and do not change the item's state on your own initiative.
