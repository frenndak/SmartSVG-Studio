"""V34-019 native desktop shell: inspect V1 projects without ComfyUI.

Explicit PNG creation, notes edits and recovery use the V1 backend.
This is an offline Tkinter prototype, NOT a packaged
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

from smartsvg_core.project_archive import MAX_ARCHIVE_BYTES, ProjectArchiveError
from smartsvg_core.project_recovery import (
    RecoveryError, inspect_project_snapshot, inspect_recovery_plan,
)
from smartsvg_core.source_preview_v34 import select_source_png
from smartsvg_core.native_preview_jobs_v34 import LatestOnlyJob
from native_theme_tk_v34 import ArtisanThemePicker
from native_templates_tk_v34 import TemplatePreviewContent
from native_app_shell_v34 import NativeAppShell
from native_atelier_tk_v34 import NativeAtelierPanel
from smartsvg_core.native_atelier_v34 import inspect_atelier_snapshot
from native_create_tk_v34 import NativeCreateDialog
from native_notes_tk_v34 import NativeNotesPanel, NotesRevision
from native_recovery_tk_v34 import NativeRecoveryPanel
from smartsvg_core.project_workspace_g22 import MAX_NOTE_LENGTH, NAME


def inspect_native_project(path: str | Path) -> dict:
    """Read an existing .smartsvg V1. Never restore, save, or expose its bytes."""
    return _inspect_native_project_snapshot(path)[0]


def _changed_project():
    return {
        "ok": False,
        "status": "PROJECT_CHANGED_DURING_INSPECTION",
        "message_fr": "Le projet a changé pendant son examen.",
        "action_fr": "Réexaminer le fichier avant de continuer.",
        "read_only": True,
    }


def _inspect_native_project_snapshot(path):
    before = _archive_sha256(path)
    try:
        report, project = inspect_project_snapshot(path, expected_sha256=before)
    except ProjectArchiveError:
        return _changed_project(), None, None
    except (RecoveryError, OSError) as exc:
        return {
            "ok": False, "status": "PROJECT_INSPECTION_FAILED",
            "error_code": exc.code if isinstance(exc, RecoveryError) else "PROJECT_READ_FAILED",
            "read_only": True,
        }, None, None
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
        return details, None, None
    if project is None or before is None or _archive_sha256(path) != before:
        return _changed_project(), None, None
    details.update({
        "project_id": project.project_id,
        "app_version": project.app_version,
        "sources": len(project.sources),
        "masks": len(project.masks),
        "subjects": len(project.subjects),
        "artifacts": len(project.artifacts),
    })
    return details, project, before


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

    The initial digest precedes inspection. Summary and image share the same
    validated in-memory project; digest checks reject changes during inspection
    or preview selection. No cache is retained between calls.
    """
    state, project, before = _inspect_native_project_snapshot(path)
    if not state.get("ok"):
        if state['status'] in ('PROJECT_RECOVERABLE', 'PENDING_BACKUP_REVIEW_REQUIRED'):
            target = Path(path)
            if target.suffix.lower() == '.smartsvg' and NAME.fullmatch(target.stem):
                state['recovery_plan'] = inspect_recovery_plan(target)
            state['action_fr'] = (
                'Consultez la copie vérifiée et confirmez l’action proposée.'
                if state.get('recovery_plan') else
                'Récupération indisponible. Conservez les fichiers et réexaminez le projet.'
            )
        return state, None
    try:
        preview = select_source_png(project)
        state['atelier_snapshot'] = inspect_atelier_snapshot(project, before)
        # One final boundary check before returning any image to the UI.
        if _archive_sha256(path) != before:
            raise ProjectArchiveError("PROJECT_SNAPSHOT_CHANGED")
        target = Path(path)
        notes = project.document.get('notes', '')
        if (target.suffix == '.smartsvg' and target.stem == project.project_id
                and NAME.fullmatch(target.stem)
                and not target.stem.endswith('_previous')
                and isinstance(notes, str) and len(notes) <= MAX_NOTE_LENGTH):
            state['notes_revision'] = NotesRevision(target.absolute(), project.project_id, before, notes)
        return state, preview
    except (ProjectArchiveError, OSError):
        return _changed_project(), None


def _project_path(selection):
    """The chooser can locate a missing primary via an existing sidecar."""
    path = Path(selection)
    for suffix in ('.previous.smartsvg', '.pending-backup.smartsvg'):
        if path.name.lower().endswith(suffix) and NAME.fullmatch(path.name[:-len(suffix)]):
            return str(path.with_name(path.name[:-len(suffix)] + '.smartsvg'))
    return selection


