---
name: plan
description: Breaks a locked goal into ordered tasks carrying owned paths, acceptance, proof, and test seams; delivers a chat brief under four tasks and writes docs/plans/<yyyy-mm-dd>-<slug>.md otherwise. Use when the work spans four or more tasks, more than one owner, or a change others depend on such as a schema, interface, or migration. Not for implementing: it writes the plan and stops.
argument-hint: "[task text or goal card] [--tickets]"
---

1. Read the argument. A goal card is the input. Bare task text is not, so invoke the `scope` skill first and plan from the card it returns.
2. Read the code the work touches before decomposing anything. List the files each task will create or modify and what each one owns after the change.
3. Choose test seams from the repository, not from theory: reuse the seam this kind of change is already tested at, take the highest one, and prefer one seam to three. When the repository keeps no tests for this kind of change, write `Test seam: none` on that task with the reason; per core, do not stand up a suite the repository does not have.
4. Cut a task where a reviewer could reject it and still accept its neighbour. Fold setup, configuration, and docs into the task whose deliverable needs them. Every task ends in something independently provable.
5. Assign owned paths per task. Tasks that can run beside each other must have prefix-disjoint path sets; when two tasks want the same file, order them with `After` rather than splitting the file to fake independence.
6. Count the tasks. Fewer than four under a single owner: deliver the brief in chat and stop. Four or more, more than one owner, or a risk surface (authorization, payments, data migration, an external contract): write `docs/plans/<yyyy-mm-dd>-<slug>.md` with the same blocks, the slug three or four words from the outcome.
7. Write Non-goals from the card's exclusions plus everything the decomposition tempted you to add and you refused.
8. Self-check before handing off: every clause of the card's acceptance maps to a task, no task names a file or symbol no task produces, and no block carries placeholder text such as "TBD", "handle edge cases", or "as in T2".
9. `--tickets`: publish the tasks to the tracker `sh <plugin root>/scripts/tracker.sh` names (`<plugin root>` is the parent of the `skills/` directory this file lives in), one ticket per task, title and body straight from the task block, and the `After` list as the blocking edges the tracker supports (`gh issue create` then `gh issue edit`; `glab issue create`; `az boards work-item create` plus `az boards work-item relation add --relation-type predecessor`). No CLI, or `auth=missing`: write `docs/tickets/<nn>-<slug>.md` instead, one file per task, edges as a `Blocked by:` line. Show every ticket and wait for the user's confirmation in this session before creating anything; never reopen or close an existing item, and print the ids or paths created.

10. Report the plan path or the brief, name the task to start with, and hand execution to the `build` skill.

Use exactly this shape, in chat or in the file:

```
Goal: <outcome from the card>
Acceptance: <the card's acceptance check>
Non-goals: <what this plan will not do>

T1 <behavior-named title>
  Paths: <owned paths, disjoint from every task that can run beside it>
  Acceptance: <check that passes only if T1 landed>
  Proof: <exact command or exercise>
  Test seam: <existing seam, or "none - repo keeps no tests for this">
  After: <task ids that must land first, or ->
```

Stop when the brief is delivered or the plan file is written. Never implement, never run a task.
