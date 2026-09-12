# Intake: work that arrived from outside

Read when the argument is an issue number, a URL, a work item, a pasted bug report, a transcript, an image, a handoff or atlas file rather than a task description.

1. Read the source. Run `sh <plugin root>/scripts/tracker.sh` (`<plugin root>` is the parent of the `skills/` directory this file lives in) for every item, pasted included: it names the forge, the CLI and whether it is authenticated, which step 4 and `--reply` depend on. A bare number or a URL is then fetched with the CLI the script named:

   | forge | item | pull request |
   |---|---|---|
   | github | `gh issue view <n> --comments` | `gh pr view <n> --comments`, `gh pr diff <n>` |
   | gitlab | `glab issue view <n> --comments` | `glab mr view <n> --comments` |
   | azure | `az boards work-item show --id <n>` | `az repos pr show --id <n>` |
   | none, or `auth=missing` | the file the argument names, or `docs/tickets/<n>.md` | the local diff |

   The CLI is missing or logged out: say which one and what it needs, then work from what the user pasted. Never invent the item's content, and never install a tool to read it.

   An image (a screenshot, a photo of a screen, a diagram) is read as the report: transcribe what it shows into a claim, the message, the state, the step it was taken at, before reproducing anything; its path is the `source:`. What the picture does not show is a missing detail for step 6, not a guess.

2. A pull request is an item with code attached: read the diff too, and everything below applies to it unchanged.

   A handoff file (`# Handoff:` on its first line, written by `handoff`) is a session resuming: its `next:` line is the work, its Open list is the outcome and the out of scope, and its Proven lines are reused as proof when `git status --short` and the last commit still match its Where it stands; anything marked assumption gets verified, nothing marked proven gets redone, and anything marked decided is carried into the card as settled, never re-asked. An atlas file (`# Atlas:` on its first line, written by `atlas`) works the same way: its settled lines are decisions already made and are never re-asked, their `reach:` lines feed the card's Risk and Size without re-measuring while the contracts they name are unchanged, its open lines are the frontier if grilling resumes, its `next:` line is the work. A howto file (`# Howto:` on its first line, written by `howto`) works the same way at the scale of a whole map: its open nodes are the frontier, its settled lines are decisions already made and never re-asked, its `next:` line is the work. Skip step 3 and 4 for all three unless the file names an item, then go to step 5.

3. Reproduce before believing. A bug gets the reporter's steps run against the code as it stands: the failing command, the request, the input. Report what happened - reproduced, did not reproduce, or could not tell and why. An unreproduced bug is not a fixed bug and not a wrong reporter; it is a missing detail, and step 6 asks for it.

4. Check the two things that make the work vanish before doing any of it:
   - **Already implemented.** Search by the domain concept the item describes, not by its wording, starting from `docs/sniper/map.md` when it exists; the feature may exist under another name. Found: say where it lives and stop.
   - **Already decided against.** Read the repository's own record of rejected work when it keeps one (a decisions or out-of-scope directory, closed items the CLI can list). Found: say which decision, and let the user reopen it deliberately rather than by accident.

5. Map the item onto the card fields: everything it says becomes outcome, acceptance, out of scope or risk, quoted where it is precise. What it leaves vague is the caller's: scope's card steps resolve it and set the size; grill grills it.

6. Too thin to act on: name exactly what is missing, as questions the reporter can answer, and never as "please provide more information". Say what you established yourself so nobody redoes it. Several open design branches rather than missing facts: that is `grill.md`, not a question list.

7. `--reply` posts what you found back on the item - reproduction result, what already exists, or the questions - after showing the text and getting the user's confirmation in this session. One comment, no agent attribution (the forge already records the author), and never a state change (no close, no label, no assignment) unless the user asked for that specific change.

```
source: <forge>#<n> | <path> | pasted
claim: reproduced (<command>) | not reproduced (<what happened>) | not testable (<why>)
already: implemented at <path:line> | rejected in <path> | new
missing: <question> | none
next: card | grill | stop (<why>)
```

Stop once the block is printed: `next: card` returns to the caller's steps with what intake established, `next: grill` goes to `grill.md`, `next: stop` ends with the reason. Do not plan, do not write code, and do not change the item's state on your own initiative.
