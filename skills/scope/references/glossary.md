# Glossary: vocabulary that lands in CONTEXT.md

Read during a grill round the moment a term resolves: a name, a boundary, a distinction the user just settled, not a design or implementation decision.

1. Find the target file. One `CONTEXT.md` at the target repository root, most repos: write there. A `CONTEXT-MAP.md` at that root: read it, and write to the `CONTEXT.md` of the context the term belongs to, by the paths and relationships the map lists; unclear which context -> ask, in the same round, rather than guess. Neither file exists yet: the first resolved term creates the root `CONTEXT.md`; nothing is scaffolded before that first write.

2. Enforce it before resolving anything new. What the user is saying contradicts an entry already in the target file (a different meaning for the same term, a word the glossary lists under `_Avoid_` for something else) -> that contradiction, quoted against the entry, becomes the next question, not a fact accepted into the round. The user moving on without addressing it does not settle it: it stays on the frontier.

3. Write the moment a term settles, term by term. Do not batch entries for the end of the round or the session: append the entry right after the answer that resolved it lands, then keep working the round.

4. Shape each entry to match what the file already has; a file with no entries yet starts like this:

   ```
   **<Term>**: <one tight sentence — what it is, not what it does>.
   _Avoid_: <the words it replaces, when the round surfaced any>
   ```

   Group entries loosely under a `## <area>` heading only once several already share one; a single term needs no heading of its own.

5. Keep the file a pure glossary. No implementation detail, no rationale for why a term won over another, no spec prose, no scratch notes, no decision log. A choice worth keeping past this session — the rejected alternative a future reader would otherwise re-litigate — is not glossary content: `atlasme.md`'s own step for that hands it to ship's learn step. Never create an ADR directory or file for it; that path does not exist here.

6. A term that only rewords an entry already there, or a synonym the file already lists under `_Avoid_` for something else, is a rewrite of that entry, not a new one.

Stop once the round's resolved terms are all written: the file holds exactly what was settled, nothing pending, nothing invented ahead of a term actually resolving.
