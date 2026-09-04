#!/usr/bin/env python3
"""Partition a git diff into review buckets so a reader knows where judgment lives.

usage: pr-partition.py [-C REPO] [--json] [--top N] BASE HEAD

Buckets, first match wins: generated (binary, linguist-generated, lockfiles,
build output, snapshots), mechanical (rename with >= 90% similarity, or a
whitespace-only change), tests, docs, config, judgment (everything else: the
code a human has to think about).
"""
import argparse
import json
import re
import subprocess
from collections import defaultdict

GENERATED = re.compile(
    r"(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|poetry\.lock|uv\.lock|Cargo\.lock|go\.sum|"
    r"composer\.lock|Pipfile\.lock|packages\.lock\.json)$"
    r"|\.(min\.js|min\.css|map|snap|lock|pb\.go|g\.cs|g\.ts|designer\.cs|generated\.\w+)$|_pb2(_grpc)?\.py$"
    r"|(^|/)(dist|build|out|vendor|node_modules|__snapshots__|__generated__|generated|codegen|coverage|"
    r"\.nx|\.angular|obj|bin)/",
    re.I,
)
TESTS = re.compile(
    r"(^|/)(tests?|__tests__|specs?|e2e|fixtures?|__fixtures__|testdata|golden)/"
    r"|[._-](test|tests|spec|e2e)\.\w+$|Tests?\.cs$|_test\.(go|py|rs)$|(^|/)test_[^/]+\.py$|(^|/)conftest\.py$",
    re.I,
)
DOCS = re.compile(r"\.(md|mdx|rst|adoc|txt)$|(^|/)docs?/", re.I)
CONFIG = re.compile(
    r"(^|/)(\.github|\.gitlab|\.azure|\.circleci|\.vscode|\.idea|\.devcontainer|deploy|helm|k8s|terraform|infra)/"
    r"|(^|/)(Dockerfile[^/]*|docker-compose[^/]*|Makefile|Justfile|\.gitattributes|\.gitignore|\.editorconfig|"
    r"\.env[^/]*|\.pre-commit-config\.yaml)$"
    r"|\.(ya?ml|toml|ini|cfg|conf|props|targets|csproj|sln|nuspec|json|xml|env)$",
    re.I,
)
ORDER = ["judgment", "tests", "mechanical", "generated", "docs", "config"]


def git(repo, *args, stdin=None):
    r = subprocess.run(["git", "-C", repo, *args], input=stdin, capture_output=True, text=True)
    if r.returncode != 0:
        first = next((l for l in r.stderr.splitlines() if l.strip()), "unknown error")
        raise SystemExit(f"pr-partition: git {' '.join(args[:3])} failed in {repo}: {first}")
    return r.stdout


def rename_new(path):
    """Normalise a numstat rename path ('a/{old => new}/b', 'old => new') to the new path."""
    if "{" in path and " => " in path and "}" in path:
        pre, rest = path.split("{", 1)
        mid, post = rest.split("}", 1)
        return (pre + mid.split(" => ")[1] + post).replace("//", "/")
    if " => " in path:
        return path.split(" => ")[1]
    return path


def numstat(repo, base, head, *flags):
    out = {}
    for line in git(repo, "diff", "--numstat", "-M90", *flags, base, head).splitlines():
        add, dele, path = line.split("\t", 2)
        out[rename_new(path)] = (None if add == "-" else int(add), None if dele == "-" else int(dele))
    return out


def bucket(path, add, dele, status, generated_attr, ws_zero):
    if generated_attr or add is None or GENERATED.search(path):
        return "generated"
    if status.startswith("R") and int(status[1:] or "100") >= 90:
        return "mechanical"
    if ws_zero and (add or dele):
        return "mechanical"
    if TESTS.search(path):
        return "tests"
    if DOCS.search(path):
        return "docs"
    if CONFIG.search(path):
        return "config"
    return "judgment"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-C", dest="repo", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("base")
    ap.add_argument("head")
    a = ap.parse_args()

    stats = numstat(a.repo, a.base, a.head)
    ws = numstat(a.repo, a.base, a.head, "-w")
    status = {}
    for line in git(a.repo, "diff", "--name-status", "-M90", a.base, a.head).splitlines():
        parts = line.split("\t")
        status[parts[-1]] = parts[0]
    attr = {}
    for line in git(a.repo, "check-attr", "--stdin", "linguist-generated", stdin="\n".join(stats)).splitlines():
        path, _, value = line.rsplit(": ", 2)
        attr[path] = value == "true"

    files = []
    for path, (add, dele) in stats.items():
        ws_zero = ws.get(path, (1, 1)) == (0, 0)
        b = bucket(path, add, dele, status.get(path, "M"), attr.get(path, False), ws_zero)
        files.append({"path": path, "bucket": b, "add": add or 0, "del": dele or 0, "status": status.get(path, "M")})

    totals = {b: [0, 0, 0] for b in ORDER}
    dirs = defaultdict(lambda: [0, 0])
    for f in files:
        t = totals[f["bucket"]]
        t[0] += 1
        t[1] += f["add"]
        t[2] += f["del"]
        if f["bucket"] == "judgment":
            d = "/".join(f["path"].split("/")[:3])
            dirs[d][0] += f["add"] + f["del"]
            dirs[d][1] += 1
    judgment = sorted((f for f in files if f["bucket"] == "judgment"), key=lambda f: -(f["add"] + f["del"]))
    top_dirs = sorted(dirs.items(), key=lambda kv: -kv[1][0])[: a.top]

    if a.json:
        print(json.dumps({"base": a.base, "head": a.head, "buckets": {b: {"files": t[0], "add": t[1], "del": t[2]} for b, t in totals.items()},
                          "judgment_dirs": [{"dir": d, "lines": v[0], "files": v[1]} for d, v in top_dirs], "files": files}, indent=1))
        return

    print(f"{'bucket':<11}{'files':>6}{'+add':>9}{'-del':>9}")
    for b in ORDER:
        t = totals[b]
        print(f"{b:<11}{t[0]:>6}{t[1]:>9}{t[2]:>9}")
    print(f"{'total':<11}{len(files):>6}{sum(f['add'] for f in files):>9}{sum(f['del'] for f in files):>9}")
    print("\njudgment by directory (lines, files):")
    for d, (lines, n) in top_dirs:
        print(f"{lines:>8} {n:>5}  {d}")
    print(f"\njudgment files by churn (top {a.top}):")
    for f in judgment[: a.top]:
        print(f"+{f['add']:<6}-{f['del']:<6} {f['path']}")


if __name__ == "__main__":
    main()
