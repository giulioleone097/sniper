---
name: grill
description: Use when the user says grill me, or brings an idea, plan or design whose outcome is still undecided and wants it interrogated before any card exists. Works the decision tree in rounds through the host's question tool, then asks whether to build, card only or stop. Not for a request whose shape is already clear.
argument-hint: "[the idea, plan, design, file, issue or PR to grill] [--out <file>]"
---

1. Take the argument as the subject. Empty: ask what to grill in one line and stop there. A file, an issue number, a URL or a PR: read it first through `<plugin root>/skills/scope/references/intake.md` (`<plugin root>` is the parent of the `skills/` directory this file lives in), list what the document already settles, and grill only the decisions it leaves open.

2. A subject whose outcome, boundary and acceptance you could already write is not grilled: say so in one line and carry that reading to step 3. Otherwise read `<plugin root>/skills/scope/references/grill.md` and work it to the end.

3. When the frontier is empty, ask one last question through the host's question tool: build now, card only, or stop at the decisions, the recommendation first and chosen from what was settled. A design session is not yet a request to change code, so the loop starts here only on that answer.

4. Print the settled tree exactly as the reference shows it. Card only, Stop, or `--out` given: write the tree to `--out <file>`, else `docs/grill-<yyyy-mm-dd>-<slug>.md`, headed `# Grill: <subject>` with a `next:` line, and print the path; `scope <file>` resumes from it. Then, on build now, invoke `scope` on the settled request (Skill tool `sniper:scope`, `$scope` on Codex); on card only, invoke `scope --card-only`.

Stop when the tree is printed and the chosen handoff has run.
