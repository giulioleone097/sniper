# Slop: the catalog for the `slop` lens

Read from shrink when walking the `delete:` and `yagni:` rungs, and handed to a `slop` reviewer with the diff. Each entry names the pattern, the rung that cuts it, and the case where it stays. A match is a candidate, not a verdict: trace the flow first, and keep core's never-remove list (trust-boundary validation, authorization, data-loss guards, error handling that acts, migration and rollback safety, concurrency protection, accessibility).

## Defensive
- try/except or try/catch around a local, idempotent call that only re-raises or logs: `delete:`. Stays when it converts the error at a boundary or releases a resource.
- Null or type checks on values the caller cannot produce (internal callers, typed parameters, constructor-set fields): `delete:`. Stays at a trust boundary: request bodies, files, environment, third-party responses, and anything derived from a model's output (a URL, path, query, row or text an LLM produced gets the check its source would need).
- Retries, timeouts or fallbacks around in-process work: `delete:`. Stays around a network or disk call with a stated failure mode.
- A silent default when a lookup fails (`or {}`, `.get(k, [])` hiding a missing key): `delete:` in favour of the error. Stays when the contract says the key is optional.

## Structural
- A wrapper whose body is one call with the same arguments: `yagni:`. Stays when it names a domain concept callers should not know the mechanism of.
- An interface, base class or protocol with one implementation and no boundary purpose (no test double, no plugin point, no domain/I/O seam): `yagni:`. Stays when it protects a real seam even with one implementation.
- A factory, builder or registry for one product: `yagni:`.
- Configuration, a flag or an option nobody sets outside its default: `delete:`, plumbing included. Stays when the value is read from the environment, CI or a deploy manifest, whose setters live outside this tree, unless those files (`.env*`, pipeline config, manifests, deploy checkouts) are in reach and show it unset; `git grep -w` alone does not prove nobody sets it.
- Parameters, hooks or `**kwargs` added for a caller that does not exist: `yagni:`.
- A prop, parameter or branch kept optional or widened only so tests, stories, mocks or demos can express states live callers never enter: `yagni:` narrowed to the live call sites (`git grep -w` on them, not on the support code), the support code adapting. Stays when a real caller exercises the wide case.
- A layer that passes data through unchanged (service to repository to client, one line each): `yagni:` down to the layer that does something.

## Noise
- Comments restating the line below, docstrings repeating the signature, section banners: `shrink:`. Stays when the comment says why or names a `ceiling:`.
- Logging every step of a happy path: `delete:` down to the lines an operator uses.
- Casts, type assertions and `Any` that silence the checker instead of expressing a type: `shrink:` to the real type.
- Re-exports, aliases and `__all__` entries nothing imports: `delete:`.
- Getters and setters over a public attribute with no invariant: `shrink:`.

## Tests
- Assertions mirroring the implementation line by line, or testing the framework: `delete:`.
- Edge cases no caller can reach (the impossible enum value, a negative count from a length): `delete:`.
- Mocks of the unit under test or of the standard library: `delete:` with the test, or rewrite against the real thing.
- Scratch checks and printouts committed with the change: `delete:`.

## Leftovers
- TODO or FIXME placeholders standing in for code the task needed: implement, or `delete:`.
- Compatibility shims, deprecated paths and renamed aliases for callers that do not exist (`git grep -w` says so): `delete:`.
- Unused imports, parameters, variables, dead branches after a return: `delete:`.
- Debug prints, commented-out code, feature flags whose both branches ship: `delete:`.
