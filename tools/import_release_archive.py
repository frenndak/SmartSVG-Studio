#!/usr/bin/env python3
"""Import an inspected SmartSVG installation ZIP into engine/ on a candidate branch.

Do not call this program on the main branch. The archive must be provided by
an operator via a private release asset, not retrieved from untrusted URLs.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from validate_release_archive import ArchiveRejected, validate_archive


def locate_package_root(members: list[str]) -> str:
    """Find the one top-level folder containing the engine's smartsvg_ai package."""
    roots = set()
    for path in members:
        if path.endswith("smartsvg_ai/__init__.py"):
            prefix = path[: -len("smartsvg_ai/__init__.py")]
            if prefix in ("",) or (prefix.endswith("/") and prefix.count("/") == 1):
                roots.add(prefix)
    if len(roots) != 1:
        raise ArchiveRejected("NO_UNIQUE_SMARTSVG_SOURCE_ROOT")
    return roots.pop()


def import_release(archive: Path, dest: Path, expected_sha256: str | None = None) -> dict:
    if not archive.is_file():
        raise ArchiveRejected("ARCHIVE_NOT_FOUND")
    dest = dest.resolve()
    repo = dest.parent
    if dest.name != "engine" or not (repo / "docs" / "ROADMAP_MASTER_v3_2.md").is_file():
        raise ArchiveRejected("UNEXPECTED_REPOSITORY_LAYOUT")
    if dest.exists():
        raise ArchiveRejected("ENGINE_ALREADY_EXISTS_NO_OVERWRITE")
    structural = validate_archive(archive, expected_sha256=expected_sha256)
    with zipfile.ZipFile(archive) as zf:
        members = [i.filename for i in zf.infolist() if not i.is_dir()]
        prefix = locate_package_root(members)
        relevant = [p for p in members if p.startswith(prefix) and p != prefix]
        if not relevant:
            raise ArchiveRejected("NO_SOURCE_FILES")
        with tempfile.TemporaryDirectory(prefix=".smartsvg-admission-", dir=repo) as td:
            staging = Path(td) / "engine"
            staging.mkdir()
            for member in relevant:
                rel = member[len(prefix):]
                if not rel:
                    continue
                target = staging.joinpath(*rel.split("/"))
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as inp, target.open("xb") as out:
                    shutil.copyfileobj(inp, out, length=1024 * 1024)
            if not (staging / "smartsvg_ai" / "__init__.py").is_file():
                raise ArchiveRejected("SMARTSVG_MODULE_MISSING")
            if not (staging / "__init__.py").is_file():
                raise ArchiveRejected("COMFYUI_ENTRY_POINT_MISSING")
            # No trust claim on internal manifest: its schema is not known here.
            # Import succeeds to a PR, but activation marker is NOT created.
            manifest_candidates = sorted(p[len(prefix):] for p in relevant
                                         if "manifest" in p.lower() and p.endswith(".json"))
            summary = {
                "version_expected": "V21.15.2",
                "original_filename": archive.name,
                "archive_sha256": structural["archive_sha256"],
                "entries_imported": len(relevant),
                "manifest_candidates": manifest_candidates,
                "archive_crc_checked": True,
                "internal_manifest_hashes_verified": False,
                "complete_regression_suite_verified": False,
                "comfyui_frontend_verified": False,
                "actual_ai_inference_verified": False,
                "cricut_design_space_verified": False,
                "operator_ready_marker_created": False,
                "import_date_utc": datetime.now(timezone.utc).isoformat(),
            }
            # os.rename within repo filesystem; no source-tree partial import.
            staging.rename(dest)
    return summary


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("archive", type=Path)
    p.add_argument("--destination", type=Path, default=Path("engine"))
    p.add_argument("--expected-sha256")
    p.add_argument("--output", type=Path, default=Path("docs/IMPORT_V21_15_2.json"))
    args = p.parse_args(argv)
    try:
        summary = import_release(args.archive, args.destination, args.expected_sha256)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if args.output.exists():
            raise ArchiveRejected("IMPORT_REPORT_EXISTS_NO_OVERWRITE")
        args.output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("Imported candidate safely into engine/. Activation remains DISABLED.")
        return 0
    except (ArchiveRejected, OSError, zipfile.BadZipFile) as exc:
        print(f"IMPORT FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
