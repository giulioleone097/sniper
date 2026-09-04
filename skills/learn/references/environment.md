# Retro: improve the environment, not the code

Use when the user asks for a retrospective on a session rather than a rule about the code. The subject is what the next agent will find waiting for it. Read the session's own record first; a category with no evidence in that record is not a candidate.

Rank candidates by what actually cost time in that session, and present them before changing anything. One accepted candidate per run, same as a learning.

| Category | Look for | Trigger |
|---|---|---|
| Navigation | the search that took many tries, the file nobody could find, the hidden dependency between two files | the session spent more than a few tool calls locating something |
| Automated check | the mistake a typecheck, lint rule, or test would have caught for free | a defect reached review that a machine could have caught |
| Review rule | the standard the reviewer missed, or the rule that fired on something harmless | the review missed a real defect, or flagged noise twice |
| Steering weight | instructions in AGENTS.md or CLAUDE.md that steer nothing, or that belong in a review rule instead | the file is long and the session ignored parts of it |
| Tool economy | the command whose output flooded the context, the tool called in a loop, the query that returned a whole file to read one line | one call cost a visible share of the window |
| Information access | the fact that existed but was not reachable: a log the agent could not read, a service with no read-only access | a question was answered by guessing because the source was out of reach |

Two rules decide where a fix lands. Implementation carries the context pressure, so it gets navigation pointers and cheaper tools; review sees only a diff, so it gets the standards. And a steering file earns its lines by changing behavior: an instruction that no session has ever acted on is deleted, not reworded.

Write the accepted candidate the way `learn` writes anything: the smallest durable change, in the file that owns it, shown to the user before it is written.
