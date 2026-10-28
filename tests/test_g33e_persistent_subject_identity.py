"""G3.3e-b1: persistent Subject identity over exact G2.4 float32 masks."""
from hashlib import sha256
from pathlib import Path
import re
import struct
import tempfile
import time
import unittest
import zlib

from smartsvg_core.project_archive import load_project
from smartsvg_core.project_workspace_g22 import ManagedWorkspace


def png(width=4, height=3):
    def chunk(kind, payload):
        return (struct.pack(">I", len(payload)) + kind + payload +
                struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff))
    row = b"\x00" + bytes([95]) * (width * 4)
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(row * height)) +
            chunk(b"IEND", b""))


class PersistentSubjectIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = ManagedWorkspace(self.temp.name)
        created = self.workspace.create(
            "subjects", png(), profile="Sticker - contour du sujet",
            width_mm=40, dpi=300, notes="")
        self.source_fingerprint = "a" * 64
        first = [
            0.0, 0.49, 0.5, 1.0,
            0.0, 0.75, 1.0, 0.0,
            0.0, 0.0, 0.0, 0.0,
        ]
        second = [
            1.0, 1.0, 0.0, 0.0,
            1.0, 0.6, 0.0, 0.0,
            0.0, 0.0, 0.0, 0.0,
        ]
        self.raw = struct.pack("<24f", *(first + second))
        self.workspace.save_base_masks(
            "subjects", raw_float32=self.raw, shape=[2, 3, 4],
            image_fingerprint="b" * 64,
            editor_fingerprint=self.source_fingerprint,
            expected_sha256=created["sha256"])

    @property
    def path(self):
        return Path(self.temp.name) / "SmartSVG_Managed_Projects" / "subjects.smartsvg"

    def binding(self, index=0):
        state = self.workspace.inspect("subjects")
        catalog = state["base_masks"]["mask_identity"]
        return state, catalog["bindings"][index], catalog["source_id"]

    def register(self, *, index=0, expected_sha256=None):
        state, item, source_id = self.binding(index)
        return self.workspace.register_subject_identity(
            "subjects",
            mask_index=index,
            mask_id=item["mask_id"],
            mask_sha256_float32=item["mask_sha256_float32"],
            source_id=source_id,
            source_sha256=self.source_fingerprint,
            expected_sha256=expected_sha256 or state["sha256"],
            confirmed=True,
            expires_at_ms=int(time.time() * 1000) + 60_000,
        )

    def test_create_reopen_and_recognize_preserves_exact_mask_resources(self):
        before = load_project(self.path)
        before_resources = dict(before.resources)
        before_snapshot_sha = sha256(
            before.resources["snapshots/base_masks_float32_v1.zlib"]).hexdigest()

        result = self.register()

        self.assertEqual(result["status"], "subject_identity_created")
        self.assertRegex(result["subject_id"], r"^subject-[a-f0-9]{32}$")
        reopened = load_project(self.path)
        self.assertEqual(len(reopened.subjects), 1)
        subject = reopened.subjects[0]
        self.assertEqual(subject.subject_id, result["subject_id"])
        self.assertEqual(subject.source_id, "source-original")
        self.assertEqual(subject.mask_id, "base-mask-00")
        self.assertEqual(subject.bbox_px, (1, 0, 3, 2))
        self.assertEqual(reopened.resources, before_resources)
        self.assertEqual(
            sha256(reopened.resources["snapshots/base_masks_float32_v1.zlib"]).hexdigest(),
            before_snapshot_sha)
        self.assertNotEqual(result["sha256"], self.workspace.inspect("subjects")["previous"]["sha256"]
                            if isinstance(self.workspace.inspect("subjects")["previous"], dict)
                            else "")

        current = self.workspace.inspect("subjects")
        state, item, source_id = self.binding(0)
        again = self.workspace.register_subject_identity(
            "subjects", mask_index=0, mask_id=item["mask_id"],
            mask_sha256_float32=item["mask_sha256_float32"],
            source_id=source_id, source_sha256=self.source_fingerprint,
            expected_sha256=current["sha256"], confirmed=True,
            expires_at_ms=int(time.time() * 1000) + 60_000)
        self.assertEqual(again["status"], "subject_identity_exists")
        self.assertEqual(again["subject_id"], result["subject_id"])
        self.assertEqual(again["sha256"], current["sha256"])
        self.assertEqual(len(load_project(self.path).subjects), 1)


if __name__ == "__main__":
    unittest.main()
