"""Regression guards for the clean SmartSVG v21.15.2 restart reference.

These tests do not certify end-to-end ComfyUI, GPU inference or physical Cricut
cutting. They ensure the original source archive and frozen requirements are
not silently re-labeled as a newer, merged production release.
"""
import hashlib
import json
import unittest
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
ZIP = ROOT / "source-releases" / "ComfyUI_SmartSVG_Studio_V21_15_2_Installation.zip"
ZIP_SHA256 = "9369656f0216cebb6dccce0d0155bffa16d8c384da6a984bf848cdd8aa003c54"
MASTER = ROOT / "docs" / "ROADMAP_MASTER_v3_2.md"
MASTER_SHA256 = "0e503a55fa622d7acea44d8e742205fb6a71119262c309a0b5a2bd48f0ab28a3"
PROTOCOL = ROOT / "docs" / "REPRISE_CANONIQUE_V21.md"
ADR = ROOT / "docs" / "ADR-20261027-001.md"
BACKLOG = ROOT / "docs" / "ROADMAP_EXECUTION_BACKLOG.md"


class CanonicalRestartReferenceTests(unittest.TestCase):
    def test_unchanged_source_zip_hash_and_crc(self):
        self.assertTrue(ZIP.is_file())
        self.assertEqual(hashlib.sha256(ZIP.read_bytes()).hexdigest(), ZIP_SHA256)
        with ZipFile(ZIP) as archive:
            self.assertEqual(len(archive.infolist()), 652)
            self.assertIsNone(archive.testzip())

    def test_frozen_master_unchanged(self):
        self.assertTrue(MASTER.is_file())
        self.assertEqual(hashlib.sha256(MASTER.read_bytes()).hexdigest(),
                         MASTER_SHA256)

    def test_spec_and_code_references_must_not_be_confused(self):
        self.assertTrue(PROTOCOL.is_file())
        self.assertTrue(ADR.is_file())
        text = PROTOCOL.read_text(encoding="utf-8")
        self.assertIn("V21.14.1", text)
        self.assertIn("V21.15.2", text)
        self.assertIn(ZIP_SHA256, text)
        self.assertIn("V21.16.0-rc.1", text)
        self.assertIn("NON CRÉÉ", text)
        self.assertIn("L2", text)
        self.assertIn("L3", text)

    def test_competing_ux_branches_are_not_silently_dropped(self):
        text = PROTOCOL.read_text(encoding="utf-8")
        for marker in (
            "#13", "#14", "#15", "#16", "#17", "#18", "#19",
            "#20 et #21", "#22", "#23 et #24", "#25", "#26", "#27",
            "#28", "#30", "#31",
            "project_workspace_g22.py", "smartsvg_project_panel_g22.mjs",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_follow_up_register_keeps_hardware_and_corpus_open(self):
        self.assertTrue(BACKLOG.is_file())
        content = BACKLOG.read_text(encoding="utf-8")
        self.assertIn("G0.3", content)
        self.assertIn("9/9 cas T", content)
        self.assertIn("L2", content)
        self.assertIn("L3", content)
        self.assertIn("BLOQUÉ PAR VÉRITÉ TERRAIN HUMAINE", content)


if __name__ == "__main__":
    unittest.main()
