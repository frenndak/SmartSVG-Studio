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
from hashlib import sha256
import json
from pathlib import Path
import sys

# A direct script entry point avoids engine/__init__.py (legacy ComfyUI nodes).
_ENGINE_DIR = str(Path(__file__).resolve().parent)
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)

from smartsvg_core.project_archive import MAX_ARCHIVE_BYTES, ProjectArchiveError, load_project
from smartsvg_core.project_recovery import RecoveryError, inspect_project
from smartsvg_core.source_preview_v34 import select_source_png
from smartsvg_core.native_preview_jobs_v34 import LatestOnlyJob
from native_theme_tk_v34 import ArtisanThemePicker


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




def _archive_sha256(path: str | Path) -> str | None:
    """Bounded read-only SHA before/after inspection: fail closed on a swap.

    This is not a filesystem lock and does not certify concurrent writer safety;
    it prevents presenting two different revisions of a single project ID.
    """
    try:
        target = Path(path)
        if (target.suffix.lower() != ".smartsvg" or target.is_symlink()
                or not target.is_file() or target.stat().st_size > MAX_ARCHIVE_BYTES):
            return None
        digest = sha256()
        with target.open("rb") as stream:
            total = 0
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                total += len(chunk)
                if total > MAX_ARCHIVE_BYTES:
                    return None
                digest.update(chunk)
        return digest.hexdigest()
    except (OSError, ValueError, TypeError):
        return None


def load_native_preview(path: str | Path):
    """Inspect and preview one verified revision, or refuse if bytes changed.

    The initial digest is acquired BEFORE the first inspection. A digest after
    the second archive read must match; project_id by itself is insufficient.
    Does not mutate the archive or open external network resources.
    """
    before = _archive_sha256(path)
    state = inspect_native_project(path)
    if not state.get("ok"):
        return state, None
    try:
        project = load_project(path)
        after = _archive_sha256(path)
        if (before is None or after is None or before != after
                or project.project_id != state["project_id"]
                or project.app_version != state["app_version"]
                or len(project.sources) != state["sources"]
                or len(project.masks) != state["masks"]
                or len(project.subjects) != state["subjects"]
                or len(project.artifacts) != state["artifacts"]):
            raise ProjectArchiveError("PROJECT_SNAPSHOT_CHANGED")
        preview = select_source_png(project)
        # One final boundary check before returning any image to the UI.
        if _archive_sha256(path) != before:
            raise ProjectArchiveError("PROJECT_SNAPSHOT_CHANGED")
        return state, preview
    except (ProjectArchiveError, OSError):
        return {
            "ok": False,
            "status": "PROJECT_CHANGED_DURING_INSPECTION",
            "message_fr": "Le projet a changé pendant son examen.",
            "action_fr": "Réexaminer le fichier avant de continuer.",
            "read_only": True,
        }, None


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
    root.geometry("920x710")
    root.minsize(770, 600)

    frame = ttk.Frame(root, padding=22)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="SmartSVG Studio", font=("Segoe UI", 18, "bold")).pack(anchor="w")
    ttk.Label(frame,
              text="Prototype local indépendant de ComfyUI • lecture seule • sans IA",
              wraplength=720).pack(anchor="w", pady=(4, 18))
    # UI preferences never enter the .smartsvg archive or its undo history.
    # Kept independent of the final choice of GUI framework.
    theme_picker = ArtisanThemePicker(root=root, parent=frame, tk=tk, ttk=ttk)

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

    jobs = LatestOnlyJob(load_native_preview)

    def refresh(*_unused):
        if not current[0]:
            return
        # Only the Tk main thread manipulates PhotoImage and widgets.
        preview_panel.configure(image="")
        photo_holder[0] = None
        message.set("Analyse du projet en cours…")
        summary.set("Lecture et vérification sans modification.")
        preview_info.set("Préparation de l'aperçu…")
        version, future = jobs.submit(current[0])

        def receive():
            if not jobs.current(version):
                return  # stale result: never update another project's widgets
            if not future.done():
                root.after(50, receive)
                return
            try:
                state, preview = future.result()
            except Exception:
                # Unexpected reader failure: fail closed without private paths.
                message.set("Impossible de lire ce projet.")
                summary.set("Aucune modification effectuée.")
                preview_info.set("Aperçu indisponible.")
                return

            message.set(state.get("message_fr") or state.get("error_code") or state["status"])
            if not state.get("ok"):
                summary.set("Aucune modification effectuée. " +
                            (state.get("action_fr") or "Contrôlez le projet avant de réessayer."))
                preview_info.set("Aperçu non disponible.")
                return

            summary.set(
                "Projet : {}  •  Version : {}  •  Sources : {}  •  Masques : {}  "
                "•  Sujets : {}  •  Exports : {}".format(
                    state["project_id"], state["app_version"], state["sources"],
                    state["masks"], state["subjects"], state["artifacts"]))

            if preview is None:
                preview_info.set("Aperçu non disponible : réexaminer le projet.")
                return
            if preview.status != "READY_PNG":
                explanations = {
                    "NO_SOURCE": "Projet sans image source.",
                    "SOURCE_FORMAT_UNSUPPORTED": "Aperçu limité aux sources PNG.",
                    "SOURCE_TOO_LARGE": "Image trop grande pour l'aperçu sécurisé.",
                    "SOURCE_CHANGED": "Source modifiée : aperçu refusé.",
                    "SOURCE_INVALID_PNG": "PNG invalide : aperçu refusé.",
                    "SOURCE_MISSING": "Source absente : aperçu refusé.",
                }
                preview_info.set(explanations.get(preview.status, "Aperçu indisponible."))
                return
            try:
                # Bounded Tk decode on the GUI thread; PNG selector verifies
                # dimensions and SHA before any PhotoImage allocation.
                original = tk.PhotoImage(
                    data=base64.b64encode(preview.png).decode("ascii"), format="png")
                display = (original.subsample(preview.subsample)
                           if preview.subsample > 1 else original)
                preview_panel.configure(image=display)
                photo_holder[0] = display
                preview_info.set(
                    f"Source {preview.source_id} — "
                    f"{preview.width_px} × {preview.height_px} px "
                    f"(affichage réduit ×{preview.subsample}; originaux intacts)")
            except tk.TclError:
                preview_panel.configure(image="")
                photo_holder[0] = None
                preview_info.set("Décodage PNG impossible : aperçu refusé.")

        root.after(50, receive)

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
    def close_window():
        # A pending or obsolete generation is never allowed to update Tk.
        jobs.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close_window)
    root.mainloop()
    jobs.close()
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
