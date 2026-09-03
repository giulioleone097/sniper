# refactor

Behavior is identical before and after. Anything that changes behavior is a different task.

1. State the behavior-preservation boundary: which public interfaces, failure modes, ordering guarantees, and compatibility promises must not move.
2. Establish the proof before the first structural edit, and run the same proof after. No baseline, no refactor: find or write that check first.
3. Move one ownership boundary at a time. Keep every intermediate state buildable and testable.
4. Keep feature work, bug fixes, and dependency bumps out of the diff; list them as follow-ups.
5. Rename with the language's own tooling, or a codemod above five occurrences. Never hand-edit a bulk rename.
6. Once the new structure works, delete the superseded shape, per core.
7. Add no dependency and no configuration without a correctness need.

Proof: the same check set passes before and after. When no such check existed beforehand, say so and name what you ran in its place.
