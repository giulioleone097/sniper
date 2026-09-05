# Asking through the host

A question to the user goes through the host's question tool, so the answer comes back structured and the user picks with one keystroke. Free text in the transcript is the fallback, not the default.

| Host | Tool | Per call | Options per question | Notes |
|---|---|---|---|---|
| Claude Code | `AskUserQuestion` | 1-4 questions | 2-4, `multiSelect` when choices are not exclusive | "Other" is added by the client |
| Codex | `request_user_input` | 1-3 questions, prefer 1 | 2-3, mutually exclusive | Only in the collaboration modes its description names; never in `codex exec`; root thread only |

Shared shape, both hosts: `header` of twelve characters or fewer naming the decision; the `question` as one sentence carrying the why; the recommended option first, its label ending in `(Recommended)`, each option's description one clause on what choosing it costs or buys. No option for "Other" in the list, no yes/no question dressed as options when a one-line answer would do.

When the round holds more questions than one call carries, ask first the ones whose answers unblock the most, then the rest, and only then recompute the frontier.

When neither tool is available (a hands-off run, a Codex mode without it), print the round as numbered text with the recommendation on its own line and stop; the answers arrive as the next message.
