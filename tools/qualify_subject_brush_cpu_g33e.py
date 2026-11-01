#!/usr/bin/env python3
"""Strict, opt-in CPU qualification for SmartSVG G3.3e-b2a (#71 / V34-132).

Run from a checkout of PR #78 with NumPy and Pillow already installed:
    python tools/qualify_subject_brush_cpu_g33e.py

This runner never installs dependencies, writes project data or certifies a
Windows/ComfyUI/Cricut device. Unlike G0's stdlib-only suite, missing CPU
packages and skipped tests are hard failures, not successful qualifications.
"""
from __future__ import annotations

import importlib.util
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

    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "engine"))
    sys.path.insert(0, str(root / "tests"))
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for name in CPU_TESTS:
        suite.addTests(loader.loadTestsFromName(f"{TEST_CASE}.{name}"))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if (result.testsRun != len(CPU_TESTS) or result.skipped or
            result.errors or result.failures or not result.wasSuccessful()):
        print("CPU QUALIFICATION FAILED: three real tests must PASS, no SKIP",
              file=sys.stderr)
        return 1
    print("CPU QUALIFICATION PASS: 3/3 G3.3e-b2a real brush tests, 0 skipped")
    return 0


if __name__ == "__main__":
    sys.exit(run())
