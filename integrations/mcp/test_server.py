import tempfile
import unittest
from pathlib import Path

from server import load_package


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


if __name__ == "__main__":
    unittest.main()
