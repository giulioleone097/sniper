#!/usr/bin/env python3
"""atlas evals: does the plugin change what a real headless Claude Code session leaves behind?

Each cell is one `claude -p` session in a temp workspace seeded with a starter file, run
in a bare session (nothing from the user's settings or other plugins) with no plugin
(baseline), current atlas, or an optional previous plugin directory. Disk output is scored
deterministically by evals/tasks.py; the delta between arms is the point.

  python3 run.py --selftest             prove every scorer: good passes, bad is caught. No API.
  python3 run.py --runs 3               live run, all tasks, both arms (spends API; needs ANTHROPIC_API_KEY, bare mode reads no login)
  python3 run.py --tasks safe-path --arms atlas --runs 1
  python3 run.py --rescore runs/<stamp> re-score kept workspaces after a scorer change. No API.

Nothing here is installed, indexed or written outside evals/runs/.
"""
import argparse
import contextlib
import datetime
import io
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
INSTRUCTIONS = ("Edit the files in place and use existing checks where useful. "
                "Do not run servers or install anything. Only files and CLI metrics are scored.")
ARMS = ("baseline", "atlas", "previous")


def core_file(plugin_dir):
    # SNIPER.md: a --previous-plugin dir preserved from before the rename still carries it
    for name in ("ATLAS.md", "SNIPER.md"):
        p = plugin_dir / "core" / name
        if p.is_file():
            return p
    return plugin_dir / "core" / "ATLAS.md"


def selftest():
    failed = 0
    for name, t in TASKS.items():
        references = [("good", t["good"]), ("bad", t["bad"]), *t.get("good_variants", {}).items()]
        for label, reference in references:
            expect_pass = label != "bad"
            with tempfile.TemporaryDirectory() as d:
                for fname, content in t["seed"].items():
                    (Path(d) / fname).write_text(content)
                for fname, content in (reference if isinstance(reference, dict) else {t["file"]: reference}).items():
                    (Path(d) / fname).write_text(content)
                r = t["score"](Path(d))
                axis = "correct" if t["axis"] == "correct" else "safe"
                ok = bool(r[axis]) == expect_pass and (r["correct"] == 1)
                if label == "bad" and t["axis"] != "correct":
                    ok = r["correct"] == 1 and r["safe"] == 0
                print(f"{'ok  ' if ok else 'FAIL'} {name:15s} {label:4s} {r}")
                failed += 0 if ok else 1
    # Missing and partial CLI costs previously appeared as free runs.
    rows = [dict(task="report", arm="baseline", correct=1, safe=1, src_loc=1, wrote_test=False)] * 2
    with contextlib.redirect_stdout(io.StringIO()) as output:
        summary = aggregate(rows)
    ok = summary[0]["total_cost_usd"] == {"median": None, "available": 0, "total": 2} and "unavailable(0/2)" in output.getvalue()
    partial = [dict(rows[0], total_cost_usd=0.25), rows[1]]
    with contextlib.redirect_stdout(io.StringIO()) as output:
        summary = aggregate(partial)
    ok = ok and summary[0]["total_cost_usd"] == {"median": 0.25, "available": 1, "total": 2} and "0.250(1/2)" in output.getvalue()
    print(f"{'ok  ' if ok else 'FAIL'} missing/partial cost reporting")
    failed += not ok
    print(f"selftest: {'ok' if not failed else f'{failed} failing'}")
    return failed == 0


