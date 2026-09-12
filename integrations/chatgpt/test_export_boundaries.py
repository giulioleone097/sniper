import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from export_native_skills import export_package


class ExportBoundaries(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        (self.source / "core").mkdir(parents=True)
        self.output = self.root / "output"
        self.output.mkdir()

    def test_external_core_is_never_packaged(self):
        private = self.root / "private.md"
        private.write_text("private data")
        (self.source / "core/ATLAS.md").symlink_to(private)
        with self.assertRaises(ValueError):
            export_package("atlas", self.source, self.output)
        self.assertFalse((self.output / "atlas.zip").exists())

    def test_unrelated_archive_is_preserved(self):
        (self.source / "core/ATLAS.md").write_text("doctrine")
        archive = self.output / "atlas.zip"
        with ZipFile(archive, "w") as target:
            target.writestr("my-file.txt", "keep this")
        original = archive.read_bytes()
        with self.assertRaises(ValueError):
            export_package("atlas", self.source, self.output)
        self.assertEqual(archive.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
