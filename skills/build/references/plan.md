# Plan: four or more tasks, several owners, or a change others depend on

Read when the card's size is complex.

1. The goal card is the input; plan from it.
2. Read the code the work touches before decomposing anything. List the files each task will create or modify and what each one owns after the change. Name new files, symbols and task titles from the repo's `CONTEXT.md` when one exists.
3. Choose proof from existing checks or real exercises. Plan a new test only when indispensable under core's rule, naming the meaningful regression existing checks miss. Otherwise use `New test: none`; the existence or absence of a test suite alone decides nothing.
4. Cut a task where a reviewer could reject it and still accept its neighbour. Fold setup, configuration, and docs into the task whose deliverable needs them. Every task ends in something independently provable.
5. Assign owned paths per task. Tasks that can run beside each other must have prefix-disjoint path sets; when two tasks want the same file, order them with `After` rather than splitting the file to fake independence.
6. Count the tasks. Four or more, more than one owner, or a risk surface (authorization, payments, data migration, an external contract): write `docs/plans/<yyyy-mm-dd>-<slug>.md` in the shape below, the slug three or four words from the outcome. Otherwise the brief stays in chat, no file.
7. Write Non-goals from the card's exclusions plus everything the decomposition tempted you to add and you refused.
8. Self-check before handing off: every clause of the card's acceptance maps to a task, no task names a file or symbol no task produces, and no block carries placeholder text such as "TBD", "handle edge cases", or "as in T2".
9. `--tickets`: publish the tasks to the tracker `sh <plugin root>/scripts/tracker.sh` names (`<plugin root>` is the parent of the `skills/` directory this file lives in), one ticket per task, title and body straight from the task block, and the `After` list as the blocking edges the tracker supports (`gh issue create` then `gh issue edit`; `glab issue create`; `az boards work-item create` plus `az boards work-item relation add --relation-type predecessor`). No CLI, or `auth=missing`: write `docs/tickets/<nn>-<slug>.md` instead, one file per task, edges as a `Blocked by:` line. Show every ticket and wait for the user's confirmation in this session before creating anything; never reopen or close an existing item, and print the ids or paths created.

10. Report the plan path or the brief and name the task to start with; implementation continues from the build steps.

Use exactly this shape, in chat or in the file:

```
Goal: <outcome from the card>
Acceptance: <the card's acceptance check>
Non-goals: <what this plan will not do>

T1 <behavior-named title>
  Paths: <owned paths, disjoint from every task that can run beside it>
  Acceptance: <check that passes only if T1 landed>
  Proof: <exact command or exercise>
  New test: <none, or real regression and why existing checks miss it>
  After: <task ids that must land first, or ->
```

The plan is written before any task runs.