def _probe() -> int:
    forbidden = ("engine", "nodes", "server", "folder_paths", "torch", "aiohttp", "tkinter")
    imported = sorted(name for name in forbidden if name in sys.modules or
                      any(module.startswith(name + ".") for module in sys.modules))
    result = {
        "ok": not imported, "phase": "V34-019_DESKTOP_SHELL",
        "comfyui_required": False, "read_only": False,
        "project_notes_available": True, "project_creation_available": True,
        "project_recovery_available": True,
        "atelier_inspection_available": True,
        "tkinter_lazy": "tkinter" not in imported,
        "desktop_ui_tested": False, "windows_qualified": False,
        "template_previews_available": True,
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if not imported else 2


def _start_gui(first_project: str | None) -> int:
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk
    except ImportError:
        print("Interface graphique Tkinter indisponible dans cet environnement.", file=sys.stderr)
        return 2

    try:
        root = tk.Tk()
    except tk.TclError:
        print("Aucune session graphique locale disponible.", file=sys.stderr)
        return 2

    shell = NativeAppShell(root, tk, ttk)
    home = shell.add_page('home', 'Accueil')
    frame = shell.add_page('project', 'Projet')
    factory = shell.add_page('factory', 'Fabrique')
    appearance = shell.add_page('appearance', 'Apparence')
    atelier = NativeAtelierPanel(shell.add_page('atelier', 'Atelier'), tk, ttk)
    # Build each tool once. Navigation changes visibility, never the project.
    # Load preferences immediately so the first screen uses the saved theme.
    theme_picker = ArtisanThemePicker(root=root, parent=appearance, tk=tk, ttk=ttk)
    template_panel = TemplatePreviewContent(factory, tk, ttk)

    ttk.Label(frame, text='Votre projet', font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 12))
    # Reserve primary actions above the image, including at minimum size.
    buttons = ttk.Frame(frame)
    buttons.pack(anchor="w", pady=(0, 12))
    file_name = tk.StringVar(value="Aucun projet sélectionné")
    message = tk.StringVar(value="Ouvrez un fichier .smartsvg pour examiner son état.")
    summary = tk.StringVar(value="Aucune ressource chargée.")
    preview_info = tk.StringVar(value="Aucun aperçu chargé.")
    photo_holder: list[object | None] = [None]
    current: list[str | None] = [None]
    creator = [None]
    creation_info = tk.StringVar(value='')
    ttk.Label(frame, textvariable=creation_info, wraplength=640).pack(anchor='w')

    ttk.Label(frame, textvariable=file_name, font=("Segoe UI", 11, "bold"),
              wraplength=640).pack(anchor="w", pady=(0, 12))
    ttk.Label(frame, textvariable=message, wraplength=640).pack(anchor="w", pady=(0, 12))
    ttk.Label(frame, textvariable=summary, wraplength=640).pack(anchor="w")
    recovery_slot = ttk.Frame(frame)
    recovery_slot.pack(fill='x')
    notes = NativeNotesPanel(root, frame, tk, ttk, messagebox,
                             on_saved=lambda revision: refresh(saved_notes=revision))
    ttk.Label(frame, textvariable=preview_info, wraplength=640).pack(anchor="w", pady=(16, 5))
    preview_panel = ttk.Label(frame)
    preview_panel.pack(anchor="w")

    jobs = LatestOnlyJob(load_native_preview)
    selected_subject = None

    def refresh(*, saved_notes=None):
        nonlocal selected_subject
        if not current[0]:
            return
        if saved_notes is None:
            selected_subject = None
            notes.load(None)
        else:
            selected_subject = atelier.selection.get() or selected_subject
        atelier.load(None)
        atelier.project.set("Vérification de la révision du projet…")
        recovery.load(None)
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
                atelier.project.set("Impossible de lire ce projet.")
                return

            snapshot = state.get('atelier_snapshot')
            if saved_notes is not None and (
                    snapshot is None or snapshot.sha256 != saved_notes.sha256
                    or snapshot.project_id != saved_notes.project_id):
                message.set("La révision enregistrée ne peut plus être vérifiée. Réexaminez le projet (F5).")
                summary.set("Aucune ressource chargée pour cette révision.")
                preview_info.set("Aperçu indisponible.")
                atelier.project.set("La révision a changé. Réexaminez le projet (F5).")
                return
            message.set(state.get("message_fr") or state.get("error_code") or state["status"])
            if not state.get("ok"):
                recovery.load(state.get('recovery_plan'))
                atelier.project.set("Ouvrez ou récupérez un projet V1 sain depuis l’espace Projet.")
                summary.set("Aucune modification effectuée. " +
                            (state.get("action_fr") or "Contrôlez le projet avant de réessayer."))
                preview_info.set("Aperçu non disponible.")
                return

            summary.set(
                "Projet : {}  •  Version : {}  •  Sources : {}  •  Masques : {}  "
                "•  Sujets : {}  •  Exports : {}".format(
                    state["project_id"], state["app_version"], state["sources"],
                    state["masks"], state["subjects"], state["artifacts"]))

            if saved_notes is None:
                notes.load(state.get('notes_revision'))
            atelier.load(snapshot, selected_subject=selected_subject)
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

    def creation_busy():
        return creator[0] is not None and creator[0].busy

    def open_created(receipt):
        recovery.status.set('')
        current[0] = receipt.path
        file_name.set(Path(receipt.path).name)
        creation_info.set('Projet créé, enregistré et relu · SHA ' + receipt.sha256[:12])
        shell.show('project', focus=True)
        refresh()

    def reexamine():
        if recovery.busy:
            return 'break'
        if creation_busy():
            return show_creator()
        if notes.can_leave():
            shell.show('project', focus=True)
            refresh()
        return 'break'

    def show_creator(*_unused):
        if recovery.busy:
            return 'break'
        if creator[0] is not None and creator[0].window.winfo_exists():
            creator[0].window.lift()
        else:
            creator[0] = NativeCreateDialog(
                root, tk, ttk, filedialog, open_created,
                can_create=lambda: not recovery.busy and notes.can_leave())
        return 'break'

    def select_project():
        if recovery.busy:
            return
        if creation_busy():
            show_creator()
            return
        chosen = filedialog.askopenfilename(
            parent=root, title="Ouvrir un projet SmartSVG",
            filetypes=[("Projets SmartSVG", "*.smartsvg")])
        if chosen and not recovery.busy and notes.can_leave():
            creation_info.set('')
            recovery.status.set('')
            shell.show('project', focus=True)
            current[0] = _project_path(chosen)
            file_name.set(Path(current[0]).name)
            refresh()

    recovery = NativeRecoveryPanel(root, recovery_slot, tk, ttk, messagebox, refresh,
                                   lambda: not creation_busy() and notes.can_leave())

    ttk.Button(buttons, text="Ouvrir un projet…", command=select_project).pack(side="left")
    ttk.Button(buttons, text="Créer depuis un PNG…", command=show_creator).pack(side="left", padx=12)
    ttk.Button(buttons, text="Réexaminer (F5)", command=reexamine).pack(side="left")

    ttk.Label(home, text='Que souhaitez-vous préparer ?',
              font=('Segoe UI', 18, 'bold')).pack(anchor='w', pady=(6, 16))
    ttk.Label(home, text=(
        'Retrouvez vos créations et explorez les gabarits dans une même fenêtre. '
        'Les espaces conservent leur état pendant la navigation.'),
        wraplength=620).pack(anchor='w', pady=(0, 22))
    ttk.Button(home, text='Créer depuis un PNG…', command=show_creator).pack(anchor='w', pady=6)
    ttk.Label(home, text='Choisir une image, enregistrer un nouveau projet et l’ouvrir après vérification.',
              wraplength=620).pack(anchor='w', pady=(0, 16))
    ttk.Button(home, text='Ouvrir un projet…', command=select_project).pack(anchor='w', pady=6)
    ttk.Label(home, text='Examiner un projet ou sélectionner son fichier de secours si le projet principal manque.',
              wraplength=620).pack(anchor='w', pady=(0, 16))
    ttk.Button(home, text='Préparer un gabarit',
               command=lambda: shell.show('factory', focus=True)).pack(anchor='w', pady=6)
    ttk.Label(home, text='Carte pliée ou boîte ouverte : dimensions en mm et aperçu CUT / SCORE.',
              wraplength=620).pack(anchor='w', pady=(0, 16))
    ttk.Button(home, text='Personnaliser mon espace',
               command=lambda: shell.show('appearance', focus=True)).pack(anchor='w', pady=6)
    ttk.Label(home, text='Thème et couleurs enregistrés localement pour toute l’application.',
              wraplength=620).pack(anchor='w', pady=(0, 16))

    def open_shortcut(_event):
        select_project()
        return 'break'

    for key, action in (('<Control-o>', open_shortcut), ('<Control-n>', show_creator),
                        ('<F5>', lambda _event: reexamine())):
        root.bind(key, action)
        # Tk's Text class processes shortcuts before the root bindtag.
        # Ctrl+O must open the picker without inserting a newline first.
        notes.editor.bind(key, action)
    shell.show('home')

    if first_project:
        shell.show('project', focus=True)
        current[0] = _project_path(first_project)
        file_name.set(Path(current[0]).name)
        refresh()
    def close_window():
        if recovery.busy:
            return
        if creation_busy():
            creator[0].close()
            creator[0].window.lift()
            return
        if not notes.can_leave():
            return
        if creator[0] is not None:
            creator[0].close()
        # A pending or obsolete generation is never allowed to update Tk.
        jobs.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close_window)
    try:
        root.mainloop()
    finally:
        if creator[0] is not None:
            creator[0].shutdown()
        jobs.close()
        notes.shutdown()
        recovery.shutdown()
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
