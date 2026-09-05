---
name: handoff
description: Use when context is running out or the work moves to another session, machine or person. Writes what a fresh session needs: goal card, branch and tree state, proven versus believed with the command, open work with the next action first, artifacts pointed at, secrets redacted. Not for approvers.
argument-hint: "[what the next session will focus on] [--out file]"
---

1. Take the argument as what the next session is for. Empty: hand off the work as it stands.

2. Write down where the work is, from this session and the repository, in this order: the goal card or the one-line outcome being pursued, the branch and the last commit, the working tree state (`git status --short`), and which stage of the pipeline finished last.

3. Point, never repeat. A plan file, a goal card written to disk, an issue, a commit message, a diff, a dossier: name its path or URL and say what it holds. Copying it into the handoff makes two copies that will disagree by tomorrow. Only what exists solely in this conversation gets written out in full.

4. Separate what is proven from what is believed. Every proven line names the command that proved it and its exact result. A check that was never run says `not run`, never `should pass`. A failure that is also on the baseline says so.

5. Name what is open as work, not as narrative: the next action first, then the blocked ones with what unblocks them, then the follow-ups deliberately left alone. Anything you assumed and did not verify belongs here, marked as an assumption.

6. Say which skill the next session should call first, and with what argument.

7. Redact before writing: no secret, token, password, connection string, or personal data goes into the file, not even one already visible in this session. Name the source instead: "the key lives in the environment file the deploy chart mounts".

8. Write to `--out <file>` when given, otherwise to the session scratch directory when the host provides one, otherwise `docs/handoff-<yyyy-mm-dd>-<slug>.md`. Never into the working tree without saying where it went. Print the path.

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

## Artifacts
- <path or URL> - <what it holds>
```

9. Stop when the file is written and its path printed. Do not summarise the conversation turn by turn, do not re-run checks to freshen the proof, and do not continue the work in the same breath.
