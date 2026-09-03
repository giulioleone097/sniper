# fix

The cause is known, or one run away. When it is not, run `debug` first and come back with the chain.

1. Reproduce the failure before editing whenever reproduction is cheap: exact trigger, expected value, actual value. When it is not cheap, capture the strongest evidence available and say which one you have.
2. Trace the symptom to the mechanism that owns the wrong behavior. Change that layer, not the caller that happened to notice.
3. Fix at the point every caller routes through, per core. A guard added at one call site leaves the defect live at every other.
4. Preserve unrelated behavior and any uncommitted user edits in the files you touch.
5. Keep cleanup, renaming, and abstraction out of the fix.
6. Above five identical occurrences, transform them with a codemod (`ast-grep`, `comby`, `jscodeshift`, `ts-morph`, `libcst`) rather than by hand.
7. Add a regression test only at a seam that exercises the real bug pattern as it occurs at the call site. A seam too shallow to reproduce the chain gives false confidence: when none exists, report that absence as a finding instead of writing the shallow test.
8. Two failed attempts: instrument, per core. Or hand the failure to `debug`.

Proof: the reproduction now passes, plus the nearest existing check that already covers the changed file.
