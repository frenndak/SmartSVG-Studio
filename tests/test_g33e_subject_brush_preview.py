"""G3.3e-b2a core: real G1.2 Subject preview, no archive write.

Requirement: V3.3 stable subject identity, exact float32, non-destructive edit.
Ticket: #71 (b2a backend slice); UI/route/CAS remain for later micro-lots.
"""
from dataclasses import replace
import importlib.util
from hashlib import sha256
from pathlib import Path
import struct
import tempfile
import time
import unittest
import zlib

from smartsvg_core.project_archive import load_project
from smartsvg_core.project_workspace_g22 import ManagedWorkspace
from smartsvg_core.subject_brush_preview_g33e import (
    SubjectBrushPreviewError, preview_subject_brush,
)


def _png(width=16, height=12):
    def chunk(kind, payload):
        return (struct.pack(">I", len(payload)) + kind + payload
                + struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff))
    row = b"\x00" + bytes([95]) * (width * 4)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(row * height))
            + chunk(b"IEND", b""))


class SubjectBrushPreviewTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.workspace = ManagedWorkspace(temp.name)
        created = self.workspace.create(
            "brush-preview", _png(), profile="Sticker - contour du sujet",
            width_mm=40, dpi=300, notes="")
        self.first = [0.0] * (16 * 12)
        self.second = [0.0] * (16 * 12)
        self.first[0] = 0.35  # untouched soft alpha must stay bit-identical
        self.first[6 * 16 + 8] = 0.6
        self.second[2 * 16 + 2] = 1.0
        self.second[3 * 16 + 3] = 0.4
        raw = struct.pack("<384f", *(self.first + self.second))
        self.workspace.save_base_masks(
            "brush-preview", raw_float32=raw, shape=[2, 12, 16],
            image_fingerprint="b" * 64, editor_fingerprint="a" * 64,
            expected_sha256=created["sha256"])
        self.subject_ids = []
        for index in (0, 1):
            state = self.workspace.inspect("brush-preview")
            item = state["base_masks"]["mask_identity"]["bindings"][index]
            result = self.workspace.register_subject_identity(
                "brush-preview", mask_index=index, mask_id=item["mask_id"],
                mask_sha256_float32=item["mask_sha256_float32"],
                source_id=state["base_masks"]["mask_identity"]["source_id"],
                source_sha256="a" * 64, expected_sha256=state["sha256"],
                confirmed=True, expires_at_ms=int(time.time() * 1000) + 60_000)
            self.subject_ids.append(result["subject_id"])
        self.path = (Path(temp.name) / "SmartSVG_Managed_Projects"
                     / "brush-preview.smartsvg")

    def command(self, index=0, **overrides):
        project = load_project(self.path)
        item = self.workspace.inspect("brush-preview")["base_masks"][
            "mask_identity"]["bindings"][index]
        values = dict(
            subject_id=self.subject_ids[index], mask_id=item["mask_id"],
            mask_sha256_float32=item["mask_sha256_float32"],
            source_id="source-original", source_sha256="a" * 64,
            mode="add", radius=0.05, points=[[0.5, 0.5]])
        values.update(overrides)
        return project, values

    @unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('PIL'),
                         'CPU brush dependencies not installed in stdlib-only G0')
    def test_add_preview_is_deterministic_and_does_not_write_archive_or_backup(self):
        project, values = self.command()
        archive = self.path.read_bytes()
        previous = self.path.with_name("brush-preview.previous.smartsvg")
        backup = previous.read_bytes() if previous.exists() else None
        resources = dict(project.resources)
        operations = list(project.operations)
        first = preview_subject_brush(project, **values)
        second = preview_subject_brush(project, **values)
        self.assertGreater(first["changed_pixels"], 0)
        self.assertEqual(first["after_png_l8"], second["after_png_l8"])
        self.assertEqual(first["preview_float32"], second["preview_float32"])
        self.assertNotEqual(first["before_png_l8"], first["after_png_l8"])
        self.assertEqual(first["dimensions_px"], [16, 12])
        self.assertFalse(first["persisted"])
        self.assertFalse(first["cricut_certified"])
        self.assertEqual(self.path.read_bytes(), archive)
        self.assertEqual(previous.read_bytes() if previous.exists() else None, backup)
        self.assertEqual(project.resources, resources)
        self.assertEqual(project.operations, operations)
        self.assertEqual(len(load_project(self.path).subjects), 2)
        preview = struct.unpack("<192f", first["preview_float32"])
        self.assertEqual(struct.pack("<f", preview[0]),
                         struct.pack("<f", self.first[0]))
        self.assertEqual(struct.pack("<f", preview[-1]),
                         struct.pack("<f", self.first[-1]))

    @unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('PIL'),
                         'CPU brush dependencies not installed in stdlib-only G0')
    def test_erase_preview_preserves_other_subject_and_base_float32(self):
        project, values = self.command(mode="erase")
        archive = self.path.read_bytes()
        result = preview_subject_brush(project, **values)
        self.assertGreater(result["changed_pixels"], 0)
        values_after = struct.unpack("<192f", result["preview_float32"])
        self.assertEqual(values_after[6 * 16 + 8], 0.0)
        # The archive stores IEEE-754 float32; compare encoded values rather
        # than Python's float64 representation of a soft alpha (0.35).
        self.assertEqual(struct.pack("<f", values_after[0]),
                         struct.pack("<f", self.first[0]))
        self.assertEqual(self.path.read_bytes(), archive)
        second_project, second_values = self.command(1, mode="erase",
                                                      points=[[0.125, 0.18]])
        second = preview_subject_brush(second_project, **second_values)
        self.assertEqual(second["subject_id"], self.subject_ids[1])
        self.assertEqual(self.path.read_bytes(), archive)
        self.assertEqual(load_project(self.path).resources, project.resources)

    @unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('PIL'),
                         'CPU brush dependencies not installed in stdlib-only G0')
    def test_fail_closed_on_identity_revision_source_and_stroke(self):
        project, values = self.command()
        before = self.path.read_bytes()
        cases = [
            ({"subject_id": "subject-" + "f" * 32}, "SUBJECT_NOT_VERIFIED"),
            ({"mask_id": "base-mask-01"}, "SUBJECT_PROOF_MISMATCH"),
            ({"mask_sha256_float32": "f" * 64}, "SUBJECT_PROOF_MISMATCH"),
            ({"source_sha256": "f" * 64}, "SUBJECT_SOURCE_MISMATCH"),
            ({"mode": "replace"}, "INVALID_PREVIEW_STROKE"),
            ({"radius": -0.01}, "INVALID_PREVIEW_STROKE"),
            ({"radius": float("nan")}, "INVALID_PREVIEW_STROKE"),
            ({"points": []}, "INVALID_PREVIEW_STROKE"),
            ({"points": [[1.1, 0.5]]}, "INVALID_PREVIEW_STROKE"),
            ({"points": [[0.5, 0.5]] * 65}, "INVALID_PREVIEW_STROKE"),
        ]
        for changes, code in cases:
            with self.subTest(changes=str(changes)), self.assertRaisesRegex(
                    SubjectBrushPreviewError, code):
                preview_subject_brush(project, **{**values, **changes})
        self.assertEqual(self.path.read_bytes(), before)

    def test_invalid_strokes_rejected_before_optional_cpu_runtime(self):
        # G2.3 preflight must fail closed even when NumPy/Pillow are absent.
        project, values = self.command()
        before = self.path.read_bytes()
        invalid = [
            {"radius": -0.01},
            {"radius": 0.3},
            {"radius": True},
            {"radius": float("nan")},
            {"points": [[1.1, 0.5]]},
            {"points": [[True, 0.5]]},
            {"points": [[0.5]]},
        ]
        for changes in invalid:
            with self.subTest(changes=str(changes)), self.assertRaisesRegex(
                    SubjectBrushPreviewError, "INVALID_PREVIEW_STROKE"):
                preview_subject_brush(project, **{**values, **changes})
        self.assertEqual(self.path.read_bytes(), before)

    def test_forged_identity_proof_is_rejected_without_write(self):
        project, values = self.command()
        before = self.path.read_bytes()
        bindings = dict(project.document["subject_identity_bindings_g33e_b1"])
        items = [dict(x) for x in bindings["items"]]
        items[0]["mask_sha256_float32"] = "f" * 64
        forged = replace(project, document={
            **project.document,
            "subject_identity_bindings_g33e_b1": {**bindings, "items": items}})
        with self.assertRaisesRegex(SubjectBrushPreviewError, "INVALID_SUBJECT_PROOF"):
            preview_subject_brush(forged, **values)
        self.assertEqual(self.path.read_bytes(), before)


class SubjectBrushPreviewAdmissionTests(unittest.TestCase):
    def test_fail_closed_identity_without_optional_cpu_dependencies(self):
        # G0 must validate imports and reject malformed identity without
        # installing numpy/Pillow or executing the production replay.
        with self.assertRaisesRegex(SubjectBrushPreviewError,
                                    "INVALID_PREVIEW_IDENTITY"):
            preview_subject_brush(
                None, subject_id="not-a-subject", mask_id="base-mask-00",
                mask_sha256_float32="a" * 64, source_id="source-original",
                source_sha256="b" * 64, mode="add", radius=0.05,
                points=[[0.5, 0.5]])


if __name__ == "__main__":
    unittest.main()
