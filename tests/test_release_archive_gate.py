"""Synthetic ZIP fixtures only; no real SmartSVG release is certified by these tests."""
import hashlib
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from validate_release_archive import ArchiveRejected, validate_archive


class ArchiveGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "candidate.zip"

    def mkzip(self, entries):
        with zipfile.ZipFile(self.path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for name, body in entries:
                zf.writestr(name, body)
        return self.path

    def assert_rejected(self, reason, **kwargs):
        with self.assertRaisesRegex(ArchiveRejected, reason):
            validate_archive(self.path, **kwargs)

    def test_valid_synthetic_release(self):
        self.mkzip([("SmartSVG/smartsvg_ai/__init__.py", b"x=1"),
                    ("SmartSVG/INSTALLATION_MANIFEST.json", b"{}")])
        h = hashlib.sha256(self.path.read_bytes()).hexdigest()
        result = validate_archive(self.path, expected_sha256=h)
        self.assertEqual(result["files"], 2)
        self.assertTrue(result["crc_checked"])
        self.assertFalse(result["internal_manifest_sha256_verified"])
        self.assertFalse(result["ready_for_automation"])

    def test_wrong_sha(self):
        self.mkzip([("app.py", "hi")])
        self.assert_rejected("ARCHIVE_SHA256_MISMATCH", expected_sha256="f"*64)

    def test_invalid_sha(self):
        self.mkzip([("app.py", "hi")])
        self.assert_rejected("INVALID_EXPECTED_SHA256", expected_sha256="xyz")

    def test_parent_path(self):
        self.mkzip([("../escape.py", "bad")])
        self.assert_rejected("UNSAFE_MEMBER_PATH")

    def test_absolute_path(self):
        self.mkzip([("/etc/passwd", "bad")])
        self.assert_rejected("ABSOLUTE_MEMBER_NAME")

    def test_windows_drive(self):
        self.mkzip([("C:/escape.py", "bad")])
        self.assert_rejected("ABSOLUTE_MEMBER_NAME")

    def test_windows_backslashes(self):
        self.mkzip([("..\\escape.py", "bad")])
        self.assert_rejected("UNSAFE_MEMBER_NAME")

    def test_case_insensitive_collision(self):
        self.mkzip([("A.py", "one"), ("a.PY", "two")])
        self.assert_rejected("CASE_INSENSITIVE_DUPLICATE")

    def test_symlink_blocked(self):
        zi = zipfile.ZipInfo("link")
        zi.create_system = 3
        zi.external_attr = (0o120777 << 16)
        with zipfile.ZipFile(self.path, "w") as zf:
            zf.writestr(zi, "target")
        self.assert_rejected("SPECIAL_OR_SYMLINK_MEMBER")

    def test_file_directory_conflict(self):
        self.mkzip([("a", "x"), ("a/b.txt", "y")])
        self.assert_rejected("FILE_DIRECTORY_CONFLICT")

    def test_total_limit(self):
        self.mkzip([("a", "a"*64), ("b", "b"*64)])
        self.assert_rejected("TOTAL_SIZE_LIMIT", max_total_bytes=100)

    def test_member_limit(self):
        self.mkzip([("a", "a"*64)])
        self.assert_rejected("MEMBER_SIZE_LIMIT", max_file_bytes=30)

    def test_too_many_entries(self):
        self.mkzip([("a", "a"), ("b", "b")])
        self.assert_rejected("EMPTY_OR_EXCESSIVE_FILE_COUNT", max_files=1)

    def test_ratio_limit(self):
        self.mkzip([("a", "z"*4096)])
        self.assert_rejected("ZIP_EXPANSION_RATIO_LIMIT", max_expansion_ratio=2)

    def test_empty_zip(self):
        self.mkzip([])
        self.assert_rejected("EMPTY_OR_EXCESSIVE_FILE_COUNT")

    def test_corrupt_non_zip(self):
        self.path.write_bytes(b"not-a-zip")
        self.assert_rejected("UNREADABLE_OR_CORRUPT_ZIP")

    def test_cli_json(self):
        self.mkzip([("a", "hello")])
        script = Path(__file__).resolve().parents[1] / "tools" / "validate_release_archive.py"
        proc = subprocess.run([sys.executable, str(script), str(self.path), "--json"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("structural_zip_checks_passed", proc.stdout)


if __name__ == "__main__":
    unittest.main()
