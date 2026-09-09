# Shrink: smaller without changing behavior

Read when changed code is about to be reviewed, or when a simplify pass was asked for by name. Read the code and trace the flow it touches end to end before cutting anything, per core: the ladder shortens the solution, never the reading.

Walk each hunk down the rungs in order and stop at the first that holds. Before cutting a guard, a branch or a check the diff removes or weakens, read its history (`git log -L<start>,<end>:<path>` or `git blame`): a line that landed as a fix stays, and its commit is cited when the cut is refused. Each rung is one output tag:

1. `reuse:` a helper, type, or pattern already in this repository does it. Call that instead.
2. `stdlib:` the standard library or an already-installed dependency does it. Name it and use it.
3. `native:` a platform feature or a database constraint does it. Name it and use it. `platform-native.md` beside this file is the lookup for this rung and the one above: browser, Node, Python, Swift, database.
4. `delete:` dead code, an unused flag, config nobody sets. Remove it, and the tests that exist only for it. `slop.md` beside this file is the catalog for this rung and the next: the patterns, the rung that cuts each, and the case where it stays.
5. `yagni:` an abstraction, wrapper or layer with no concrete responsibility, boundary or variation to protect. Collapse it only when that purpose is absent; one implementation or caller alone is not evidence of waste.
6. `shrink:` same logic, fewer lines, only where it lowers the cost of reading that function; rename or flatten never as a sweep across the diff.

Apply cuts within the requested scope, surgical and behavior-preserving. Skip any cut whose behavior preservation you cannot establish; keep core's safety guards and meaningful domain/I/O boundaries. A kept deliberate limit gets a `ceiling:` comment naming the limit and upgrade trigger, per core. Keep tests that catch a meaningful regression; do not invent edge cases to justify more code.
