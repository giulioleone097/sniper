---
name: question
description: Use when a decision is blocked on knowledge that lives in someone else's head. Turns the gap into a Markdown questionnaire the user hands to that person to fill async or together over a meeting, grilling the user only on who it goes to and what they need back. Not for questions the user or the repository can already answer.
argument-hint: "[decision or topic that's blocked] [--out <file>]"
---

1. Take the argument as the decision or topic blocked on someone else's knowledge. Empty: ask what decision is blocked, in one line, through the host's question tool, and stop there.

2. Grill the send, not the subject: ask who it goes to — the recipient's role, expertise and relationship to the user — through the host's question tool, contract in `<plugin root>/skills/scope/references/asking.md` (`<plugin root>` is the parent of the `skills/` directory this file lives in). This fixes the questionnaire's tone and how much context it must carry. Done when the recipient is known.

3. Ask what the user needs back: the concrete decisions or facts the user can't resolve alone and must walk away with. One exchange, same question tool. Done when the list is concrete enough that each item can become one question.

4. Draft the questionnaire from the template below. Order questions most-important-first (async may give only one pass), group under `##` theme headings once there are more than a handful, one idea per question with an answer stub directly beneath, and a one-line "why this matters" only where the question invites a throwaway or misread answer. Every item named in step 3 maps to a question.

5. Write the file to `--out <file>` when given, otherwise `docs/question-<slug>.md` (slug from the topic), and print the path.

```
# <Questionnaire title>

**Purpose:** <why this exists and the decision riding on it>

**From:** <the user> · **To:** <the recipient> · **How your answers will be used:** <where they go>

## Context

<one paragraph orienting a recipient who wasn't in the user's head>

## How to answer

<deadline, rough effort, "I don't know" is a useful answer>

## <Theme heading>

### <Question, one idea>

_Why this matters: <only where misreading is likely>_

>

## Anything else?

<closing catch-all>
```

Stop when the file exists and every item from step 3 maps to a question.
