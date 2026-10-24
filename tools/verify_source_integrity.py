#!/usr/bin/env python3
"""Check that checked-in SmartSVG source is an exact byte copy of V21.15.2 ZIP.

Verifies archival SHA, ZIP structure/CRC, all manifest hashes, all 652 extracted
source files and absence of unexpected engine files. This is NOT a runtime test.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

from validate_release_archive import validate_archive
from verify_v21152_manifest import EXPECTED_ZIP_SHA256, verify_v21152_manifest

REL_ZIP = Path("source-releases/ComfyUI_SmartSVG_Studio_V21_15_2_Installation.zip")
PREFIX = "ComfyUI-SmartSVG-Studio-V21.15.2/"


def check_archive(repo: Path) -> dict:
    """Verify the immutable source ZIP/manifest without comparing live engine files.

    This is the appropriate CI check AFTER G0 admission, because engine/ may
    legitimately evolve. It does not certify those evolved files.
    """
    archive_path = repo / REL_ZIP
    result = validate_archive(archive_path, expected_sha256=EXPECTED_ZIP_SHA256)
    with zipfile.ZipFile(archive_path) as zf:
        verified = verify_v21152_manifest(zf, PREFIX)
    return {
        "status": "source_archive_integrity_passed",
        "original_zip_sha256": result["archive_sha256"],
        "manifest_file_hashes_verified": verified["declared_files_verified"],
        "zip_crc_checked": result["crc_checked"],
        "engine_compared": False,
        "complete_runtime_tests": False,
        "physical_cricut_verified": False,
        "gpu_inference_verified": False,
    }


def check_source(repo: Path) -> dict:
    """Strict G0 admission check: use ONLY for the as-imported baseline."""
    archive_path = repo / REL_ZIP
    archive_result = check_archive(repo)
    with zipfile.ZipFile(archive_path) as zf:
        expected = {}
        for item in zf.infolist():
            if item.is_dir():
                continue
            if not item.filename.startswith(PREFIX):
                raise ValueError("SOURCE_PREFIX_ESCAPE")
            relative = item.filename[len(PREFIX):]
            if not relative:
                raise ValueError("EMPTY_SOURCE_PATH")
            dest = repo / "engine" / relative
            if not dest.is_file() or dest.is_symlink():
                raise ValueError("MISSING_OR_SYMLINK_SOURCE: " + relative)
            with dest.open("rb") as f:
                digest = hashlib.sha256()
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    digest.update(chunk)
            if digest.hexdigest() != hashlib.sha256(zf.read(item)).hexdigest():
                raise ValueError("SOURCE_CONTENT_MISMATCH: " + relative)
            expected[relative] = True
        # compileall and imports generate bytecode in-place. These are not
        # distribution source, but every other unexpected engine file still
        # fails the exact source inventory check.
        actual = set()
        for path in (repo / "engine").rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(repo / "engine")
            if "__pycache__" in relative.parts and relative.suffix in {".pyc", ".pyo"}:
                continue
            actual.add(relative.as_posix())
        if actual != expected.keys():
            raise ValueError("SOURCE_FILE_INVENTORY_MISMATCH")
    return {
        "status": "source_integrity_passed",
        "original_zip_sha256": archive_result["original_zip_sha256"],
        "manifest_file_hashes_verified": archive_result["manifest_file_hashes_verified"],
        "extracted_files_compared": len(expected),
        "zip_crc_checked": archive_result["zip_crc_checked"],
        "engine_compared": True,
        "complete_runtime_tests": False,
        "physical_cricut_verified": False,
        "gpu_inference_verified": False,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", type=Path, default=Path("."))
    p.add_argument("--archive-only", action="store_true",
                   help="Verify immutable source archive without rejecting legitimate live engine changes")
    args = p.parse_args()
    try:
        report = check_archive(args.repo.resolve()) if args.archive_only else check_source(args.repo.resolve())
        print(json.dumps(report, sort_keys=True))
        return 0
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        print(json.dumps({"status": "source_integrity_failed", "reason": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
