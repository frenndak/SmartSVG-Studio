"""V34-019 native desktop shell: inspect V1 projects without ComfyUI.

This is a deliberately read-only, offline Tkinter prototype, NOT a packaged
Windows application or a validated rendering/editing environment. Tkinter is
loaded only when an actual graphical session is requested.

    python engine/standalone_desktop_v34.py
    python engine/standalone_desktop_v34.py --project mon_projet.smartsvg
    python -I -S engine/standalone_desktop_v34.py --probe
"""
from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
import sys

# A direct script entry point avoids engine/__init__.py (legacy ComfyUI nodes).
_ENGINE_DIR = str(Path(__file__).resolve().parent)
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)

from smartsvg_core.project_archive import ProjectArchiveError, load_project
from smartsvg_core.project_recovery import RecoveryError, inspect_project
from smartsvg_core.source_preview_v34 import select_source_png


def inspect_native_project(path: str | Path) -> dict:
    """Read an existing .smartsvg V1. Never restore, save, or expose its bytes."""
    try:
        report = inspect_project(path)
    except (RecoveryError, OSError) as exc:
        return {
            "ok": False, "status": "PROJECT_INSPECTION_FAILED",
            "error_code": exc.code if isinstance(exc, RecoveryError) else "PROJECT_READ_FAILED",
            "read_only": True,
        }
    details = {
        "ok": report.status == "PROJECT_HEALTHY",
        "status": report.status,
        "primary": report.primary,
        "previous": report.previous,
        "project_id": report.project_id,
        "message_fr": report.message_fr,
        "action_fr": report.action_fr,
        "read_only": True,
        "automatic_restore": False,
        "windows_qualified": False,
        "cricut_qualified": False,
    }
    if report.status != "PROJECT_HEALTHY":
        return details
    # Re-read the validated V1 using the existing untrusted-ZIP parser. A
    # project that changes between these reads is not shown as healthy.
    try:
        project = load_project(path)
    except (ProjectArchiveError, OSError):
        details.update({
            "ok": False,
            "status": "PROJECT_CHANGED_DURING_INSPECTION",
            "message_fr": "Le projet a changé pendant son examen.",
            "action_fr": "Réexaminer le fichier avant toute modification.",
        })
        details.pop("project_id", None)
        return details
    details.update({
        "project_id": project.project_id,
        "app_version": project.app_version,
        "sources": len(project.sources),
        "masks": len(project.masks),
        "subjects": len(project.subjects),
        "artifacts": len(project.artifacts),
    })
    return details


