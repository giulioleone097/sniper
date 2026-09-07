---
name: grill
description: Use when the user says grill me, or brings an idea, plan or design whose outcome is still undecided and wants it interrogated before any card exists. Works the decision tree in rounds through the host's question tool, then hands the settled request to scope. Not for a request whose shape is already clear.
argument-hint: "[the idea, plan, or design to grill]"
---

1. Take the argument as the subject. Empty: ask what to grill through the host's question tool and stop there.

2. Read `<plugin root>/skills/scope/references/grill.md` (`<plugin root>` is the parent of the `skills/` directory this file lives in) and work it to the end: the tree in your head, facts looked up yourself, the whole frontier per round through the host's question tool with the recommendation first, no round answered on assumptions. A subject whose outcome, boundary and acceptance you could already write is not grilled: say so in one line and carry that reading to step 4.

3. When the frontier is empty, ask one last question through the same tool: build now, card only, or stop at the decisions, the recommendation first and chosen from what was settled. A design session is not yet a request to change code, so the loop starts here only on that answer.

4. Print the settled tree exactly as the reference shows it. Build now: invoke `scope` on the settled request (Skill tool `sniper:scope`, `$scope` on Codex) and the loop carries it from there. Card only: invoke `scope --card-only`. Stop: the tree is the deliverable; the decisions a future reader would re-litigate go through ship's learn step when the work lands.

Stop when the tree is printed and the chosen handoff has run. Never write code here, and never read the user's silence as agreement.
