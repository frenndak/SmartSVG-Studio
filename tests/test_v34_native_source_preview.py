"""V34-019 — bounded actual PNG source preview for the native UI.

No Tk session is required; these tests verify the bytes handed to Tk, limits,
metadata consistency and preservation of the existing in-memory project.
"""
from dataclasses import replace
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import struct
import sys
import unittest

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from smartsvg_core.project_contracts import SourceAsset
from smartsvg_core.source_preview_v34 import (
    MAX_ENCODED_BYTES, MAX_DECODED_PIXELS, PNG_SIGNATURE, select_source_png
)

FIXTURE = ENGINE / "tests" / "test_project_recovery_g14.py"
spec = spec_from_file_location("preview_native_fixture_v34", FIXTURE)
module = module_from_spec(spec)
spec.loader.exec_module(module)


class NativeSourcePngPreviewTests(unittest.TestCase):
    def setUp(self):
        self.project = module.fixture()
        self.source_path = self.project.source_paths["source-a"]
        self.original = self.project.resources[self.source_path]

    def test_real_source_png_is_selected_without_mutating_project(self):
        before = dict(self.project.resources)
        selection = select_source_png(self.project)
        self.assertEqual(selection.status, "READY_PNG")
        self.assertEqual(selection.source_id, "source-a")
        self.assertEqual((selection.width_px, selection.height_px), (8, 6))
        self.assertEqual(selection.png, self.original)
        self.assertEqual(selection.subsample, 1)
        self.assertEqual(self.project.resources, before)

    def test_empty_sources_and_non_png_graceful(self):
        self.assertEqual(select_source_png(replace(self.project, sources=())).status,
                         "NO_SOURCE")
        self.assertEqual(select_source_png(replace(
            self.project, source_paths={"source-a": "sources/source-a.webp"}
        )).status, "SOURCE_FORMAT_UNSUPPORTED")

    def test_missing_resource_fails_closed(self):
        p = replace(self.project, resources={})
        self.assertEqual(select_source_png(p).status, "SOURCE_MISSING")

    def test_modified_bytes_cannot_be_shown(self):
        raw = self.original + b"extra"
        p = replace(self.project, resources={self.source_path: raw})
        self.assertEqual(select_source_png(p).status, "SOURCE_CHANGED")
        self.assertEqual(self.project.resources[self.source_path], self.original)

    def test_invalid_png_header_refused(self):
        raw = b"BAD" + self.original[3:]
        p = replace(self.project, resources={self.source_path: raw})
        self.assertEqual(select_source_png(p).status, "SOURCE_INVALID_PNG")

    def test_dimensions_must_agree_with_source_metadata(self):
        p = replace(self.project, sources=(
            replace(self.project.sources[0], width_px=9),))
        self.assertEqual(select_source_png(p).status, "SOURCE_CHANGED")

    def test_large_declared_dimensions_refused_before_decoder(self):
        raw = (PNG_SIGNATURE + b"\x00\x00\x00\rIHDR"
               + struct.pack(">II", 5000, 5000) + self.original[24:])
        p = replace(self.project, resources={self.source_path: raw})
        self.assertEqual(select_source_png(p).status, "SOURCE_TOO_LARGE")
        self.assertLess(MAX_DECODED_PIXELS, 5000 * 5000)

    def test_encoded_bytes_bound_avoids_large_tk_allocation(self):
        raw = self.original + b"x" * (MAX_ENCODED_BYTES + 1)
        p = replace(self.project, resources={self.source_path: raw})
        self.assertEqual(select_source_png(p).status, "SOURCE_TOO_LARGE")

    def test_large_but_allowed_png_preview_has_display_subsample(self):
        raw = module.png(width=1000, height=400)
        source = SourceAsset("source-a", sha256(raw).hexdigest(), 1000, 400)
        project = replace(self.project,
                          sources=(source,),
                          resources={self.source_path: raw,
                                     "masks/mask-a.png": self.project.resources["masks/mask-a.png"]})
        selected = select_source_png(project)
        self.assertEqual(selected.status, "READY_PNG")
        self.assertEqual(selected.subsample, 3)
        self.assertEqual(selected.png, raw)


if __name__ == "__main__":
    unittest.main()
