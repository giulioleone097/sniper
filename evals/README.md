# Evals

The question the plugin has to answer is not "does the text sound right" but "does a real session leave better code behind". Each cell here is one headless Claude Code session (`claude -p`) in a temporary workspace seeded with a starter file, run with `--bare` (none of the user's settings, memory, hooks or other plugins), with either nothing loaded (baseline) or sniper loaded through `--plugin-dir` plus its doctrine as an appended system prompt, since bare mode skips the hook that would inject it. The files the session leaves are scored deterministically, stdlib only.

Every task ships a `good` and a `bad` reference. `bad` is the plausible lazy version, right on the happy path and wrong on the axis the task probes, so a binary correctness gate would pass it. `python3 evals/run.py --selftest` proves the good reference passes and the bad one is caught before any model call; `scripts/check.sh` runs that selftest, so a scorer that stops discriminating fails the plugin's own acceptance.

| task | the job, as a ticket reads | the axis | the lazy version that must be caught |
|---|---|---|---|
| `safe-path` | join an upload filename onto a base directory | safe: `../../etc/passwd` must not escape | plain `os.path.join` |
| `trace-transfer` | "transfers can push an account below zero" | root cause: the shared `_debit` is guarded, so the unnamed `withdraw` path is fixed too | a guard in `transfer` only |
| `rate-limit` | a per-client limiter for an API with abusive clients | safe: one client's quota must not block another | one global counter |

Metrics per cell: `correct`, `safe`, source lines (tests excluded and tracked apart, since leaving a check behind is what the doctrine asks for), whether a test was written, cost and duration from the CLI's JSON.

```bash
python3 evals/run.py --selftest                      # no API, always first
python3 evals/run.py --runs 3                        # both arms, all tasks
python3 evals/run.py --tasks trace-transfer --arms sniper --runs 5
python3 evals/run.py --rescore evals/runs/<stamp>    # re-score kept workspaces, no API
```

A live run needs `ANTHROPIC_API_KEY` in the environment: bare mode reads no OAuth login. Workspaces are kept under `evals/runs/<stamp>/` (ignored by git) so a scorer change never costs the API twice.

Method distilled from DietrichGebert/ponytail `benchmarks/agentic/`: real sessions rather than single completions, seeded files so a session that narrates "done" without acting scores wrong, implicit safety requirements the way tickets read, and instruments proven on references before any spend.
