"""W03 Tk Print Then Cut dialog: explicit preview, pinned identity and export."""
from __future__ import annotations

import base64
import os
import math
import stat
import xml.etree.ElementTree as ET
from hashlib import sha256
from pathlib import Path
from tkinter import filedialog, messagebox
from smartsvg_core.native_ptc_export_v35 import (
    inspect_native_ptc_png, publish_native_ptc_png, NativePTCError,
)
from native_ptc_atelier_tk_v35 import ptc_preview_request
from smartsvg_core.native_basic_cut_subject_v35 import inspect_native_basic_cut_subject
from smartsvg_core.native_basic_cut_export_v35 import publish_native_basic_cut_svg
from smartsvg_core.native_basic_cut_v35 import BasicCutError

_ERRORS = {
    "PROJECT_CHANGED": "Le projet a changé. Réexaminer (F5), puis recommencer.",
    "PREVIEW_CHANGED": "La sortie a changé depuis l’aperçu. Refaire l’aperçu.",
    "EMPTY_CUT_SILHOUETTE": "Aucun contour découpable : retoucher le masque pour conserver une zone opaque.",
    "MULTIPLE_CUT_COMPONENTS": "Plusieurs contours séparés : choisissez un sujet continu ou retouchez le masque.",
    "AMBIGUOUS_CORNER_CONTACT": "Des zones se touchent seulement par un coin : séparez ou reliez ces zones dans la retouche.",
    "SILHOUETTE_TOO_COMPLEX": "Contour trop détaillé : simplifiez la silhouette ou sélectionnez un sujet plus simple.",
    "GEOMETRY_TOO_COMPLEX": "Contour trop détaillé : simplifiez la silhouette ou sélectionnez un sujet plus simple.",
    "DEGENERATE_CUT_CONTOUR": "Contour trop mince ou incomplet : retouchez le masque puis réessayez.",
    "OPEN_CUT_CONTOUR": "Contour ouvert : retouchez le masque pour obtenir une silhouette fermée.",
    "INVALID_SIZE": "Dimensions physiques incompatibles : adapter la largeur en mm.",
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


# The native PNG renderer caps the source at five million RGBA pixels.
# 32 MiB covers the resulting lossless PNG plus its framing/metadata; the
# SVG path uses the exact inspected byte count, not an arbitrary larger file.
_MAX_PNG_READBACK = 32 * 1024 * 1024


def _readback_digest(target, limit):
    """Bound UI readback and refuse a substituted non-regular output.

    The publisher already verifies its own write. This independent UI
    readback must not load a concurrently replaced arbitrary file into RAM.
    """
    def regular(info):
        return (stat.S_ISREG(info.st_mode)
                and not (getattr(info, "st_file_attributes", 0)
                         & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))
                and 0 < info.st_size <= limit)

    def identity(info):
        return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns)

    before = os.lstat(target)
    if not regular(before):
        return None
    flags = (os.O_RDONLY | getattr(os, "O_BINARY", 0)
             | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    fd = os.open(target, flags)
    try:
        opened = os.fstat(fd)
        if not regular(opened) or identity(opened) != identity(before):
            return None
        digest = sha256()
        total = 0
        while True:
            block = os.read(fd, min(1024 * 1024, limit - total + 1))
            if not block:
                break
            total += len(block)
            if total > limit:
                return None
            digest.update(block)
        after = os.fstat(fd)
        final = os.lstat(target)
        if (total != opened.st_size or not regular(after) or not regular(final)
                or identity(after) != identity(opened)
                or identity(final) != identity(opened)):
            return None
        return digest.hexdigest()
    finally:
        os.close(fd)


def _draw_cut_preview(canvas, result):
    """Draw only the bounded, generated M/L/Z contour; never load external SVG."""
    raw = result.svg
    if (type(raw) is not bytes or len(raw) > 131072
            or sha256(raw).hexdigest() != result.svg_sha256
            or b"<!DOCTYPE" in raw or b"<!ENTITY" in raw):
        raise ValueError("INVALID_CUT_PREVIEW")
    root = ET.fromstring(raw)
    ns = "{http://www.w3.org/2000/svg}"
    w, h = result.width_mm, result.height_mm
    if (root.tag != ns + "svg" or len(root) != 1
            or root[0].tag != ns + "path" or len(root[0])
            or not all(math.isfinite(v) and 0.01 <= v <= 10000 for v in (w, h))
            or [float(v) for v in root.attrib["viewBox"].split()] != [0, 0, w, h]):
        raise ValueError("INVALID_CUT_PREVIEW")
    rings = root[0].attrib["d"].split(" Z")
    if rings[-1] != "" or len(rings) - 1 != result.ring_count or not 1 <= result.ring_count <= 32:
        raise ValueError("INVALID_CUT_PREVIEW")
    scale = min(440 / w, 196 / h)
    ox, oy = (460 - w * scale) / 2, (216 - h * scale) / 2
    lines = []
    count = 0
    for ring in rings[:-1]:
        tokens = ring.strip().split()
        if len(tokens) < 9 or len(tokens) % 3 or tokens[0] != "M":
            raise ValueError("INVALID_CUT_PREVIEW")
        coords = []
        for i in range(0, len(tokens), 3):
            x, y = float(tokens[i + 1]), float(tokens[i + 2])
            if (tokens[i] != ("M" if i == 0 else "L")
                    or not (0 <= x <= w and 0 <= y <= h)):
                raise ValueError("INVALID_CUT_PREVIEW")
            coords.extend((ox + x * scale, oy + y * scale))
            count += 1
        if count > 512:
            raise ValueError("INVALID_CUT_PREVIEW")
        lines.append(coords + coords[:2])
    canvas.delete("all")
    for line in lines:
        canvas.create_line(*line, fill="#164e63", width=2)


def show_ptc_dialog(panel):
    """Existing PNG workflow."""
    return _show_export_dialog(panel, basic_cut=False)


def show_basic_cut_dialog(panel):
    """Distinct Basic Cut SVG workflow using the same revision/consent guards."""
    return _show_export_dialog(panel, basic_cut=True)


def _show_export_dialog(panel, *, basic_cut):
    """No project write, no implicit export on open or cancel."""
    kind = "SVG" if basic_cut else "PNG"
    suffix = ".svg" if basic_cut else ".png"
    label = "SVG Basic Cut" if basic_cut else "PNG Print Then Cut"
    tk, ttk = panel.tk, panel.ttk
    if panel._closed or panel.busy or panel.history_requires_review or panel.has_open_brush:
        return False
    subject = panel.subjects.get(panel.selection.get())
    path, snapshot = panel._project_path, panel.snapshot
    if subject is None or snapshot is None:
        return False
    original = (path, snapshot.sha256, subject.subject_id)
    dialog = tk.Toplevel(panel.parent)
    dialog.title("Exporter le sujet · " + label)
    dialog.transient(panel.parent)
    dialog.geometry("520x450")
    frame = ttk.Frame(dialog, padding=12)
    frame.pack(fill="both", expand=True)
    width = tk.StringVar(value="100")
    status = tk.StringVar(value="Saisir une largeur, puis examiner le " + kind + ".")
    destination = tk.StringVar(value="")
    ttk.Label(frame, text="Largeur physique (mm) :").pack(anchor="w")
    ttk.Entry(frame, textvariable=width).pack(fill="x")
    ttk.Label(frame, textvariable=status, wraplength=470).pack(anchor="w", pady=8)
    ttk.Label(frame, textvariable=destination, wraplength=470).pack(anchor="w")
    # Reserve the bottom action row before placing variable-height preview text/image.
    # The export and close controls must remain reachable with long paths/status.
    actions = ttk.Frame(frame)
    actions.pack(side="bottom", fill="x")
    image_label = (tk.Canvas(frame, width=460, height=216, background="white")
                   if basic_cut else ttk.Label(frame))
    image_label.pack(pady=8)
    preview = None
    request = None
    busy = False
    closed = False
    close_requested = False
    published_target = None

    def open_folder():
        if close_requested or busy or published_target is None or not current():
            status.set("Dossier indisponible : réexaminer le projet ou republier.")
            return
        try:
            if basic_cut:
                target = Path(published_target)
                opener = getattr(os, "startfile", None)
                if not target.is_file() or opener is None:
                    status.set("Ouverture du dossier indisponible sur ce système.")
                    return
                opener(str(target.parent))
            elif not open_export_folder(published_target):
                status.set("Ouverture du dossier indisponible sur ce système.")
        except OSError:
            status.set("Impossible d’ouvrir le dossier : utiliser le chemin affiché.")

    def invalidate_preview(*_args):
        nonlocal preview, request, published_target
        preview = request = None
        published_target = None
        if basic_cut:
            image_label.delete("all")
        export_button.configure(state="disabled")
        folder_button.configure(state="disabled")
        # A modal callback can modify the width while an inspection or a
        # publication is running. Never let its stale completion re-enable
        # export for a different physical size.
        if not busy and not closed:
            status.set("Largeur modifiée : examiner à nouveau avant toute publication.")

    def current():
        return (not closed and not panel._closed and not panel.busy
                and not panel.history_requires_review and not panel.has_open_brush
                and (panel._project_path, getattr(panel.snapshot, "sha256", None),
                     panel.selection.get()) == original
                and panel.subjects.get(original[2]) is subject)

    def close():
        nonlocal closed, close_requested
        if busy:
            close_requested = True
            status.set("Fermeture demandée : terminer la fenêtre en cours sans publier.")
            return
        closed = True
        dialog.destroy()

    def inspect():
        nonlocal preview, request, busy, published_target
        if busy or closed or close_requested:
            return
        preview = request = None
        published_target = None
        folder_button.configure(state="disabled")
        if basic_cut:
            image_label.delete("all")
        export_button.configure(state="disabled")
        if not current():
            status.set("Sélection ou révision modifiée : réexaminer (F5).")
            return
        req, issue = preview_identity(panel.snapshot, subject, path, width.get())
        if issue:
            status.set(issue)
            return
        busy = True
        try:
            if basic_cut:
                cut = inspect_native_basic_cut_subject(**req)
                if (cut.project_sha256 != req["expected_sha256"] or
                        cut.subject_id != req["subject_id"] or cut.width_mm != req["width_mm"]):
                    raise ValueError("STALE_CUT_PREVIEW")
                result = dict(status=cut.status, output_sha256=cut.svg_sha256,
                              width_mm=cut.width_mm, height_mm=cut.height_mm,
                              readback_limit=len(cut.svg), low_resolution_warning=False)
            else:
                result = inspect_native_ptc_png(**req)
            if (close_requested or not current() or
                    ptc_preview_request(panel.snapshot, subject, path, width.get()) != req or
                    result.get("status") != ("BASIC_CUT_PREVIEW_READY" if basic_cut else "PTC_PREVIEW_READY")):
                status.set("Aperçu périmé : recommencer.")
                return
            if basic_cut:
                _draw_cut_preview(image_label, cut)
            else:
                raw = result["preview_png_rgba"]
                image = tk.PhotoImage(master=dialog, data=base64.b64encode(raw), format="png")
                image_label.configure(image=image)
                image_label.image = image
            request, preview = req, result
            status.set("Sujet " + original[2] + " · SHA projet " + original[1][:12]
                       + " · " + kind + " " + result["output_sha256"][:12]
                       + " · " + str(result["width_mm"]) + " × "
                       + str(result["height_mm"]) + " mm"
                       + (" · résolution faible" if result["low_resolution_warning"] else ""))
            export_button.configure(state="normal")
        except (NativePTCError, ValueError, OSError, tk.TclError, ET.ParseError, KeyError, TypeError) as exc:
            if not closed:
                status.set(_ERRORS.get(getattr(exc, "code", str(exc) if isinstance(exc, BasicCutError) else ""), "Aperçu impossible : réexaminer (F5)."))
        finally:
            busy = False
            if close_requested:
                close()

    def export():
        nonlocal busy, published_target
        if busy or closed or close_requested:
            return
        if preview is None or request is None or not current():
            status.set("Aperçu périmé : recommencer.")
            return
        if ptc_preview_request(panel.snapshot, subject, path, width.get()) != request:
            status.set("Largeur modifiée : refaire l'aperçu.")
            return
        # File dialogs and confirmations run nested Tk event loops. A queued
        # WM_DELETE_WINDOW must not destroy the parent while either is active.
        busy = True
        target = None
        dialog_failed = False
        try:
            target = filedialog.asksaveasfilename(parent=dialog, title="Destination " + kind,
                                                   defaultextension=suffix,
                                                   filetypes=[(label, "*" + suffix)])
        except (OSError, tk.TclError):
            status.set("Sélecteur de fichier indisponible : aucun fichier publié. Réessayer.")
            dialog_failed = True
        finally:
            busy = False
        if close_requested:
            close()
            return
        if dialog_failed or closed or not target:
            return
        if not current() or Path(target).suffix.lower() != suffix:
            status.set("Destination ou sélection invalide.")
            return
        if Path(target).exists():
            status.set("Ce fichier existe déjà : choisir un autre nom, sans écrasement.")
            return
        destination.set(target)
        busy = True
        confirmed = False
        dialog_failed = False
        try:
            confirmed = messagebox.askyesno(
                "Confirmer l'export", "Publier ce " + kind + " sans écraser de fichier existant ?",
                parent=dialog, default="no")
        except (OSError, tk.TclError):
            status.set("Confirmation indisponible : aucun fichier publié. Réessayer.")
            dialog_failed = True
        finally:
            busy = False
        if close_requested:
            close()
            return
        if dialog_failed or closed or not confirmed:
            return
        if (not current() or preview is None or request is None or
                ptc_preview_request(panel.snapshot, subject, path, width.get()) != request):
            if not closed:
                status.set("Révision ou largeur modifiée : refaire l'aperçu.")
            return
        if Path(target).exists():
            status.set("Le fichier vient d’apparaître : choisir une autre destination.")
            return
        # Pin the inspected digest before entering the publisher. Queued Tk
        # width-change callbacks may invalidate `preview` while it runs.
        expected_digest = preview["output_sha256"]
        readback_limit = preview["readback_limit"] if basic_cut else _MAX_PNG_READBACK
        publish_request = request
        busy = True
        published_target = None
        folder_button.configure(state="disabled")
        export_button.configure(state="disabled")
        try:
            if basic_cut:
                receipt = publish_native_basic_cut_svg(**publish_request, destination_path=target,
                           expected_svg_sha256=expected_digest, confirmed=True)
            else:
                receipt = publish_native_ptc_png(**publish_request, destination_path=target,
                           expected_output_sha256=expected_digest, confirmed=True)
            if receipt.get("persisted") is not True:
                status.set("Résultat incertain : vérifier le fichier avant tout nouvel essai.")
            else:
                digest = _readback_digest(target, readback_limit)
                if digest != expected_digest:
                    status.set("Relecture différente : vérifier le fichier, ne pas réessayer.")
                elif (receipt.get("project_revision_still_current") is not True or
                      receipt.get("status") == ("LOCAL_SVG_REVISION_CHANGED" if basic_cut else "LOCAL_PNG_REVISION_CHANGED")):
                    # The publisher owns the authoritative project-revision CAS.
                    # A persisted PNG can still be stale even if the Tk panel
                    # has not observed the external concurrent modification.
                    status.set(kind + " enregistré et relu, mais révision du projet modifiée "
                               "ou non confirmée : vérifier le fichier manuellement, "
                               "puis réexaminer (F5). Aucun nouvel export automatique.")
                elif (not current() or
                      ptc_preview_request(panel.snapshot, subject, path, width.get()) != publish_request):
                    # A queued Tk callback can change selection/revision/width
                    # during the synchronous publisher. The file is already
                    # committed: report it without authorizing stale actions.
                    status.set(kind + " enregistré et relu, mais sélection ou largeur modifiée : "
                               "vérifier le fichier manuellement, puis réexaminer (F5).")
                else:
                    published_target = target
                    folder_button.configure(state="normal")
                    status.set(kind + " enregistré et relu · SHA " + digest[:12]
                               + " · dossier : " + str(Path(target).parent))
        except (NativePTCError, BasicCutError, OSError) as exc:
            status.set(_ERRORS.get(getattr(exc, "code", str(exc) if isinstance(exc, BasicCutError) else ""),
                                   "Export incertain : vérifier le fichier avant de réessayer."))
        finally:
            busy = False
            if close_requested:
                close()

    ttk.Button(actions, text="Examiner", command=inspect).pack(side="left")
    export_button = ttk.Button(actions, text="Choisir et publier…", command=export, state="disabled")
    export_button.pack(side="left", padx=6)
    folder_button = ttk.Button(actions, text="Ouvrir le dossier", command=open_folder, state="disabled")
    folder_button.pack(side="left", padx=6)
    width.trace_add("write", invalidate_preview)
    ttk.Button(actions, text="Fermer", command=close).pack(side="left")
    dialog.protocol("WM_DELETE_WINDOW", close)
    return True
