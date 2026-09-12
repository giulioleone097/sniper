---
name: prototype
description: Use when a design question code review can't answer needs settling before real work starts — which interaction model works, does this state machine feel right, what should this screen look like. Not for a design already validated and ready to implement.
argument-hint: "[the design question, state machine or UI to prototype]"
---

1. Take the argument as the question. Empty: ask what to prototype in one line and stop there. Pick the branch from the question's shape: a question about a state machine, a flow, or "does this logic feel right" is the logic branch; a question about layout, interaction feel, or "which of these works" is the UI branch. Genuinely ambiguous and the user reachable: ask through the host's question tool; otherwise infer from the surrounding code (a backend module → logic, a page or component → UI) and state the assumption.

2. Pick a scratch location outside the versioned tree: `.prototype-<slug>/` at the repo root, added to `.gitignore` if not already ignored, or the system temp directory when the repo forbids stray top-level dirs. Never place prototype files under `<plugin root>` or any other tracked path, and never stage or commit them.

3. Logic branch: build one self-contained HTML file in the scratch dir — inline JS and CSS, no build step, no dependency — that pushes the state machine through the cases hard to reason about on paper. Give it free-play controls plus buttons that walk guided cases, and render the full current state after every action so a non-developer can drive it and see what changed.

4. UI branch: build several radically different variants of the interaction behind one entry point in the scratch dir (one HTML file or one route), switchable with a plain toggle — buttons, tabs, or a query param — so the variants sit side by side without restarting anything.

5. Keep it disposable in both branches: no tests, no error handling beyond what keeps it runnable, no abstractions, no persistence unless persistence is itself the question — then a scratch file or database named so its disposability is obvious. It is never hardened and never reused; the deliverable is the answer it produces, not the code.

6. Hand the artifact to the user, let them exercise it, and capture the verdict: which option won or what the logic proved, and what it ruled out. Leave the scratch dir where it is or delete it — either way it stays out of the versioned tree and nothing from it is committed.

7. Report the verdict in this shape, then feed the proven answer into `atlas` or `scope` (Skill tool `sniper:atlas` / `sniper:scope`, `$atlas` / `$scope` on Codex) so the settled design continues as a normal request:

```
prototype: <slug>
question: <what it was built to answer>
path: <scratch path, outside the versioned tree>
verdict: <what the prototype proved and what it ruled out>
next: atlas <question> | scope <question> | none
```

Stop when the artifact has produced a verdict and it has been reported, with the follow-up handoff run when the verdict warrants one.
