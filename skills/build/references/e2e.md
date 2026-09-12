# E2E: deterministic scenarios on the repository's harness

Read when a changed flow is user-facing or a critical integration path and proof needs the real path exercised end to end; authoring the scenario is part of the change, not a follow-up.

1. Find the harness before writing anything: `sh <plugin root>/scripts/checks.sh <changed path>` (`<plugin root>` is the parent of the `skills/` directory this file lives in) prints `e2e=` when the project already runs one — Playwright, Cypress, or a Detox/Maestro config under the touched project. Use that harness; never introduce a second framework beside it. None exists: say so once — a first harness is a scope decision for the card, not something to hand-roll around the work.
2. Write one scenario per critical changed flow, covering the happy path and the key error or edge path (checkout: payment success plus declined-card retry; auth: valid login plus expired-token refresh). Flows the change cannot reach get none.
3. Drive the flow through stable selectors. A step that needs a handle the markup lacks gets a `data-testid` added as part of this change — that edit is the work, not overhead. Never key on copy text, DOM position, or styling classes.
4. Wait on a stable signal, never on time: assert the element, response, or state that proves the step landed. A `sleep`, a raised timeout, or a blanket retry is a postponed flake.
5. Isolate each scenario: its own setup and teardown and its own data, passing alone and in any order — no state shared with siblings or borrowed from a previous run.
6. Run programmatically only: one non-interactive command, CI-compatible, failing non-zero. Iterate on the focused scenario of the changed flow; before closure the required suite passes whole, not just the focused run.
7. Treat a flake as a diagnosis: find the unstable signal — selector, wait, leaked state — and fix it, never the wait. A flow that breaks repeatedly gets promoted to a mandatory regression scenario so it cannot rot quietly.

Recording run artifacts for the dossier belongs to `<plugin root>/skills/ship/references/evidence.md`; this file owns whether a scenario is trustworthy.
