# Evals

Each cell is one headless Claude Code session (`claude -p`) in a temporary workspace, run with `--bare` (no user settings, memory, hooks or other plugins). Arms use no plugin (`baseline`), the current repository (`atlas`), and optionally `--previous-plugin` (`previous`). Plugin arms load that directory's skills and doctrine. The same runner, model argument, tasks and limits apply to every arm. Files are scored deterministically, stdlib only.

Every task ships a `good` and a `bad` reference. `bad` is the plausible lazy version, right on the happy path and wrong on the axis the task probes, so a binary correctness gate would pass it. `python3 evals/run.py --selftest` proves the good reference passes and the bad one is caught before any model call; `scripts/check.sh` runs that selftest, so a scorer that stops discriminating fails the plugin's own acceptance.

| task | the job, as a ticket reads | the axis | the lazy version that must be caught |
|---|---|---|---|
| `safe-path` | join an upload filename onto a base directory | safe: `../../etc/passwd` must not escape | plain `os.path.join` |
| `trace-transfer` | "transfers can push an account below zero" | root cause: the shared `_debit` is guarded, so the unnamed `withdraw` path is fixed too | a guard in `transfer` only |
| `rate-limit` | a per-client limiter for an API with abusive clients | safe: one client's quota must not block another | one global counter |
| `bounded-fix` | subtotal skips the first price; an existing check covers it | scope: fix validated-list calculation without redundant tests, fallback branches or extra helpers | correct sum plus a speculative null fallback and duplicate test |
| `domain-port` | invoice total ignores quantities | boundary: keep the existing injected catalog protocol and JSON adapter separation | correct total but deleted protocol because it has only one production implementation |

Metrics per cell: `correct`, `safe` (the secondary axis named above), source lines excluding checks, whether an additional test was written, and cost, duration and turns reported by the CLI. Missing metrics stay unavailable. Console output and `summary.json` give each metric's median over available cells and its `available/total` coverage; partial costs are not full-run costs. `aggregate.json` retains raw rows. New tests and fewer lines are descriptive metrics, not universal quality scores.

Scorers cover these concrete fixtures only: the subtotal probe has validated inputs and complete existing checks; the domain probe already has an IO port. They do not justify omitting needed validation or adding architecture elsewhere. Correctness and the task's secondary axis gate any cost or speed comparison. User interventions and prompt counts are not measured by this runner.

```bash
python3 evals/run.py --selftest                      # no API, always first
python3 evals/run.py --runs 3                        # both arms, all tasks
python3 evals/run.py --tasks trace-transfer --arms atlas --runs 5
python3 evals/run.py --previous-plugin /path/to/previous-atlas --model MODEL --runs 3
python3 evals/run.py --rescore evals/runs/<stamp>    # re-score kept workspaces, no API
```

A live run needs `ANTHROPIC_API_KEY` in the environment: bare mode reads no OAuth login. Workspaces are kept under `evals/runs/<stamp>/` (ignored by git) so a scorer change never costs the API twice.

For a version comparison, preserve the previous plugin directory before editing, select an explicit model, and pass `--previous-plugin`. All three arms run by default; `--arms atlas,previous` skips the no-plugin baseline. The selftest and CLI validation use no API. Live results must be collected before claiming efficiency gains.

Method distilled from DietrichGebert/ponytail `benchmarks/agentic/`: real sessions rather than single completions, seeded files so a session that narrates "done" without acting scores wrong, implicit safety requirements the way tickets read, and instruments proven on references before any spend.
