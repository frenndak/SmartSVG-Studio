#!/usr/bin/env python3
"""Admission gate for an untrusted SmartSVG distribution ZIP (stdlib only).

Verifies archive SHA-256 (if supplied), ZIP entry safety and CRC.
NOT a validation of embedded SmartSVG manifests, runtime operation, actual
GPU inference, Design Space import, or physical cutting.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath


class ArchiveRejected(ValueError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as src:
        for chunk in iter(lambda: src.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_archive(
    path: Path, *, expected_sha256: str | None = None,
    max_files: int = 5000, max_file_bytes: int = 100 * 1024 * 1024,
    max_total_bytes: int = 1024 * 1024 * 1024, max_expansion_ratio: int = 1000,
) -> dict:
    if not path.is_file():
        raise ArchiveRejected("ARCHIVE_NOT_FOUND")
    if any(v <= 0 for v in (max_files, max_file_bytes, max_total_bytes, max_expansion_ratio)):
        raise ArchiveRejected("INVALID_LIMITS")
    if expected_sha256 is not None and not re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha256):
        raise ArchiveRejected("INVALID_EXPECTED_SHA256")
    actual_sha256 = sha256_file(path)
    if expected_sha256 is not None and actual_sha256 != expected_sha256.lower():
        raise ArchiveRejected("ARCHIVE_SHA256_MISMATCH")

    names: set[str] = set()
    regular_files: set[str] = set()
    parent_dirs: set[str] = set()
    manifests = 0
    total_bytes = 0
    total_entries = 0
    try:
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            if not infos or len(infos) > max_files:
                raise ArchiveRejected("EMPTY_OR_EXCESSIVE_FILE_COUNT")
            for info in infos:
                name = info.filename
                if not name or "\\" in name or "\x00" in name or "\n" in name or "\r" in name:
                    raise ArchiveRejected("UNSAFE_MEMBER_NAME")
                if name.startswith("/") or re.match(r"^[A-Za-z]:", name):
                    raise ArchiveRejected("ABSOLUTE_MEMBER_NAME")
                clean = name[:-1] if info.is_dir() else name
                parts = clean.split("/")
                if not clean or any(p in ("", ".", "..") for p in parts):
                    raise ArchiveRejected("UNSAFE_MEMBER_PATH")
                if unicodedata.normalize("NFC", name) != name:
                    raise ArchiveRejected("NON_NORMALIZED_NAME")
                folded = clean.casefold()
                if folded in names:
                    raise ArchiveRejected("CASE_INSENSITIVE_DUPLICATE")
                names.add(folded)
                if info.flag_bits & 0x1:
                    raise ArchiveRejected("ENCRYPTED_MEMBER")
                mode = (info.external_attr >> 16) & 0xFFFF
                if info.create_system == 3 and stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR):
                    raise ArchiveRejected("SPECIAL_OR_SYMLINK_MEMBER")
                if info.file_size < 0 or info.file_size > max_file_bytes:
                    raise ArchiveRejected("MEMBER_SIZE_LIMIT")
                if not info.is_dir():
                    total_bytes += info.file_size
                    if total_bytes > max_total_bytes:
                        raise ArchiveRejected("TOTAL_SIZE_LIMIT")
                    if info.file_size and info.file_size > max_expansion_ratio * max(1, info.compress_size):
                        raise ArchiveRejected("ZIP_EXPANSION_RATIO_LIMIT")
                    regular_files.add(folded)
                    if "manifest" in PurePosixPath(clean).name.casefold() and clean.casefold().endswith(".json"):
                        manifests += 1
                for i in range(1, len(parts)):
                    parent_dirs.add("/".join(parts[:i]).casefold())
                total_entries += 1
            if regular_files & parent_dirs:
                raise ArchiveRejected("FILE_DIRECTORY_CONFLICT")
            bad = archive.testzip()  # Streaming CRC check, never extract.
            if bad is not None:
                raise ArchiveRejected("ZIP_CRC_FAILURE")
    except (zipfile.BadZipFile, OSError, NotImplementedError, RuntimeError, EOFError) as exc:
        raise ArchiveRejected("UNREADABLE_OR_CORRUPT_ZIP") from exc
    return {
        "status": "structural_zip_checks_passed",
        "archive_sha256": actual_sha256,
        "files": len(regular_files),
        "entries": total_entries,
        "declared_total_uncompressed_bytes": total_bytes,
        "manifest_candidate_files": manifests,
        "crc_checked": True,
        "internal_manifest_sha256_verified": False,
        "application_tests_executed": False,
        "gpu_cricut_hardware_verified": False,
        "ready_for_automation": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--expected-sha256", type=str)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = validate_archive(args.archive, expected_sha256=args.expected_sha256)
        print(json.dumps(result, indent=2, sort_keys=True) if args.json else
              "PASS: ZIP structurally safe and CRC verified; internal manifests and application UNVERIFIED")
        return 0
    except ArchiveRejected as exc:
        if args.json:
            print(json.dumps({"status": "rejected", "reason": str(exc)}, sort_keys=True))
        else:
            print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
