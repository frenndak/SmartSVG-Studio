"""Synthetic import tests only; these do NOT validate SmartSVG V21.15.2."""
import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from import_release_archive import ArchiveRejected, import_release, locate_package_root


class ImportReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "docs").mkdir()
        (self.root / "docs" / "ROADMAP_MASTER_v3_2.md").write_text("synthetic roadmap")
        self.zipfile = self.root / "test.zip"

    def archive(self, members, prefix="ComfyUI-SmartSVG-Studio-V21.15.2/"):
        members = dict(members)
        if "INSTALLATION_MANIFEST_V21_15_2.json" not in members:
            members["INSTALLATION_MANIFEST_V21_15_2.json"] = json.dumps({
                "version": "21.15.2",
                "full_files_sha256_excluding_self": {
                    name: hashlib.sha256(data.encode() if isinstance(data, str) else data).hexdigest()
                    for name, data in members.items()
                },
            })
        with zipfile.ZipFile(self.zipfile, "w", zipfile.ZIP_DEFLATED) as zf:
            for path, data in members.items():
                zf.writestr(prefix + path, data)
        return self.zipfile

    def valid_zip(self):
        return self.archive({
            "__init__.py": "# comfy entrypoint",
            "smartsvg_ai/__init__.py": "# engine",
            "README.md": "example",
        })

    def test_unique_root(self):
        self.assertEqual(locate_package_root(["one/smartsvg_ai/__init__.py"]), "one/")
        with self.assertRaisesRegex(ArchiveRejected, "NO_UNIQUE"):
            locate_package_root(["one/smartsvg_ai/__init__.py", "two/smartsvg_ai/__init__.py"])

    def test_safe_import_not_ready(self):
        self.valid_zip()
        digest = hashlib.sha256(self.zipfile.read_bytes()).hexdigest()
        report = import_release(self.zipfile, self.root / "engine", digest)
        self.assertEqual(report["archive_sha256"], digest)
        self.assertEqual(report["entries_imported"], 4)
        self.assertEqual(report["verified_manifest_files"], 3)
        self.assertFalse(report["operator_ready_marker_created"])
        self.assertTrue(report["internal_manifest_hashes_verified"])
        self.assertTrue((self.root / "engine" / "smartsvg_ai" / "__init__.py").exists())
        self.assertFalse((self.root / ".automation" / "READY").exists())

    def test_refuse_overwrite(self):
        self.valid_zip()
        (self.root / "engine").mkdir()
        with self.assertRaisesRegex(ArchiveRejected, "ENGINE_ALREADY_EXISTS"):
            import_release(self.zipfile, self.root / "engine")

    def test_refuse_missing_comfyui_entry(self):
        self.archive({"smartsvg_ai/__init__.py": "ok"})
        with self.assertRaisesRegex(ArchiveRejected, "COMFYUI_ENTRY_POINT"):
            import_release(self.zipfile, self.root / "engine")
        self.assertFalse((self.root / "engine").exists())

    def test_refuse_wrong_root(self):
        self.valid_zip()
        with self.assertRaisesRegex(ArchiveRejected, "UNEXPECTED_REPOSITORY"):
            import_release(self.zipfile, self.root / "elsewhere")

    def test_refuse_unsigned_mismatch(self):
        self.valid_zip()
        with self.assertRaisesRegex(ArchiveRejected, "ARCHIVE_SHA256_MISMATCH"):
            import_release(self.zipfile, self.root / "engine", "0" * 64)
        self.assertFalse((self.root / "engine").exists())


if __name__ == "__main__":
    unittest.main()