def _probe() -> int:
    forbidden = ("engine", "nodes", "server", "folder_paths", "torch", "aiohttp", "tkinter")
    imported = sorted(name for name in forbidden if name in sys.modules or
                      any(module.startswith(name + ".") for module in sys.modules))
    result = {
        "ok": not imported, "phase": "V34-019_DESKTOP_SHELL",
        "comfyui_required": False, "read_only": True,
        "tkinter_lazy": "tkinter" not in imported,
        "desktop_ui_tested": False, "windows_qualified": False,
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if not imported else 2


def _start_gui(first_project: str | None) -> int:
    try:
        import tkinter as tk
        from tkinter import filedialog, ttk
    except ImportError:
        print("Interface graphique Tkinter indisponible dans cet environnement.", file=sys.stderr)
        return 2

    try:
        root = tk.Tk()
    except tk.TclError:
        print("Aucune session graphique locale disponible.", file=sys.stderr)
        return 2

    root.title("SmartSVG Studio V3.4 — prototype autonome")
    root.geometry("780x630")
    root.minsize(610, 520)

    frame = ttk.Frame(root, padding=22)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="SmartSVG Studio", font=("Segoe UI", 18, "bold")).pack(anchor="w")
    ttk.Label(frame,
              text="Prototype local indépendant de ComfyUI • lecture seule • sans IA",
              wraplength=640).pack(anchor="w", pady=(4, 18))

    file_name = tk.StringVar(value="Aucun projet sélectionné")
    message = tk.StringVar(value="Ouvrez un fichier .smartsvg pour examiner son état.")
    summary = tk.StringVar(value="Aucune ressource chargée.")
    preview_info = tk.StringVar(value="Aucun aperçu chargé.")
    photo_holder: list[object | None] = [None]
    current: list[str | None] = [None]

    ttk.Label(frame, textvariable=file_name, font=("Segoe UI", 11, "bold"),
              wraplength=640).pack(anchor="w", pady=(0, 12))
    ttk.Label(frame, textvariable=message, wraplength=640).pack(anchor="w", pady=(0, 12))
    ttk.Label(frame, textvariable=summary, wraplength=640).pack(anchor="w")
    ttk.Label(frame, textvariable=preview_info, wraplength=640).pack(anchor="w", pady=(16, 5))
    preview_panel = ttk.Label(frame)
    preview_panel.pack(anchor="w")

    def refresh(*_unused):
        if not current[0]:
            return
        # Clear the previous photo before loading a different project.
        preview_panel.configure(image="")
        photo_holder[0] = None
        preview_info.set("Aperçu non disponible.")
        state = inspect_native_project(current[0])
        message.set(state.get("message_fr") or state.get("error_code") or state["status"])
        if state.get("ok"):
            summary.set(
                "Projet : {}  •  Version : {}  •  Sources : {}  •  Masques : {}  "
                "•  Sujets : {}  •  Exports : {}".format(
                    state["project_id"], state["app_version"], state["sources"],
                    state["masks"], state["subjects"], state["artifacts"]))
            try:
                # Existing validated V1 reader; no export, network or disk write.
                project = load_project(current[0])
                if project.project_id != state["project_id"]:
                    preview_info.set("Projet modifié depuis l'inspection : réexaminer.")
                else:
                    preview = select_source_png(project)
                    if preview.status == "READY_PNG":
                        original = tk.PhotoImage(
                            data=base64.b64encode(preview.png).decode("ascii"),
                            format="png")
                        display = (original.subsample(preview.subsample)
                                   if preview.subsample > 1 else original)
                        preview_panel.configure(image=display)
                        photo_holder[0] = display
                        preview_info.set(
                            f"Source {preview.source_id} — "
                            f"{preview.width_px} × {preview.height_px} px "
                            f"(affichage réduit ×{preview.subsample}; originaux intacts)")
                    else:
                        explanations = {
                            "NO_SOURCE": "Projet sans image source.",
                            "SOURCE_FORMAT_UNSUPPORTED":
                                "Aperçu limité aux sources PNG : JPEG/WebP à venir.",
                            "SOURCE_TOO_LARGE":
                                "Image trop grande pour l'aperçu sécurisé.",
                            "SOURCE_CHANGED": "Source modifiée : aperçu refusé.",
                            "SOURCE_INVALID_PNG": "Source PNG invalide : aperçu refusé.",
                            "SOURCE_MISSING": "Source absente : aperçu refusé.",
                        }
                        preview_info.set(explanations.get(
                            preview.status, "Aperçu non disponible."))
            except (ProjectArchiveError, OSError, tk.TclError):
                preview_panel.configure(image="")
                photo_holder[0] = None
                preview_info.set("Aperçu indisponible : réexaminer le projet.")
        else:
            summary.set("Aucune modification effectuée. " +
                        (state.get("action_fr") or "Contrôlez le projet avant de réessayer."))

    def select_project():
        chosen = filedialog.askopenfilename(
            parent=root, title="Ouvrir un projet SmartSVG",
            filetypes=[("Projets SmartSVG", "*.smartsvg")])
        if chosen:
            current[0] = chosen
            file_name.set(Path(chosen).name)
            refresh()

    buttons = ttk.Frame(frame)
    buttons.pack(anchor="w", pady=(24, 0))
    ttk.Button(buttons, text="Ouvrir un projet…", command=select_project).pack(side="left")
    ttk.Button(buttons, text="Réexaminer (F5)", command=refresh).pack(side="left", padx=12)
    root.bind("<F5>", refresh)
    ttk.Separator(frame).pack(fill="x", pady=(25, 12))
    ttk.Label(frame, text=(
        "Aperçu PNG source uniquement : pas de dessin, d'export, de sauvegarde, "
        "de restauration, de téléchargement ou de découpe Cricut."
    ), wraplength=660).pack(anchor="w")

    if first_project:
        current[0] = first_project
        file_name.set(Path(first_project).name)
        refresh()
    root.mainloop()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="SmartSVG : prototype bureau sans ComfyUI")
    parser.add_argument("--probe", action="store_true",
                        help="Contrôler le démarrage sans dépendances graphiques")
    parser.add_argument("--project", default=None,
                        help="Projet .smartsvg à inspecter au lancement graphique")
    args = parser.parse_args(argv)
    if args.probe:
        return _probe()
    return _start_gui(args.project)


if __name__ == "__main__":
    raise SystemExit(main())
