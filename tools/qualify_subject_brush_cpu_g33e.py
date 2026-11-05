#!/usr/bin/env python3
"""Strict CPU qualification for G3.3e preview and first-stroke persistence.

Run from a current checkout with NumPy and Pillow already installed:
    python tools/qualify_subject_brush_cpu_g33e.py

This runner never installs dependencies, writes project data or certifies a
Windows/ComfyUI/Cricut device. Unlike G0's stdlib-only suite, missing CPU
packages and skipped tests are hard failures, not successful qualifications.
"""
from __future__ import annotations

import importlib.util
from importlib.metadata import version
from pathlib import Path
import sys
import unittest

TEST_CASE = "test_g33e_subject_brush_preview.SubjectBrushPreviewTests"
CPU_TESTS = (
    "test_add_preview_is_deterministic_and_does_not_write_archive_or_backup",
    "test_erase_preview_preserves_other_subject_and_base_float32",
    "test_fail_closed_on_identity_revision_source_and_stroke",
)


def run() -> int:
    missing = [name for name in ("numpy", "PIL")
               if importlib.util.find_spec(name) is None]
    if missing:
        print("CPU QUALIFICATION BLOCKED: missing " + ", ".join(missing),
              file=sys.stderr)
        return 2

    # Record dependency versions for repeatable, exact-HEAD CPU evidence.
    print(f"CPU runtime versions: numpy={version('numpy')}, Pillow={version('Pillow')}")
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "engine"))
    sys.path.insert(0, str(root / "tests"))
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for name in CPU_TESTS:
        suite.addTests(loader.loadTestsFromName(f"{TEST_CASE}.{name}"))
    suite.addTests(loader.loadTestsFromName(
        "test_g33e_subject_brush_save.SubjectBrushSaveTests"))
    suite.addTests(loader.loadTestsFromName(
        "test_g33e_brush_composition.BrushCompositionTests"))
    suite.addTests(loader.loadTestsFromName(
        "test_g33e_brush_save_route.BrushSaveRouteTests.test_real_preview_save_reopen_and_duplicate_ack_preserve_base_resources"))
    expected_count = suite.countTestCases()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if (result.testsRun != expected_count or result.skipped or
            result.errors or result.failures or not result.wasSuccessful()):
        print("CPU QUALIFICATION FAILED: all real brush tests must PASS, no SKIP",
              file=sys.stderr)
        return 1
    print(f"CPU QUALIFICATION PASS: {result.testsRun}/{expected_count} real brush tests, 0 skipped")
    return 0


if __name__ == "__main__":
    sys.exit(run())
