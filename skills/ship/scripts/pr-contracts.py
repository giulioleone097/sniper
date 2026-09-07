#!/usr/bin/env python3
"""Cross-domain contract check for a diff: what the diff removes, and who outside the diff still uses it.

usage: pr-contracts.py [-C REPO] [--max N] BASE HEAD

1. Exported symbols removed by the diff (TypeScript/JavaScript exports, Python top-level
   def/class, C# public members, Go exported funcs) that are not re-added elsewhere in the
   diff, with their consumers at HEAD in files the diff does not touch.
2. Deleted files, with residual references to their module name at HEAD outside the diff.
Consumers in the diff's own files are ignored: the author already updated them.
"""
import argparse
import re
import subprocess
from pathlib import PurePosixPath

PATTERNS = [
    re.compile(r"^\s*export\s+(?:default\s+)?(?:async\s+)?(?:function\*?|const|let|var|class|interface|type|enum)\s+([A-Za-z_$][\w$]*)"),
    re.compile(r"^(?:async\s+)?(?:def|class)\s+([A-Za-z_]\w*)"),
    re.compile(r"^\s*public\s+(?:static\s+|virtual\s+|override\s+|async\s+|readonly\s+|sealed\s+|abstract\s+)*[\w<>\[\],.?\s]+?\s+([A-Z]\w*)\s*[({=]"),
    re.compile(r"^func\s+(?:\([^)]*\)\s*)?([A-Z]\w*)"),
]
NOISE = {"main", "test", "Test", "index", "__init__", "setup", "run"}
CODE = ["*.py", "*.pyi", "*.ts", "*.tsx", "*.js", "*.mjs", "*.cjs", "*.cs", "*.go", "*.rs", "*.java", "*.kt",
        "*.yaml", "*.yml", "*.json", "*.toml", "*.html", "*.sql", "*.sh", "*.md"]


def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True).stdout


def symbols(line):
    for p in PATTERNS:
        m = p.match(line)
        if m and m.group(1) not in NOISE:
            return m.group(1)
    return None


def consumers(repo, head, names, changed, chunk=150):
    """Map each name to the files at HEAD outside the diff that mention it as a whole word (one git grep per chunk)."""
    hits = {n: set() for n in names}
    names = sorted(names, key=len, reverse=True)
    keys = [(n, re.compile("^" + (n if "[./]" in n else re.escape(n)) + "$")) for n in names]
    for i in range(0, len(names), chunk):
        alt = "|".join(n if "[./]" in n else re.escape(n) for n in names[i:i + chunk])
        out = git(repo, "grep", "-I", "-o", "-w", "-E", alt, head, "--", *CODE, ":!*.lock", ":!*.min.js", ":!*.min.css", ":!*.map")
        for line in out.splitlines():
            try:
                _, path, match = line.split(":", 2)
            except ValueError:
                continue
            if path in changed:
                continue
            if match in hits:
                hits[match].add(path)
            else:
                for n, rx in keys:
                    if rx.match(match):
                        hits[n].add(path)
                        break
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-C", dest="repo", default=".")
    ap.add_argument("--max", type=int, default=400, help="max removed symbols to check")
    ap.add_argument("base")
    ap.add_argument("head")
    a = ap.parse_args()

    changed = set(git(a.repo, "diff", "--name-only", a.base, a.head).splitlines())
    removed, added, current = {}, set(), None
    for raw in git(a.repo, "diff", "-U0", "--no-color", a.base, a.head).splitlines():
        if raw.startswith("+++ "):
            current = raw[6:] if raw.startswith("+++ b/") else None
        elif raw.startswith("--- ") or raw.startswith("@@"):
            continue
        elif raw.startswith("+"):
            s = symbols(raw[1:])
            if s:
                added.add(s)
        elif raw.startswith("-"):
            s = symbols(raw[1:])
            if s and current:
                removed.setdefault(s, current)
    gone = {s: f for s, f in removed.items() if s not in added}

    print(f"removed exported symbols: {len(removed)} seen, {len(gone)} not re-added in the diff")
    names = sorted(gone)[: a.max]
    deleted = [l.split("\t", 1)[1] for l in git(a.repo, "diff", "--name-status", a.base, a.head).splitlines() if l.startswith("D\t")]
    # a deleted module is referenced as "<parent>/<stem>" or "<parent>.<stem>", never as the bare stem
    stems = {}
    for p in deleted:
        pp = PurePosixPath(p)
        if len(pp.stem) >= 3 and pp.stem not in NOISE and pp.parent.name:
            stems[f"{pp.parent.name}[./]{pp.stem}"] = p
    hits = consumers(a.repo, a.head, set(names) | set(stems), changed)
    flagged = 0
    for name in names:
        files = sorted(hits[name])
        if files:
            flagged += 1
            print(f"  {name}  (was in {gone[name]})  consumers outside diff: {len(files)}  {' '.join(files[:3])}")
    print(f"  -> {flagged} removed symbols still referenced outside the diff")
    print(f"\ndeleted files: {len(deleted)}")
    stale = 0
    for stem, path in sorted(stems.items(), key=lambda kv: kv[1]):
        files = sorted(hits[stem])
        if files:
            stale += 1
            print(f"  {path}  residual references outside diff: {len(files)}  {' '.join(files[:3])}")
    print(f"  -> {stale} deleted files still referenced outside the diff (judge each: a test asserting absence is fine)")


if __name__ == "__main__":
    main()
