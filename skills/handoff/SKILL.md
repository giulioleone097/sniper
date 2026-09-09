---
name: handoff
description: Use when the user says hand off, handoff, stop here, or pick this up later, or when a session must stop before the work is done. Writes where the work stands, what is proven, what is open and which skill the next session calls first, pointing at artifacts instead of repeating them. Not for finished work; ship commits that.
argument-hint: "[what the next session is for] [--out <file>]"
---

1. Take the argument as what the next session is for. Empty: hand off the work as it stands.

2. Write down where the work is, from this session and the repository, in this order: the goal card or the one-line outcome being pursued, the branch and the last commit, the working tree state (`git status --short`, plus every worktree `git worktree list` shows beyond this one, with its path and the slice whose uncommitted diff it holds, since build's parallel workers leave theirs unintegrated when a session stops mid-slice), and which stage of the loop finished last.

3. Point, never repeat. A plan file, a goal card written to disk, an issue, a commit message, a diff, a dossier, a ledger: name its path or URL and say what it holds. Copying it into the handoff makes two copies that will disagree by tomorrow. Only what exists solely in this conversation gets written out in full.

4. Separate what is proven from what is believed. Every proven line names the command that proved it and its exact result. A check that was never run is not proven: it is an assumption under Open. A failure that is also on the baseline says so.

5. Name what is open as work, not as narrative: the next action first, then the blocked ones with what unblocks them, then the follow-ups deliberately left alone. Anything you assumed and did not verify belongs here, marked as an assumption. A decision settled or a constraint given in this conversation that no file carries (a path not to touch, a model pin, an alternative grill rejected on the way to build) is listed as `decided`: it is not open, but this file is the only place the next session will find it.

6. Say which skill the next session should call first, and with what argument. The default is `scope <this file>`: intake reads a handoff file and resumes from its `next:` line without redoing what is marked proven.

7. Redact before writing: no secret, token, password, connection string, or personal data goes into the file, not even one already visible in this session. Name the source instead: "the key lives in the environment file the deploy chart mounts".

8. Write to `--out <file>` when given, otherwise `docs/handoff-<yyyy-mm-dd>-<slug>.md`, where `scope` looks for it. Print the path.

```
# Handoff: <outcome in one line>
next: <the exact next action> - call `<skill>` with <argument>

## Where it stands
<branch, last commit, working tree, stage that finished>

## Proven
- <claim> - `<command>` - <exact result>

## Open
1. <next action>
2. <blocked item> - unblocked by <what>
- follow-up: <left alone deliberately>
- assumption: <believed, never verified>
- decided: <decision or constraint from this session that no file carries>

## Artifacts
- <path or URL> - <what it holds>
```

Stop when the file is written and its path printed. Do not summarise the conversation turn by turn, do not re-run checks to freshen the proof, do not commit, and do not continue the work in the same breath.
