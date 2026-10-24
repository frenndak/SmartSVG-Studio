"""Manifest regression tests use synthetic ZIPs, not hardware claims."""
import hashlib
import io
import json
import sys
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from verify_v21152_manifest import verify_v21152_manifest, MANIFEST


def bundle(content, version="21.15.2", missing=False, additional=False):
    root = "ComfyUI-SmartSVG-Studio-V21.15.2/"
    mapping = {key: hashlib.sha256(value).hexdigest() for key, value in content.items()}
    if missing:
        mapping.pop(next(iter(mapping)))
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for key, value in content.items():
            archive.writestr(root + key, value)
        archive.writestr(root + MANIFEST, json.dumps({
            "version": version,
            "full_files_sha256_excluding_self": mapping,
        }))
        if additional:
            archive.writestr(root + "hidden-extra.txt", "unexpected")
    output.seek(0)
    return zipfile.ZipFile(output), root


class ManifestGateTests(unittest.TestCase):
    def test_valid(self):
        archive, root = bundle({"__init__.py": b"code", "smartsvg_ai/__init__.py": b"other"})
        with archive:
            result = verify_v21152_manifest(archive, root)
        self.assertTrue(result["manifest_hashes_verified"])
        self.assertEqual(result["declared_files_verified"], 2)

    def test_changed_file_rejected(self):
        archive, root = bundle({"file.py": b"original"})
        with archive:
            data = json.loads(archive.read(root + MANIFEST))
        data["full_files_sha256_excluding_self"]["file.py"] = "0" * 64
        out = io.BytesIO()
        with zipfile.ZipFile(out, "w") as z:
            z.writestr(root + "file.py", b"original")
            z.writestr(root + MANIFEST, json.dumps(data))
        out.seek(0)
        with zipfile.ZipFile(out) as z, self.assertRaisesRegex(ValueError, "HASH_MISMATCH"):
            verify_v21152_manifest(z, root)

    def test_missing_declaration_rejected(self):
        archive, root = bundle({"a": b"a", "b": b"b"}, missing=True)
        with archive, self.assertRaisesRegex(ValueError, "INVENTORY_MISMATCH"):
            verify_v21152_manifest(archive, root)

    def test_unlisted_file_rejected(self):
        archive, root = bundle({"a": b"a"}, additional=True)
        with archive, self.assertRaisesRegex(ValueError, "INVENTORY_MISMATCH"):
            verify_v21152_manifest(archive, root)

    def test_wrong_version_rejected(self):
        archive, root = bundle({"a": b"a"}, version="21.15.1")
        with archive, self.assertRaisesRegex(ValueError, "UNEXPECTED_VERSION"):
            verify_v21152_manifest(archive, root)


if __name__ == "__main__":
    unittest.main()
