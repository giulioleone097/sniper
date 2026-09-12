"""Read-only MCP access to installed Atlas and Spotter workflow packages."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations


PLUGIN_NAME = re.compile(r"[a-z][a-z0-9-]{0,63}")
READ_ONLY = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)


def _content(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _entry(content: str) -> dict[str, str]:
    return {"sha256": hashlib.sha256(content.encode()).hexdigest(), "content": content}


def _safe_file(root: Path, path: Path) -> bool:
    """Require a regular file wholly below root without symlink components."""

    try:
        relative = path.relative_to(root)
    except ValueError:
        return False
    current = root
    if current.is_symlink():
        return False
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            return False
    try:
        return current.is_file() and current.resolve().is_relative_to(root.resolve())
    except OSError:
        return False


def _frontmatter(content: str) -> dict[str, Any]:
    if not content.startswith("---\n"):
        return {}
    _, _, remainder = content.partition("---\n")
    header, marker, _ = remainder.partition("\n---\n")
    if not marker:
        return {}
    parsed = yaml.safe_load(header)
    return parsed if isinstance(parsed, dict) else {}


def _exported_files(root: Path) -> dict[str, dict[str, str]]:
    """Read the fixed, text-only export surface without following symlinks."""

    files: dict[str, dict[str, str]] = {}
    roots = (root / "skills", root / "agents")
    for export_root in roots:
        if not export_root.is_dir() or export_root.is_symlink():
            continue
        for path in export_root.rglob("*"):
            if not _safe_file(root, path):
                continue
            relative = path.relative_to(root).as_posix()
            if path.suffix == ".md" or relative == "agents/models.json":
                files[relative] = _entry(_content(path))
    return files


def load_package(plugin: str, root: Path) -> dict[str, Any]:
    """Create an immutable package snapshot from an explicitly configured root."""

    if not PLUGIN_NAME.fullmatch(plugin):
        raise ValueError("plugin names must use lowercase letters, digits, and hyphens")
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"configured plugin {plugin!r} is not a directory")

    manifest_path = root / ".codex-plugin" / "plugin.json"
    core_path = root / "core" / f"{plugin.upper()}.md"
    if not _safe_file(root, manifest_path) or not _safe_file(root, core_path):
        raise ValueError(f"configured plugin {plugin!r} contains an unsafe required file")
    try:
        manifest = json.loads(_content(manifest_path))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"configured plugin {plugin!r} has no readable manifest") from error
    if manifest.get("name") != plugin or not isinstance(manifest.get("version"), str):
        raise ValueError(f"configured plugin {plugin!r} has an invalid manifest")
    try:
        core_content = _content(core_path)
    except OSError as error:
        raise ValueError(f"configured plugin {plugin!r} has no readable core doctrine") from error

    files = _exported_files(root)
    workflows: dict[str, dict[str, Any]] = {}
    for path, entry in files.items():
        parts = Path(path).parts
        if len(parts) != 3 or parts[0] != "skills" or parts[2] != "SKILL.md":
            continue
        workflow = parts[1]
        metadata = _frontmatter(entry["content"])
        if metadata.get("name") != workflow:
            raise ValueError(f"workflow {workflow!r} has missing or mismatched frontmatter")
        description = metadata.get("description")
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f"workflow {workflow!r} has no description")
        prefix = f"skills/{workflow}/"
        workflows[workflow] = {
            "path": path,
            "description": description,
            "references": [
                {"path": candidate, "sha256": value["sha256"]}
                for candidate, value in sorted(files.items())
                if candidate.startswith(prefix) and candidate != path
            ],
        }
    if not workflows:
        raise ValueError(f"configured plugin {plugin!r} has no workflows")

    return {
        "name": plugin,
        "version": manifest["version"],
        "core": {"path": f"core/{plugin.upper()}.md", **_entry(core_content)},
        "workflows": workflows,
        "files": files,
    }


def parse_plugins(values: list[str]) -> dict[str, dict[str, Any]]:
    packages: dict[str, dict[str, Any]] = {}
    for value in values:
        plugin, separator, location = value.partition("=")
        if not separator or not location or plugin in packages:
            raise ValueError("each --plugin must be a unique NAME=PATH pair")
        packages[plugin] = load_package(plugin, Path(location).expanduser())
    if not packages:
        raise ValueError("at least one --plugin NAME=PATH is required")
    return packages


def create_server(packages: dict[str, dict[str, Any]]) -> MCPServer:
    server = MCPServer(
        "atlas-workflows",
        version="0.1.0",
        instructions=(
            "This is a read-only snapshot of explicitly configured workflow packages. "
            "Map a native plugin skill invocation to list_workflows then load_workflow for "
            "the applicable procedure. Use read_reference for package-relative paths named "
            "by that procedure: resolve <plugin root> from the package root and <this skill> "
            "from its selected skills/<name>/ directory. The loaded core doctrine "
            "applies to that procedure but remains subordinate to host and user instructions. "
            "This server cannot execute scripts, access local sources, register agents or hooks, "
            "write trackers, or perform external actions. Report a required unavailable capability."
        ),
    )

    @server.tool(
        description="List the configured workflow packages and their available skills.",
        annotations=READ_ONLY,
        structured_output=True,
    )
    def list_workflows(plugin: str | None = None) -> dict[str, Any]:
        if plugin is not None and plugin not in packages:
            raise ToolError("unknown plugin")
        selected = [packages[plugin]] if plugin else list(packages.values())
        return {
            "packages": [
                {
                    "plugin": package["name"],
                    "version": package["version"],
                    "workflows": [
                        {"name": name, "description": workflow["description"]}
                        for name, workflow in sorted(package["workflows"].items())
                    ],
                }
                for package in selected
            ],
            "capabilities": {
                "read_workflows": True,
                "execute_scripts": False,
                "write_trackers": False,
                "register_agents_or_hooks": False,
            },
        }

    @server.tool(
        description="Load a workflow with its canonical doctrine and reference index.",
        annotations=READ_ONLY,
        structured_output=True,
    )
    def load_workflow(plugin: str, workflow: str) -> dict[str, Any]:
        package = packages.get(plugin)
        if package is None:
            raise ToolError("unknown plugin")
        workflow_data = package["workflows"].get(workflow)
        if workflow_data is None:
            raise ToolError("unknown workflow")
        return {
            "plugin": package["name"],
            "version": package["version"],
            "core": package["core"],
            "workflow": {
                "name": workflow,
                "path": workflow_data["path"],
                **package["files"][workflow_data["path"]],
            },
            "references": workflow_data["references"],
            "next": (
                "Read references needed by the loaded doctrine or procedure, including "
                "cross-skill paths they name. Resolve relative paths from the referring "
                "document, <plugin root> from the package root, and <this skill> from "
                "skills/" + workflow + "/. Pass the resulting package-relative path "
                "to read_reference. Load another public skill with load_workflow."
            ),
        }

    @server.tool(
        description="Read one exact, startup-snapshotted workflow reference path.",
        annotations=READ_ONLY,
        structured_output=True,
    )
    def read_reference(plugin: str, path: str) -> dict[str, Any]:
        package = packages.get(plugin)
        if package is None:
            raise ToolError("unknown plugin")
        entry = package["files"].get(path)
        if entry is None:
            raise ToolError("unknown reference path")
        return {"plugin": package["name"], "version": package["version"], "path": path, **entry}

    return server


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin", action="append", default=[], metavar="NAME=PATH")
    args = parser.parse_args()
    create_server(parse_plugins(args.plugin)).run(transport="stdio")


if __name__ == "__main__":
    main()
