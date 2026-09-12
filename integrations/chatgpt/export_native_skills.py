#!/usr/bin/env python3
"""Export Atlas and Spotter as independently uploadable native skills."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, BadZipFile, ZipFile


def bundle_entry(name: str, workflows: dict[str, str]) -> str:
    trigger = {
        "atlas": "software delivery, code review, scoped implementation, debugging, or measured optimization",
        "spotter": "personal-life planning, a daily brief, prioritization, KPI or time review, or cross-area preparation",
    }[name]
    procedures = "\n".join(
        f"- `{workflow}` — {description} Read `references/package/skills/{workflow}/PROCEDURE.md`."
        for workflow, description in workflows.items()
    )
    return f"""---
name: {name}
description: Use when the user needs {trigger}. Routes the request to the matching maintained procedure.
---

Read `references/package/core/{name.upper()}.md` first. It is the canonical doctrine
for this bundle and user and host instructions still outrank it.

Choose the one procedure that best matches the request, then read only the references
that procedure names. Whenever an internal procedure invokes another skill, read the
matching bundled procedure below and carry its arguments forward in this chat.
Bundled procedures do not register separate commands, agents, hooks or connectors.

Available procedures:
{procedures}

Use `references/package/` as the bundle root. Paths in the exported procedures already
resolve there. Helper scripts are reference material only: run one only when the host
can execute it and its required capability is available. When a required local tool,
connector, scheduled run, native agent, or lifecycle hook is unavailable, report that
specific gap and continue any independent read-only or preparation work. Do not claim
that this upload installs those capabilities.
"""


def safe_relative(path: Path, root: Path) -> Path | None:
    try:
        relative = path.relative_to(root)
        current = root
        for part in relative.parts:
            current /= part
            if current.is_symlink():
                return None
        path.resolve(strict=True).relative_to(root.resolve())
        return relative
    except (FileNotFoundError, ValueError):
        return None


def skill_descriptions(source: Path) -> dict[str, str]:
    descriptions = {}
    for path in sorted(source.glob("skills/*/SKILL.md")):
        if safe_relative(path, source) is None:
            raise ValueError(f"unsafe skill entry: {path}")
        header = path.read_text(encoding="utf-8").split("---", 2)[1]
        match = re.search(r"^description:\s*(.+)$", header, re.MULTILINE)
        if not match or match[1].strip() in {"|", ">", "|-", ">-"}:
            raise ValueError(f"expected canonical single-line description: {path}")
        descriptions[path.parent.name] = match[1].strip().strip("\"'")
    return descriptions


def rewrite_markdown(text: str, skill: str | None, source: Path) -> str:
    """Map plugin-relative instruction paths into the exported package tree."""
    text = text.replace("<plugin root>/", "references/package/")
    text = text.replace("<plugin root>", "references/package")
    # Some canonical prose names a sibling directly rather than through a placeholder.
    # Keep those references valid after the source tree moves under references/package.
    text = re.sub(
        r"(?<![\w/])skills/([a-z-]+)/(?:SKILL|PROCEDURE)\.md",
        r"references/package/skills/\1/PROCEDURE.md",
        text,
    )
    text = re.sub(
        r"(?<![\w/])skills/([a-z-]+)/references/([\w.-]+\.md)",
        r"references/package/skills/\1/references/\2",
        text,
    )
    if skill:
        text = text.replace(
            "<this skill>/", f"references/package/skills/{skill}/"
        )
        text = text.replace("<this skill>", f"references/package/skills/{skill}")
        # Procedure bodies formerly lived directly in skills/<skill>/.
        text = re.sub(
            r"(?<![\w/])references/([\w.-]+\.md)",
            rf"references/package/skills/{skill}/references/\1",
            text,
        )
        def rewrite_script(match: re.Match[str]) -> str:
            filename = match.group(1)
            root = "references/package" if (source / "scripts" / filename).is_file() else f"references/package/skills/{skill}"
            return f"{root}/scripts/{filename}"

        text = re.sub(r"(?<![\w/])scripts/([\w.-]+\.(?:py|sh))", rewrite_script, text)
    text = text.replace("/SKILL.md", "/PROCEDURE.md")
    text = re.sub(
        r"Skill tool `[^`:]+:([a-z-]+)` / `[^`:]+:([a-z-]+)`, `\$[a-z-]+` / `\$[a-z-]+` on Codex",
        r"read `references/package/skills/\1/PROCEDURE.md` or `references/package/skills/\2/PROCEDURE.md` in this chat",
        text,
    )
    return re.sub(
        r"Skill tool `[^`:]+:([a-z-]+)`, `\$[a-z-]+` on Codex",
        r"read `references/package/skills/\1/PROCEDURE.md` in this chat",
        text,
    )


def referenced_root_helpers(source: Path, name: str) -> set[str]:
    helpers = set()
    for document in list((source / "skills").rglob("*.md")) + [source / "core" / f"{name.upper()}.md"]:
        if not document.is_file() or safe_relative(document, source) is None:
            continue
        for filename in re.findall(r"scripts/([\w.-]+\.(?:py|sh))", document.read_text(encoding="utf-8")):
            if (source / "scripts" / filename).is_file():
                helpers.add(filename)
    return helpers


def export_package(name: str, source: Path, output: Path) -> Path:
    if not source.is_dir():
        raise ValueError(f"source directory is missing: {source}")
    core = source / "core" / f"{name.upper()}.md"
    if not core.is_file() or safe_relative(core, source) is None:
        raise ValueError(f"canonical core is missing: {core}")

    bundle = output / name
    marker = bundle / ".chatgpt-skill-export"
    if bundle.is_symlink() or (bundle.exists() and (marker.is_symlink() or not marker.is_file())):
        raise ValueError(f"refusing to replace unowned output directory: {bundle}")
    archive = output / f"{name}.zip"
    if archive.is_symlink():
        raise ValueError(f"refusing to replace symlink archive: {archive}")
    if archive.exists():
        try:
            with ZipFile(archive) as previous:
                owned = previous.read(".chatgpt-skill-export") == b"generated; do not edit\n"
        except (BadZipFile, KeyError):
            owned = False
        if not owned:
            raise ValueError(f"refusing to replace unowned archive: {archive}")
    if bundle.exists():
        shutil.rmtree(bundle)
    package = bundle / "references" / "package"
    (package / "core").mkdir(parents=True)
    (package / "core" / core.name).write_text(
        rewrite_markdown(core.read_text(), None, source), encoding="utf-8"
    )

    workflows = skill_descriptions(source)
    (bundle / "SKILL.md").write_text(bundle_entry(name, workflows), encoding="utf-8")
    (bundle / ".chatgpt-skill-export").write_text("generated; do not edit\n", encoding="utf-8")
    (bundle / "agents").mkdir(parents=True)
    color = "#2563EB" if name == "atlas" else "#0F766E"
    (bundle / "agents" / "openai.yaml").write_text(
        "interface:\n"
        f"  display_name: \"{name.title()}\"\n"
        f"  short_description: \"{('Code delivery and review workflows' if name == 'atlas' else 'Whole-life planning and review')}\"\n"
        "  icon_small: \"./assets/icon.png\"\n"
        "  icon_large: \"./assets/icon.png\"\n"
        f"  brand_color: \"{color}\"\n"
        f"  default_prompt: \"Use ${name} for this request.\"\n"
        "policy:\n"
        "  allow_implicit_invocation: true\n",
        encoding="utf-8",
    )

    for source_file in sorted((source / "skills").rglob("*")):
        if not source_file.is_file() or source_file.is_symlink():
            continue
        relative = safe_relative(source_file, source)
        if relative is None or relative.parts[0] != "skills":
            continue
        is_document = source_file.suffix == ".md"
        is_helper = source_file.suffix in {".py", ".sh"} and "scripts" in relative.parts
        if not (is_document or is_helper):
            continue
        destination = package / relative
        if destination.name == "SKILL.md":
            destination = destination.with_name("PROCEDURE.md")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if is_document:
            destination.write_text(
                rewrite_markdown(source_file.read_text(encoding="utf-8"), relative.parts[1], source),
                encoding="utf-8",
            )
        else:
            shutil.copy2(source_file, destination)

    for helper in referenced_root_helpers(source, name):
        source_file = source / "scripts" / helper
        if source_file.is_file() and safe_relative(source_file, source) is not None:
            destination = package / "scripts" / helper
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, destination)

    icon = source / "assets" / "icon.png"
    if icon.is_file() and safe_relative(icon, source) is not None:
        destination = bundle / "assets" / "icon.png"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(icon, destination)

    with ZipFile(archive, "w", ZIP_DEFLATED) as zip_file:
        for file in sorted(bundle.rglob("*")):
            if file.is_file():
                zip_file.write(file, file.relative_to(bundle))
    return bundle


def check_bundle(bundle: Path, source: Path) -> list[str]:
    errors: list[str] = []
    skills = list(bundle.rglob("SKILL.md"))
    if skills != [bundle / "SKILL.md"]:
        errors.append(f"{bundle}: expected exactly one root SKILL.md, found {len(skills)}")
    package = bundle / "references" / "package"
    if not (bundle / ".chatgpt-skill-export").is_file():
        errors.append(f"{bundle}: missing generated-output marker")
    if not (bundle / "agents" / "openai.yaml").is_file():
        errors.append(f"{bundle}: missing native UI sidecar")
    if not (bundle / "assets" / "icon.png").is_file():
        errors.append(f"{bundle}: missing native icon")
    for procedure in source.glob("skills/*/SKILL.md"):
        exported = package / procedure.relative_to(source)
        exported = exported.with_name("PROCEDURE.md")
        if not exported.is_file():
            errors.append(f"{bundle}: missing procedure {exported.relative_to(bundle)}")
    for document in package.rglob("*.md"):
        text = document.read_text(encoding="utf-8")
        if "<plugin root>" in text or "<this skill>" in text or "/SKILL.md" in text:
            errors.append(f"{bundle}: unresolved exported path in {document.relative_to(bundle)}")
        if "Skill tool" in text:
            errors.append(f"{bundle}: unresolved native skill invocation in {document.relative_to(bundle)}")
        if re.search(r"(?<!references/package/)skills/[a-z-]+/(?:PROCEDURE\.md|references/)", text):
            errors.append(f"{bundle}: raw plugin path in {document.relative_to(bundle)}")
        for target in set(re.findall(r"references/package/[\w./-]+\.(?:md|py|sh)", text)):
            if not (bundle / target).is_file():
                errors.append(f"{bundle}: broken reference {target} in {document.relative_to(bundle)}")
    for helper in referenced_root_helpers(source, bundle.name):
        if not (package / "scripts" / helper).is_file():
            errors.append(f"{bundle}: missing referenced root helper scripts/{helper}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--atlas-root", required=True, type=Path)
    parser.add_argument("--spotter-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--check", action="store_true", help="validate existing exports")
    args = parser.parse_args()
    output = args.output.resolve()
    source_roots = {"atlas": args.atlas_root.resolve(), "spotter": args.spotter_root.resolve()}

    if not args.check:
        output.mkdir(parents=True, exist_ok=True)
        for name, source in source_roots.items():
            export_package(name, source, output)

    errors = []
    for name, source in source_roots.items():
        errors.extend(check_bundle(output / name, source))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("exports: atlas and spotter; one root SKILL.md each; source procedures and references closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
