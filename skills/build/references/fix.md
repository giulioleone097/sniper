# fix

The cause is known, or one run away. When it is not, run the debug reference first and come back with the chain.

1. Reproduce the failure before editing whenever reproduction is cheap: exact trigger, expected value, actual value. When it is not cheap, capture the strongest evidence available and say which one you have.
2. Trace the symptom to the mechanism that owns the wrong behavior and fix there, at the point every caller routes through, per core; not at the caller that noticed.
3. Preserve unrelated behavior and any uncommitted user edits in the files you touch.
4. Above five identical occurrences, transform them with a codemod (`ast-grep`, `comby`, `jscodeshift`, `ts-morph`, `libcst`) rather than by hand.
5. Add a regression test only when indispensable per core and only where it exercises the real bug at its observable boundary; internal mechanics or an unsupported input do not prove this repair.
6. After two failed attempts the cause is not known after all: run the debug reference instead of guessing a third time.

Proof: the reproduction or an adequate existing check now passes; add another check only for an uncovered relevant risk or a repository requirement.
