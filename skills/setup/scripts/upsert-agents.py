#!/usr/bin/env python3
"""Install or refresh the sniper doctrine in a project's AGENTS.md and CLAUDE.md, without touching anything else.

usage: upsert-agents.py PROJECT_DIR CORE_FILE

AGENTS.md: the block between <!-- sniper:core:start --> and <!-- sniper:core:end --> is replaced with CORE_FILE;
a missing file gets a skeleton (title, the block, "## Working on this repo" with a fill marker, "## Code Review Rules").
CLAUDE.md: created as "@AGENTS.md", or the import line is appended when absent. Idempotent: a second run changes nothing.
"""
import re
import sys
from pathlib import Path

START, END = "<!-- sniper:core:start -->", "<!-- sniper:core:end -->"
FILL = "<!-- sniper:fill: the 3-6 commands that prove a change here (build, typecheck, lint, test), one per line -->"


def upsert_agents(path: Path, core: str, name: str) -> str:
    block = f"{START}\n{core.strip()}\n{END}"
    if not path.exists():
        path.write_text(
            f"# {name}\n\n{block}\n\n## Working on this repo\n\n{FILL}\n\n## Code Review Rules\n\n"
            "<!-- one line per non-obvious invariant: <invariant>. Safe path: <what to do instead>. -->\n"
        )
        return "created"
    text = path.read_text()
    if START in text and END in text:
        new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, count=1, flags=re.S)
        if new == text:
            return "unchanged"
        path.write_text(new)
        return "block refreshed"
    body = text.rstrip("\n")
    extra = ""
    if "## Code Review Rules" not in text:
        extra = "\n\n## Code Review Rules\n"
    path.write_text(f"{body}\n\n{block}{extra}\n")
    return "block appended"


def upsert_claude(path: Path) -> str:
    """Root CLAUDE.md, or .claude/CLAUDE.md when the project already keeps it there (plugin repos must)."""
    nested = path.parent / ".claude" / "CLAUDE.md"
    if not path.exists() and nested.exists():
        path, line = nested, "@../AGENTS.md"
    else:
        line = "@AGENTS.md"
    if not path.exists():
        path.write_text(line + "\n")
        return "created"
    text = path.read_text()
    if re.search(r"^@(\.\./|\./)?AGENTS\.md\s*$", text, re.M):
        return "unchanged"
    path.write_text(text.rstrip("\n") + f"\n\n{line}\n")
    return "import appended"


POINTER = "Repository map and conventions: `docs/sniper/map.md`, `docs/sniper/conventions.md` (refresh with `setup --map`)."


def remove_agents(path: Path) -> str:
    if not path.exists() or START not in path.read_text():
        return "absent"
    text = path.read_text()
    new = re.sub(re.escape(START) + r".*?" + re.escape(END) + r"\n*", "", text, count=1, flags=re.S)
    new = new.replace(POINTER + "\n", "").replace(POINTER, "")
    if FILL in new:
        path.unlink()
        return "deleted (skeleton untouched)"
    path.write_text(re.sub(r"\n{3,}", "\n\n", new))
    return "block removed"


def remove_claude(path: Path) -> str:
    nested = path.parent / ".claude" / "CLAUDE.md"
    if not path.exists() and nested.exists():
        path = nested
    if not path.exists():
        return "absent"
    text = path.read_text()
    new = re.sub(r"^@(\.\./|\./)?AGENTS\.md\s*\n?", "", text, flags=re.M)
    if new == text:
        return "unchanged"
    if not new.strip():
        path.unlink()
        return "deleted"
    path.write_text(new)
    return "import removed"


def upsert_pointer(path: Path) -> str:
    """One navigation line after the doctrine block, so AGENTS.md points at the map instead of holding it."""
    text = path.read_text()
    if "docs/sniper/map.md" in text:
        return "unchanged"
    end = "<!-- sniper:core:end -->"
    i = text.find(end)
    if i < 0:
        return "no block"
    i += len(end)
    path.write_text(text[:i] + "\n\n" + POINTER + text[i:])
    return "pointer added"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if len(args) != (1 if "--remove" in flags else 2):
        sys.exit(__doc__)
    project = Path(args[0]).resolve()
    if "--remove" in flags:
        print(f"AGENTS.md: {remove_agents(project / 'AGENTS.md')}")
        print(f"CLAUDE.md: {remove_claude(project / 'CLAUDE.md')}")
        print("docs/sniper/: left for manual deletion")
        return
    core = Path(args[1]).read_text()
    print(f"AGENTS.md: {upsert_agents(project / 'AGENTS.md', core, project.name)}")
    print(f"CLAUDE.md: {upsert_claude(project / 'CLAUDE.md')}")
    if "--map" in flags:
        print(f"map pointer: {upsert_pointer(project / 'AGENTS.md')}")
    print(f"fill marker present: {FILL in (project / 'AGENTS.md').read_text()}")


if __name__ == "__main__":
    main()
