#!/usr/bin/env python3
"""Post inline walkthrough comments on a pull request as one review.

usage: pr-walkthrough.py OWNER/REPO NUMBER comments.json [--post] [-C REPO_PATH]

comments.json: [{"path": "src/x.py", "line": 42, "body": "why this decision"}]
`line` is a new-file line number that appears in the PR diff. Without --post
the script validates every comment against the diff and prints the payload;
with --post it submits one COMMENT review carrying the marker below.
`gh pr diff` refuses very large PRs; pass -C with a local checkout that has the
PR refs fetched and the diff is read from git instead.
"""
import json
import re
import subprocess
import sys

MARKER = "<!-- sniper:narrate walkthrough -->"


def gh(*args, stdin=None):
    return subprocess.run(["gh", *args], input=stdin, capture_output=True, text=True, check=True).stdout


def raw_diff(repo, number, local, paths):
    if local is None:
        return gh("pr", "diff", number, "-R", repo)
    base = gh("pr", "view", number, "-R", repo, "--json", "baseRefName", "--jq", ".baseRefName").strip()
    git = ["git", "-C", local]
    run = lambda *a: subprocess.run([*git, *a], capture_output=True, text=True, check=True).stdout.strip()
    run("fetch", "-q", "origin", f"+refs/heads/{base}:refs/remotes/origin/{base}", f"+refs/pull/{number}/head:refs/remotes/origin/pr/{number}")
    head = f"origin/pr/{number}"
    return run("diff", run("merge-base", f"origin/{base}", head), head, "--", *paths)


def diff_lines(repo, number, local, paths):
    """Map path -> set of right-side line numbers present in the diff hunks."""
    lines, current, new, in_hunk = {}, None, 0, False
    for raw in raw_diff(repo, number, local, paths).splitlines():
        if raw.startswith("diff --git"):
            in_hunk = False
            continue
        if raw.startswith("+++ "):
            current = raw[6:] if raw.startswith("+++ b/") else None
            in_hunk = False
            continue
        if raw.startswith("@@"):
            new = int(re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", raw).group(1))
            in_hunk = current is not None
            if in_hunk:
                lines.setdefault(current, set())
            continue
        if not in_hunk or raw.startswith("-") or raw.startswith("\\"):
            continue
        lines[current].add(new)
        new += 1
    return lines


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    repo, number, path = sys.argv[1:4]
    post = "--post" in sys.argv
    local = sys.argv[sys.argv.index("-C") + 1] if "-C" in sys.argv else None
    comments = json.load(open(path))
    valid = diff_lines(repo, number, local, sorted({c["path"] for c in comments}))
    errors = []
    for c in comments:
        if c["path"] not in valid:
            errors.append(f"{c['path']}: not in the PR diff")
        elif c["line"] not in valid[c["path"]]:
            near = sorted(valid[c["path"]])
            errors.append(f"{c['path']}:{c['line']}: not a diff line (diff covers {near[0]}..{near[-1]})")
    if errors:
        sys.exit("invalid comments:\n" + "\n".join(errors))
    payload = {
        "event": "COMMENT",
        "body": MARKER + "\nWalkthrough: the reason behind each decision, at the line where it lives.",
        "comments": [{"path": c["path"], "line": c["line"], "side": "RIGHT", "body": c["body"]} for c in comments],
    }
    if not post:
        print(json.dumps(payload, indent=1))
        print(f"\n{len(comments)} comments valid; add --post to submit", file=sys.stderr)
        return
    out = gh("api", "-X", "POST", f"repos/{repo}/pulls/{number}/reviews", "--input", "-", stdin=json.dumps(payload))
    print(json.loads(out).get("html_url", out))


if __name__ == "__main__":
    main()
