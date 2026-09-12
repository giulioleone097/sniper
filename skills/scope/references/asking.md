# Asking through the host

A question to the user follows this contract in every stage, including empty-input prompts and the final build/card/stop choice. Select by the tools actually exposed and their current mode restrictions, not the host name alone. Prefer a permitted blocking question tool; otherwise use the asynchronous tool only when the host also provides an interruptible wait that keeps the turn active. Without either usable path, use the text fallback before opening a panel.

| Host | Tool | Per call | Options per question | Notes |
|---|---|---|---|---|
| Claude Code | `AskUserQuestion` | 1-4 questions | 2-4, `multiSelect` when choices are not exclusive | "Other" is added by the client |
| Codex blocking | `request_user_input` | 1-3 questions, prefer 1 | 2-3, mutually exclusive | Only when its live tool description permits the current mode; root thread only |
| Codex asynchronous | `request_user_input_async` | 1-3 questions, prefer 1 | 2-3 suggested answers, or free text | Returns an acknowledgement immediately; the answer arrives as a later user message |

Use the selected tool's actual schema. Blocking tools: `header` of twelve characters or fewer naming the decision; `question` as one sentence carrying the why; recommended option first, label ending in `(Recommended)`, description one clause on cost or benefit. Asynchronous tool: each `title` is a self-contained question; `options` are strings carrying the choice and its tradeoff, recommendation first; omit options for free text. Do not send blocking-only fields to the asynchronous tool. No "Other" option: the client supplies free text. No yes/no question dressed as options when a one-line answer would do.

When the round holds more questions than one call carries, ask first the ones whose answers unblock the most. Resolve that batch before opening another; only then recompute the frontier.

## Own the interaction until it is answered

1. Open one batch once. A return such as `accepted: true` means the questions were displayed, not that the user accepted an option. Preselected choices are not answers.
2. Blocking call: consume the returned answers. Asynchronous call: keep the turn active. Continue useful independent work, then use the host's interruptible wait (for example `clock.sleep`), at most 60 seconds per call, and resume waiting until a user reply arrives. Do not poll with shell sleeps or use a wait tool whose prerequisite has not occurred. Elapsed time is never an answer or approval.
3. While a question is pending, do not send a final response, close the turn, open a duplicate panel, or run work that depends on its answer. Keep any required progress updates brief and in commentary; a stage's "ask and stop" suspends dependent work, not this wait. An asynchronous tool return cannot satisfy a stage's stop condition.
4. Consume only what the user's reply settles. A partial answer keeps the rest pending; a status question or unrelated steering is not an answer. Handle the steering while preserving the open decisions. Explicit cancellation or replacement of the question resolves it as cancelled, never as agreement.
5. Once the batch is answered or explicitly cancelled, continue the stage or ask the next frontier. A design session hands off to build only on the user's actual choice.

If no permitted question tool and active wait are available, print the round as numbered text with the recommendation on its own line and end the turn; answers arrive as the next message. If the asynchronous tool or wait fails after opening, report that limitation and preserve the unanswered questions in plain text before ending. A hands-off run records missing input as blocked; it does not invent answers.
