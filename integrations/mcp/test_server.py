import asyncio
import tempfile
import unittest
from pathlib import Path

from mcp.server.mcpserver.exceptions import ToolError

from server import create_server, load_package, parse_plugin


class PackageBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "atlas"
        for directory in ("core", "skills/scope/references", ".codex-plugin"):
            (self.root / directory).mkdir(parents=True)
        (self.root / "core/ATLAS.md").write_text("Canonical doctrine")
        (self.root / ".codex-plugin/plugin.json").write_text(
            '{"name":"atlas","version":"1.0.0"}'
        )
        (self.root / "skills/scope/SKILL.md").write_text(
            "---\nname: scope\ndescription: Scope a request\n---\nRead references/asking.md"
        )
        (self.root / "skills/scope/references/asking.md").write_text("Await the answer")

    def test_workflow_keeps_doctrine_and_supporting_reference(self):
        package = load_package("atlas", self.root)
        self.assertEqual(package["core"]["content"], "Canonical doctrine")
        self.assertEqual(package["workflows"]["scope"]["description"], "Scope a request")
        self.assertEqual(
            package["files"]["skills/scope/references/asking.md"]["content"],
            "Await the answer",
        )
        # Runtime reads use an immutable startup snapshot, not a caller-selected disk path.
        (self.root / "skills/scope/references/asking.md").write_text("Changed on disk")
        self.assertEqual(
            package["files"]["skills/scope/references/asking.md"]["content"],
            "Await the answer",
        )

    def test_secrets_and_symlinks_are_not_exported(self):
        secret = Path(self.temp.name) / "secret.md"
        secret.write_text("must not be exposed")
        (self.root / ".env").write_text("secret")
        (self.root / "skills/scope/references/leak.md").symlink_to(secret)
        package = load_package("atlas", self.root)
        for path in (".env", "../secret.md", str(secret), "skills/scope/references/leak.md"):
            self.assertNotIn(path, package["files"])

    def test_server_isolated_to_one_package(self):
        server = create_server(load_package("atlas", self.root))

        async def assert_isolation():
            listing = await server.call_tool("list_workflows", {})
            self.assertEqual(listing.structured_content["plugin"], "atlas")
            self.assertNotIn("spotter", str(listing.structured_content))
            with self.assertRaises(ToolError):
                await server.call_tool("read_reference", {"path": "skills/spotter/SKILL.md"})

        asyncio.run(assert_isolation())
        with self.assertRaisesRegex(ValueError, "exactly one"):
            parse_plugin(["atlas=/tmp/atlas", "spotter=/tmp/spotter"])


if __name__ == "__main__":
    unittest.main()
