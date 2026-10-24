"""Verify original SmartSVG V21.15.2 source archive against its own full SHA manifest.

No import occurs here; verification does not imply passing application, ComfyUI,
GPU, Design Space or physical Cricut tests.
"""
from __future__ import annotations

import hashlib
import json
import zipfile

MANIFEST = "INSTALLATION_MANIFEST_V21_15_2.json"
VERSION = "21.15.2"
EXPECTED_ZIP_SHA256 = "9369656f0216cebb6dccce0d0155bffa16d8c384da6a984bf848cdd8aa003c54"


def verify_v21152_manifest(archive: zipfile.ZipFile, prefix: str) -> dict:
    """Raise ValueError unless every declared file exists and matches SHA-256."""
    full_name = prefix + MANIFEST
    try:
        payload = json.loads(archive.read(full_name))
    except (KeyError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("V21152_MANIFEST_MISSING_OR_INVALID") from exc
    if payload.get("version") != VERSION:
        raise ValueError("V21152_UNEXPECTED_VERSION")
    hashes = payload.get("full_files_sha256_excluding_self")
    if not isinstance(hashes, dict) or not hashes:
        raise ValueError("V21152_MANIFEST_MISSING_HASHES")
    actual = {
        item.filename[len(prefix):]
        for item in archive.infolist()
        if item.filename.startswith(prefix) and not item.is_dir()
    }
    if actual != set(hashes) | {MANIFEST}:
        raise ValueError("V21152_MANIFEST_INVENTORY_MISMATCH")
    for name, expected in hashes.items():
        if not isinstance(name, str) or not isinstance(expected, str) or len(expected) != 64:
            raise ValueError("V21152_INVALID_MANIFEST_ENTRY")
        actual_digest = hashlib.sha256(archive.read(prefix + name)).hexdigest()
        if actual_digest != expected.lower():
            raise ValueError("V21152_HASH_MISMATCH: " + name)
    return {
        "version": VERSION,
        "manifest_file": MANIFEST,
        "declared_files_verified": len(hashes),
        "manifest_hashes_verified": True,
        "application_tests_executed": False,
        "gpu_tested": False,
        "cricut_tested": False,
    }
