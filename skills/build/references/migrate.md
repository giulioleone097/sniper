# migrate

A transition between two shapes, reversible at every stage.

1. Map first: current readers, current writers, the data shape, the compatibility window, and who owns each side. Do not edit until that map exists.
2. Define the forward path and the rollback path together. A stage with no rollback is a stage that is not ready.
3. Sequence expand, migrate, verify, contract. Run only the stage that was requested; never contract implicitly.
4. Preserve existing data. Destructive steps — dropping a column, deleting rows, removing an endpoint — need separate explicit authorization: list them and stop.
5. Keep mixed-version operation safe while old and new run together: the old reader must survive the new writer's output for the whole rollout window.
6. Make every step idempotent so a retry is safe, and make partial failure observable rather than silent.
7. Verify both paths at the transition: the old path still works, the new path produces the expected shape.

Proof: the requested stage runs forward, the rollback runs, and both readers see correct data.
