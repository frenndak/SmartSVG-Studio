"""Git line-ending conversion must preserve pins; content edits must fail pins."""
from hashlib import sha1
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

DOC = Path(__file__).resolve().parents[1] / "docs/roadmap-v3.5"
spec = importlib.util.spec_from_file_location("v35_git_blob", DOC / "git_blob_provenance.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def raw_blob(raw):
    return sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


class GitBlobProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], check=True, capture_output=True, text=True).stdout.strip()

    def repository(self):
        self.git("init")
        self.git("config", "core.autocrlf", "true")

    def test_non_git_snapshot_hashes_exact_bytes(self):
        file = self.root / "note.md"
        file.write_bytes(b"one\r\ntwo\r\n")
        self.assertEqual(module.file_blob(file), raw_blob(file.read_bytes()))

    def test_git_crlf_worktree_matches_lf_blob(self):
        self.repository()
        file = self.root / "note.md"
        file.write_bytes(b"one\ntwo\n")
        self.git("add", "note.md")
        expected = self.git("rev-parse", ":note.md")
        file.write_bytes(b"one\r\ntwo\r\n")
        self.assertNotEqual(raw_blob(file.read_bytes()), expected)
        self.assertEqual(module.file_blob(file), expected)

    def test_real_text_edit_cannot_reuse_pin(self):
        self.repository()
        file = self.root / "note.md"
        file.write_bytes(b"one\ntwo\n")
        self.git("add", "note.md")
        expected = self.git("rev-parse", ":note.md")
        file.write_bytes(b"one\r\nchanged\r\n")
        self.assertNotEqual(module.file_blob(file), expected)

    def test_explicit_binary_attribute_preserves_byte_identity(self):
        self.repository()
        (self.root / ".gitattributes").write_text("*.md -text\n", encoding="utf-8")
        file = self.root / "note.md"
        file.write_bytes(b"one\r\ntwo\r\n")
        self.git("add", ".gitattributes", "note.md")
        self.assertEqual(module.file_blob(file), raw_blob(file.read_bytes()))
        self.assertEqual(module.file_blob(file), self.git("rev-parse", ":note.md"))

    def test_binary_content_is_not_normalized(self):
        self.repository()
        file = self.root / "image.bin"
        file.write_bytes(b"\x00one\r\ntwo\r\n")
        self.git("add", "image.bin")
        self.assertEqual(module.file_blob(file), raw_blob(file.read_bytes()))

    def test_git_hash_failure_does_not_fall_back_to_raw_bytes(self):
        file = self.root / "note.md"
        file.write_bytes(b"one\n")
        answers = [
            subprocess.CompletedProcess([], 0, stdout=str(self.root), stderr=""),
            subprocess.CompletedProcess([], 1, stdout="", stderr="failed"),
        ]
        with patch.object(module.subprocess, "run", side_effect=answers):
            with self.assertRaises(ValueError):
                module.file_blob(file)


if __name__ == "__main__":
    unittest.main()
