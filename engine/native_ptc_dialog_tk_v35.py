"""W03 Tk Print Then Cut dialog: explicit preview, pinned identity and export."""
from __future__ import annotations

import base64
import os
from hashlib import sha256
from pathlib import Path
from tkinter import filedialog, messagebox
from smartsvg_core.native_ptc_export_v35 import (
    inspect_native_ptc_png, publish_native_ptc_png, NativePTCError,
)
from native_ptc_atelier_tk_v35 import ptc_preview_request

_ERRORS = {
    "PROJECT_CHANGED": "Le projet a changé. Réexaminer (F5), puis recommencer.",
    "PREVIEW_CHANGED": "Le PNG a changé depuis l'aperçu. Refaire l'aperçu.",
    "PHYSICAL_SIZE_NOT_SUPPORTED": "Dimensions physiques incompatibles : adapter la largeur en mm.",
    "OUTPUT_REQUIRES_REVIEW": "Écriture incertaine : vérifier le fichier manuellement, sans réessayer.",
    "EXPORT_DIRECTORY_NOT_FOUND": "Dossier introuvable : choisir un dossier existant.",
    "EXPORT_ALREADY_EXISTS": "Ce fichier existe déjà : choisir un autre nom, sans écrasement.",
    "OUTPUT_ALREADY_EXISTS": "Ce fichier existe déjà : choisir un autre nom, sans écrasement.",
    "UNSAFE_EXPORT_PATH": "Destination non sûre : choisir un autre dossier.",
    "EXPORT_PREPARATION_UNAVAILABLE": "Préparation impossible : réexaminer le projet (F5).",
}

def preview_identity(snapshot, subject, project_path, width_text):
    """Pure Tk admission; never write on invalid or stale selection."""
    req = ptc_preview_request(snapshot, subject, project_path, width_text)
    preview = getattr(subject, "preview", None)
    if req is None or preview is None:
        return None, "Sujet non vérifié : réexaminer le projet (F5)."
    # Inspector previews can be downsampled. Their dimensions are not the
    # archived source dimensions used by the native renderer to calculate PPI
    # and physical height. Rejecting here would incorrectly block valid exports.
    # inspect_native_ptc_png is read-only and performs the authoritative source
    # geometry and float32-mask validation before enabling publication.
    return req, None


def open_export_folder(target, opener=None):
    """Open only the directory of an existing, verified PNG export."""
    path = Path(target)
    if (not path.is_absolute() or path.suffix.lower() != ".png"
            or not path.is_file() or not path.parent.is_dir()):
        return False
    if opener is None:
        opener = getattr(os, "startfile", None)
    if opener is None:
        return False
    opener(str(path.parent))
    return True


