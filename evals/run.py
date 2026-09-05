#!/usr/bin/env python3
"""sniper evals: does the plugin change what a real headless Claude Code session leaves behind?

Each cell is one `claude -p` session in a temp workspace seeded with a starter file, run
in a bare session (nothing from the user's settings or other plugins) with either no plugin
(baseline) or sniper loaded through --plugin-dir. What the session leaves on disk is scored
deterministically by evals/tasks.py; the delta between arms is the point.

  python3 run.py --selftest             prove every scorer: good passes, bad is caught. No API.
  python3 run.py --runs 3               live run, all tasks, both arms (spends API; needs ANTHROPIC_API_KEY, bare mode reads no login)
  python3 run.py --tasks safe-path --arms sniper --runs 1
  python3 run.py --rescore runs/<stamp> re-score kept workspaces after a scorer change. No API.

Nothing here is installed, indexed or written outside evals/runs/.
"""
import argparse
import datetime
import json
import os
import shutil
import statistics
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tasks import TASKS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RUNS = Path(__file__).resolve().parent / "runs"
CELL_TIMEOUT = 300
# The agent writes code and stops; execution is what the scorer does, identically for every arm.
NO_RUN = ("Edit the file in place, include a test only if you normally would for a change like this, "
          "do not run servers or install anything. Only what you write is measured.")
ARMS = ("baseline", "sniper")


def selftest():
    failed = 0
    for name, t in TASKS.items():
        for label, expect_pass in (("good", True), ("bad", False)):
            with tempfile.TemporaryDirectory() as d:
                (Path(d) / t["file"]).write_text(t[label])
                r = t["score"](Path(d))
                axis = "correct" if t["axis"] == "correct" else "safe"
                ok = bool(r[axis]) == expect_pass and (r["correct"] == 1)
                if label == "bad" and t["axis"] != "correct":
                    ok = r["correct"] == 1 and r["safe"] == 0
                print(f"{'ok  ' if ok else 'FAIL'} {name:15s} {label:4s} {r}")
                failed += 0 if ok else 1
    print(f"selftest: {'ok' if not failed else f'{failed} failing'}")
    return failed == 0


def run_cell(task, arm, model, keep_dir):
    work = Path(tempfile.mkdtemp(prefix=f"sniper-eval-{task}-{arm}-"))
    for fname, content in TASKS[task]["seed"].items():
        (work / fname).write_text(content)
    # --bare: no user settings, memory, other plugins or hooks, so both arms start equal. Hooks off
    # means the doctrine is not injected by the plugin's own hook: the sniper arm carries it as an
    # appended system prompt, and its skills and agents through --plugin-dir.
    cmd = ["claude", "-p", TASKS[task]["prompt"] + "\n\n" + NO_RUN, "--bare",
           "--output-format", "json", "--max-turns", "12", "--dangerously-skip-permissions"]
    if model:
        cmd += ["--model", model]
    if arm == "sniper":
        cmd += ["--plugin-dir", str(ROOT), "--append-system-prompt-file", str(ROOT / "core" / "SNIPER.md")]
    env = dict(os.environ)
    try:
        p = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=CELL_TIMEOUT, env=env)
        meta = {}
        try:
            j = json.loads(p.stdout)
            meta = {k: j.get(k) for k in ("total_cost_usd", "duration_ms", "num_turns", "is_error")}
        except Exception:
            meta = {"raw": p.stdout[-300:], "stderr": p.stderr[-300:]}
    except subprocess.TimeoutExpired:
        meta = {"timeout": True}
    score = TASKS[task]["score"](work)
    src = sum(1 for f in work.glob("*.py") if not f.name.startswith("test_") for _ in f.read_text().splitlines() if _.strip())
    tests = any(f.name.startswith("test_") for f in work.glob("*.py"))
    row = dict(task=task, arm=arm, model=model or "default", **score, src_loc=src, wrote_test=tests, **meta)
    dest = keep_dir / f"{task}-{arm}-{datetime.datetime.now().strftime('%H%M%S%f')}"
    shutil.copytree(work, dest)
    (dest / "result.json").write_text(json.dumps(row, indent=2))
    shutil.rmtree(work, ignore_errors=True)
    return row


def aggregate(rows):
    by = {}
    for r in rows:
        by.setdefault((r["task"], r["arm"]), []).append(r)
    print(f"{'task':15s} {'arm':9s} {'n':>2s} {'correct':>8s} {'safe':>5s} {'src_loc':>8s} {'tests':>6s} {'cost':>7s}")
    for (task, arm), rs in sorted(by.items()):
        n = len(rs)
        cost = [r.get("total_cost_usd") or 0 for r in rs]
        print(f"{task:15s} {arm:9s} {n:2d} {sum(r['correct'] for r in rs)/n:8.2f} {sum(r['safe'] for r in rs)/n:5.2f} "
              f"{statistics.median(r['src_loc'] for r in rs):8.0f} {sum(r['wrote_test'] for r in rs)/n:6.2f} {statistics.median(cost):7.3f}")


def rescore(stamp_dir):
    rows = []
    for d in sorted(Path(stamp_dir).iterdir()):
        if not (d / "result.json").exists():
            continue
        old = json.loads((d / "result.json").read_text())
        old.update(TASKS[old["task"]]["score"](d))
        rows.append(old)
    aggregate(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--rescore")
    ap.add_argument("--tasks", default=",".join(TASKS))
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--model", default=None)
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if a.rescore:
        rescore(a.rescore)
        return
    if not selftest():
        sys.exit("scorers failed their selftest; not spending on a live run")
    keep = RUNS / datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    keep.mkdir(parents=True)
    rows = []
    for task in a.tasks.split(","):
        for arm in a.arms.split(","):
            for _ in range(a.runs):
                row = run_cell(task, arm, a.model, keep)
                rows.append(row)
                print(json.dumps(row))
    (keep / "aggregate.json").write_text(json.dumps(rows, indent=2))
    aggregate(rows)
    print(f"kept under {keep}")


if __name__ == "__main__":
    main()
