# Shrink: smaller without changing behavior

Read when changed code is about to be reviewed, or when a simplify pass was asked for by name. Read the code and trace the flow it touches end to end before cutting anything, per core: the ladder shortens the solution, never the reading.

Walk each hunk down the rungs in order and stop at the first that holds. Each rung is one output tag:

1. `reuse:` a helper, type, or pattern already in this repository does it. Call that instead.
2. `stdlib:` the standard library or an already-installed dependency does it. Name it and use it.
3. `native:` a platform feature or a database constraint does it. Name it and use it. `platform-native.md` beside this file is the lookup for this rung and the one above: browser, Node, Python, Swift, database.
4. `delete:` dead code, an unused flag, config nobody sets. Remove it, and the tests that exist only for it.
5. `yagni:` an abstraction with one implementation, a wrapper that only delegates, a layer with one caller, or anything else on core's never-add list. Collapse it into its one caller.
6. `shrink:` same logic, fewer lines. Rename or flatten only where it lowers the cost of reading that function, never as a sweep across the diff.

Apply the cuts directly, surgical and behavior-preserving. Skip any cut whose behavior preservation you cannot establish, and never thin the guards core lists as never-remove. A kept limit (a global lock, a linear scan, a naive heuristic) gets a `ceiling:` comment naming the limit and the upgrade trigger, per core. Boring over clever: a shorter line that takes longer to read is not a win. The one runnable check core asks for where a repository keeps no tests is not slop; leave it.