def show_ptc_dialog(panel):
    """Modal Tk flow; no project write, no implicit export on open or cancel."""
    tk, ttk = panel.tk, panel.ttk
    if panel._closed or panel.busy or panel.history_requires_review or panel.has_open_brush:
        return False
    subject = panel.subjects.get(panel.selection.get())
    path, snapshot = panel._project_path, panel.snapshot
    if subject is None or snapshot is None:
        return False
    original = (path, snapshot.sha256, subject.subject_id)
    dialog = tk.Toplevel(panel.parent)
    dialog.title("Exporter le sujet · PNG Print Then Cut")
    dialog.transient(panel.parent)
    dialog.geometry("520x450")
    frame = ttk.Frame(dialog, padding=12)
    frame.pack(fill="both", expand=True)
    width = tk.StringVar(value="100")
    status = tk.StringVar(value="Saisir une largeur, puis examiner le PNG.")
    destination = tk.StringVar(value="")
    ttk.Label(frame, text="Largeur physique (mm) :").pack(anchor="w")
    ttk.Entry(frame, textvariable=width).pack(fill="x")
    ttk.Label(frame, textvariable=status, wraplength=470).pack(anchor="w", pady=8)
    ttk.Label(frame, textvariable=destination, wraplength=470).pack(anchor="w")
    image_label = ttk.Label(frame)
    image_label.pack(pady=8)
    actions = ttk.Frame(frame)
    actions.pack(fill="x")
    preview = None
    request = None
    busy = False
    closed = False
    published_target = None

    def open_folder():
        if published_target is None or not current():
            status.set("Dossier indisponible : réexaminer le projet ou republier.")
            return
        try:
            if not open_export_folder(published_target):
                status.set("Ouverture du dossier indisponible sur ce système.")
        except OSError:
            status.set("Impossible d’ouvrir le dossier : utiliser le chemin affiché.")

    def invalidate_preview(*_args):
        nonlocal preview, request
        preview = request = None
        export_button.configure(state="disabled")
        status.set("Largeur modifiée : examiner à nouveau avant toute publication.")

    def current():
        return (not closed and not panel._closed and not panel.busy
                and not panel.history_requires_review and not panel.has_open_brush
                and (panel._project_path, getattr(panel.snapshot, "sha256", None),
                     panel.selection.get()) == original
                and panel.subjects.get(original[2]) is subject)

    def close():
        nonlocal closed
        if busy:
            status.set("Export en cours : attendre le résultat avant de fermer.")
            return
        closed = True
        dialog.destroy()

    def inspect():
        nonlocal preview, request
        preview = request = None
        export_button.configure(state="disabled")
        if not current():
            status.set("Sélection ou révision modifiée : réexaminer (F5).")
            return
        req, issue = preview_identity(panel.snapshot, subject, path, width.get())
        if issue:
            status.set(issue)
            return
        try:
            result = inspect_native_ptc_png(**req)
            if not current() or result.get("status") != "PTC_PREVIEW_READY":
                status.set("Aperçu périmé : recommencer.")
                return
            raw = result["preview_png_rgba"]
            image = tk.PhotoImage(master=dialog, data=base64.b64encode(raw), format="png")
            image_label.configure(image=image)
            image_label.image = image
            request, preview = req, result
            status.set("Sujet " + original[2] + " · SHA projet " + original[1][:12]
                       + " · PNG " + result["output_sha256"][:12]
                       + " · " + str(result["width_mm"]) + " × "
                       + str(result["height_mm"]) + " mm"
                       + (" · résolution faible" if result["low_resolution_warning"] else ""))
            export_button.configure(state="normal")
        except (NativePTCError, ValueError, OSError, tk.TclError) as exc:
            status.set(_ERRORS.get(getattr(exc, "code", ""), "Aperçu impossible : réexaminer (F5)."))

    def export():
        nonlocal busy, published_target
        if preview is None or request is None or not current():
            status.set("Aperçu périmé : recommencer.")
            return
        if ptc_preview_request(panel.snapshot, subject, path, width.get()) != request:
            status.set("Largeur modifiée : refaire l'aperçu.")
            return
        target = filedialog.asksaveasfilename(parent=dialog, title="Destination PNG",
                                               defaultextension=".png",
                                               filetypes=[("Image PNG", "*.png")])
        if not target:
            return
        if not current() or Path(target).suffix.lower() != ".png":
            status.set("Destination ou sélection invalide.")
            return
        if Path(target).exists():
            status.set("Ce fichier existe déjà : choisir un autre nom, sans écrasement.")
            return
        destination.set(target)
        if not messagebox.askyesno("Confirmer l'export", "Publier ce PNG sans écraser de fichier existant ?",
                                   parent=dialog, default="no"):
            return
        if not current() or ptc_preview_request(panel.snapshot, subject, path, width.get()) != request:
            status.set("Révision ou largeur modifiée : refaire l'aperçu.")
            return
        if Path(target).exists():
            status.set("Le fichier vient d’apparaître : choisir une autre destination.")
            return
        busy = True
        published_target = None
        folder_button.configure(state="disabled")
        export_button.configure(state="disabled")
        try:
            receipt = publish_native_ptc_png(**request, destination_path=target,
                       expected_output_sha256=preview["output_sha256"], confirmed=True)
            if receipt.get("persisted") is not True:
                status.set("Résultat incertain : vérifier le fichier avant tout nouvel essai.")
            else:
                with open(target, "rb") as stream:
                    digest = sha256(stream.read()).hexdigest()
                if digest != preview["output_sha256"]:
                    status.set("Relecture différente : vérifier le fichier, ne pas réessayer.")
                else:
                    published_target = target
                    folder_button.configure(state="normal")
                    status.set("PNG enregistré et relu · SHA " + digest[:12]
                               + " · dossier : " + str(Path(target).parent))
        except (NativePTCError, OSError) as exc:
            status.set(_ERRORS.get(getattr(exc, "code", ""),
                                   "Export incertain : vérifier le fichier avant de réessayer."))
        finally:
            busy = False

    ttk.Button(actions, text="Examiner", command=inspect).pack(side="left")
    export_button = ttk.Button(actions, text="Choisir et publier…", command=export, state="disabled")
    export_button.pack(side="left", padx=6)
    folder_button = ttk.Button(actions, text="Ouvrir le dossier", command=open_folder, state="disabled")
    folder_button.pack(side="left", padx=6)
    width.trace_add("write", invalidate_preview)
    ttk.Button(actions, text="Fermer", command=close).pack(side="left")
    dialog.protocol("WM_DELETE_WINDOW", close)
    return True
