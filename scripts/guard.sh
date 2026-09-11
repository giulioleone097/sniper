#!/bin/sh
# sniper guard: pre-execution shell hook for Claude Code (PreToolUse Bash),
# Codex (same), Devin (PreToolUse exec/write_to_process) and Cursor
# (beforeShellExecution). Denies a fixed list of destructive git/rm commands
# anywhere in the command string, including after &&, ;, |.
# See docs/DESIGN.md "Hooks" for the rule table. Any parse or unexpected
# error: print nothing, exit 0 -- never trap the user.

exec python3 -c '
import sys, json, shlex

def allow():
    sys.exit(0)

def deny(reason):
    msg = "sniper guard: " + reason
    # one payload, every host reads the fields it knows:
    # Claude Code/Codex -> hookSpecificOutput.permissionDecision
    # Devin             -> decision + reason
    # Cursor            -> permission + user_message/agent_message
    payload = {
        "decision": "block",
        "reason": msg,
        "permission": "deny",
        "user_message": msg,
        "agent_message": msg,
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": msg,
        },
    }
    sys.stdout.write(json.dumps(payload))
    sys.exit(0)

try:
    raw = sys.stdin.read()
    data = json.loads(raw)
except Exception:
    allow()

# Claude/Devin send tool_input.command; Devin write_to_process sends
# text_input/bytes_input; Cursor beforeShellExecution sends command at top level.
ti = data.get("tool_input") if isinstance(data, dict) else None
if not isinstance(ti, dict):
    ti = {}
cmd = (
    ti.get("command")
    or ti.get("text_input")
    or ti.get("bytes_input")
    or (data.get("command") if isinstance(data, dict) else None)
    or ""
)

if not isinstance(cmd, str) or not cmd.strip():
    allow()

try:
    lexer = shlex.shlex(cmd, posix=True, punctuation_chars=True)
    lexer.wordchars += "${}"
    tokens = list(lexer)
except ValueError:
    allow()

OPERATORS = set("&|;()")
FORBIDDEN_RM_TARGETS = {"/", "~", "$HOME", ".", "..", "*"}

segments = [[]]
for tok in tokens:
    if tok and set(tok) <= OPERATORS:
        segments.append([])
    else:
        segments[-1].append(tok)

for seg in segments:
    if not seg:
        continue

    if "git" in seg and "--no-verify" in seg:
        deny("--no-verify bypasses git hooks")

    if "git" in seg:
        gi = seg.index("git")
        rest = seg[gi + 1:]

        if "push" in rest:
            pi = rest.index("push")
            after = rest[pi + 1:]
            for t in after:
                if t == "--force":
                    deny("git push --force can overwrite remote history; use --force-with-lease")
                if t.startswith("-") and not t.startswith("--") and "f" in t:
                    deny("git push -f can overwrite remote history; use --force-with-lease")
                if t.startswith("+"):
                    deny("git push +refspec forces the update; use --force-with-lease")

        if "reset" in rest and "--hard" in rest:
            deny("git reset --hard discards uncommitted work")

        if "clean" in rest:
            has_force = "--force" in rest or any(
                t.startswith("-") and not t.startswith("--") and "f" in t
                for t in rest
            )
            if has_force:
                deny("git clean -f deletes untracked files with no undo")

        if "checkout" in rest:
            ci = rest.index("checkout")
            tail = rest[ci + 1:]
            if "." in tail:
                deny("git checkout . discards working-tree changes")

        if "restore" in rest:
            ri = rest.index("restore")
            tail = rest[ri + 1:]
            if "." in tail:
                staged_only = ("--staged" in tail or "-S" in tail) and not (
                    "--worktree" in tail or "-W" in tail
                )
                if not staged_only:
                    deny("git restore . discards working-tree changes")

    if "rm" in seg:
        ri = seg.index("rm")
        rest = seg[ri + 1:]
        flags = [t for t in rest if t.startswith("-")]
        args = [t for t in rest if not t.startswith("-")]
        short_letters = "".join(f.lstrip("-") for f in flags if not f.startswith("--"))
        long_flags = set(t for t in flags if t.startswith("--"))
        recursive = "r" in short_letters or "R" in short_letters or "--recursive" in long_flags
        force = "f" in short_letters or "--force" in long_flags
        if recursive and force:
            for a in args:
                norm = a.replace("${HOME}", "$HOME")
                if norm.endswith("/*"):
                    norm = norm[:-2]
                norm = norm.rstrip("/") or "/"
                if norm in FORBIDDEN_RM_TARGETS:
                    deny("rm -rf " + a + " is a catastrophic delete target")

allow()
'