def run_cell(task, arm, model, keep_dir, plugin_dir):
    work = Path(tempfile.mkdtemp(prefix=f"atlas-eval-{task}-{arm}-"))
    for fname, content in TASKS[task]["seed"].items():
        (work / fname).write_text(content)
    # --bare: no user settings, memory, other plugins or hooks, so both arms start equal. Hooks off
    # means the doctrine is not injected by the plugin's own hook: the atlas arm carries it as an
    # appended system prompt, and its skills and agents through --plugin-dir.
    cmd = ["claude", "-p", TASKS[task]["prompt"] + "\n\n" + INSTRUCTIONS, "--bare",
           "--output-format", "json", "--max-turns", "12", "--dangerously-skip-permissions"]
    if model:
        cmd += ["--model", model]
    if plugin_dir is not None:
        cmd += ["--plugin-dir", str(plugin_dir), "--append-system-prompt-file", str(core_file(plugin_dir))]
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
    code = list(work.rglob("*.py"))
    checks = {f for f in code if f.name.startswith("test_") or f.name == "check.py" or "tests" in f.relative_to(work).parts}
    src = sum(1 for f in code if f not in checks for line in f.read_text().splitlines() if line.strip())
    tests = any(f.relative_to(work).as_posix() not in TASKS[task]["seed"] for f in checks)
    row = dict(task=task, arm=arm, model=model or "default", plugin_dir=str(plugin_dir) if plugin_dir else None,
               **score, src_loc=src, wrote_test=tests, **meta)
    dest = keep_dir / f"{task}-{arm}-{datetime.datetime.now().strftime('%H%M%S%f')}"
    shutil.copytree(work, dest)
    (dest / "result.json").write_text(json.dumps(row, indent=2))
    shutil.rmtree(work, ignore_errors=True)
    return row


def aggregate(rows):
    by = {}
    for r in rows:
        by.setdefault((r["task"], r["arm"]), []).append(r)
    summaries = []
    print(f"{'task':15s} {'arm':9s} {'n':>2s} {'correct':>8s} {'safe':>5s} {'src_loc':>8s} {'tests':>6s} cost_usd duration_ms turns (median; available/total)")
    for (task, arm), rs in sorted(by.items()):
        n = len(rs)
        metrics, display = {}, []
        for key in ("total_cost_usd", "duration_ms", "num_turns"):
            values = [r[key] for r in rs if r.get(key) is not None]
            median = statistics.median(values) if values else None
            metrics[key] = dict(median=median, available=len(values), total=n)
            display.append((f"{median:.3f}" if median is not None else "unavailable") + f"({len(values)}/{n})")
        summaries.append(dict(task=task, arm=arm, **metrics))
        print(f"{task:15s} {arm:9s} {n:2d} {sum(r['correct'] for r in rs)/n:8.2f} {sum(r['safe'] for r in rs)/n:5.2f} "
              f"{statistics.median(r['src_loc'] for r in rs):8.0f} {sum(r['wrote_test'] for r in rs)/n:6.2f} " + " ".join(display))
    return summaries


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
    ap.add_argument("--arms", help="comma-separated baseline,atlas,previous; previous is included by default when supplied")
    ap.add_argument("--previous-plugin", type=Path, help="previous plugin directory to compare using the same model and tasks")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--model", default=None)
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if a.rescore:
        rescore(a.rescore)
        return
    tasks = a.tasks.split(",")
    arms = a.arms.split(",") if a.arms else list(ARMS if a.previous_plugin else ARMS[:2])
    if set(tasks) - TASKS.keys() or set(arms) - set(ARMS) or a.runs < 1:
        ap.error("choose known tasks and arms, with --runs at least 1")
    if "previous" in arms and a.previous_plugin is None:
        ap.error("the previous arm requires --previous-plugin")
    if a.previous_plugin:
        a.previous_plugin = a.previous_plugin.resolve()
        if not (a.previous_plugin / ".claude-plugin/plugin.json").is_file() or not core_file(a.previous_plugin).is_file():
            ap.error("--previous-plugin must contain core/ATLAS.md (or a pre-rename core/SNIPER.md) and .claude-plugin/plugin.json")
    if not selftest():
        sys.exit("scorers failed their selftest; not spending on a live run")
    keep = RUNS / datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    keep.mkdir(parents=True)
    rows = []
    for task in tasks:
        for arm in arms:
            for _ in range(a.runs):
                row = run_cell(task, arm, a.model, keep, {"baseline": None, "atlas": ROOT, "previous": a.previous_plugin}[arm])
                rows.append(row)
                print(json.dumps(row))
    (keep / "aggregate.json").write_text(json.dumps(rows, indent=2))
    (keep / "summary.json").write_text(json.dumps(aggregate(rows), indent=2))
    print(f"kept under {keep}")


if __name__ == "__main__":
    main()
