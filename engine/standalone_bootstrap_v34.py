"""V34-019 (first micro-slice): read-only SmartSVG V1 bootstrap without ComfyUI.

Run from any working directory, even with site-packages disabled:
    python -I -S engine/standalone_bootstrap_v34.py status
    python -I -S engine/standalone_bootstrap_v34.py inspect /path/project.smartsvg

Not a desktop GUI, installer, image processor or Windows qualification.
No HTTP server, model, download, automatic project repair or write operation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

# Running this file directly MUST NOT import engine/__init__.py: that entrypoint
# registers historical ComfyUI nodes and optionally the ComfyUI HTTP routes.
_ENGINE_DIR = str(Path(__file__).resolve().parent)
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)

from smartsvg_core.project_recovery import RecoveryError, inspect_project


def _send(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="SmartSVG V3.4 — preuve de démarrage autonome en lecture seule"
    )
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="Vérifier le chargement du noyau sans ComfyUI")
    inspection = sub.add_parser("inspect", help="Examiner un projet V1 sans le modifier")
    inspection.add_argument("project", help="Chemin local d'un projet .smartsvg existant")
    args = parser.parse_args(argv)

    # This is an assertion about this *running process*, not proof of a Windows
    # installation or a complete native application.
    forbidden = ("engine", "nodes", "server", "folder_paths", "torch", "aiohttp")
    loaded = sorted(name for name in forbidden if (
        name in sys.modules or any(module.startswith(name + ".") for module in sys.modules)
    ))
    if loaded:
        _send({"ok": False, "error_code": "COMFYUI_DEPENDENCY_IMPORTED"})
        return 2

    if args.command == "status":
        _send({
            "ok": True,
            "phase": "V34-019_BOOTSTRAP_READONLY",
            "comfyui_required": False,
            "project_v1_inspection": True,
            "read_only": True,
            "desktop_ui_available": False,
            "windows_qualified": False,
            "cricut_qualified": False,
        })
        return 0

    try:
        report = inspect_project(args.project)
    except (RecoveryError, OSError) as exc:
        _send({
            "ok": False,
            "error_code": exc.code if isinstance(exc, RecoveryError) else "PROJECT_READ_FAILED",
            "read_only": True,
        })
        return 2

    _send({
        "ok": report.status == "PROJECT_HEALTHY",
        "status": report.status,
        "primary": report.primary,
        "previous": report.previous,
        "project_id": report.project_id,
        "message_fr": report.message_fr,
        "action_fr": report.action_fr,
        "read_only": True,
        "automatic_restore": False,
        "cricut_qualified": False,
    })
    return 0 if report.status == "PROJECT_HEALTHY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
