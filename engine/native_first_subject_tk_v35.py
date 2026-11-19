"""W02 native Tk handoff: guarded preview, explicit consent and one V1 write.

All disk/PNG work stays in a worker; Tk callbacks run on its owner thread.
A lost write receipt is *uncertain*, never a reason to retry automatically.
"""
from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event
import re
import struct

from smartsvg_core.native_first_subject_v35 import (
    MAX_MASK_PREVIEW_AXIS,
    NativeFirstSubjectError, inspect_first_alpha_subject,
    confirm_first_alpha_subject,
)

_SHA = re.compile(r"^[0-9a-f]{64}$")
_SUBJECT = re.compile(r"^subject-[0-9a-f]{32}$")
_MESSAGES = {
    "MANUAL_SELECTION_REQUIRED": (
        "Le PNG n’a pas de sujet transparent exploitable. "
        "Une sélection manuelle sera nécessaire ; aucun fichier modifié."),
    "MASK_SNAPSHOT_TOO_LARGE": (
        "Image trop grande pour ce premier masque (5 millions de pixels maximum)."),
    "SUBJECT_ALREADY_PRESENT": "Un sujet existe déjà. Réexaminer le projet (F5).",
    "EXISTING_MASK_REQUIRES_REVIEW": (
        "Un autre masque est déjà présent. Réexaminer avant toute modification."),
    "PROJECT_CHANGED": "Le projet a changé. Réexaminer (F5), sans réessai automatique.",
    "PROJECT_REQUIRES_REVIEW": "Projet non vérifié. Réexaminer (F5).",
}


def show_first_subject_confirmation(root, tk, ttk, proposal):
    """Show the exact candidate's bounded mask before explicit confirmation."""
    raw = proposal.get("mask_preview_png_l8")
    if (type(raw) is not bytes or not 33 <= len(raw) <= 96 * 1024 or
            raw[:16] != b"\x89PNG\r\n\x1a\n\x00\x00\x00\x0dIHDR"):
        raise ValueError("invalid candidate preview")
    width, height = struct.unpack_from(">II", raw, 16)
    if (not 0 < width <= MAX_MASK_PREVIEW_AXIS or
            not 0 < height <= MAX_MASK_PREVIEW_AXIS or
            raw[24:29] != b"\x08\x00\x00\x00\x00"):
        raise ValueError("invalid candidate preview bounds")
    image = tk.PhotoImage(master=root, data=base64.b64encode(raw), format="png")
    if (image.width(), image.height()) != (width, height):
        raise ValueError("candidate preview size mismatch")
    scale = max(1, 160 // max(width, height))
    if scale > 1:
        image = image.zoom(scale)

    window = tk.Toplevel(root)
    accepted = False

    def finish(value=False):
        nonlocal accepted
        accepted = value
        window.destroy()

    try:
        window.title("Vérifier le masque du premier sujet")
        window.transient(root)
        window.protocol("WM_DELETE_WINDOW", finish)
        window.bind("<Escape>", lambda _event: finish())
        content = ttk.Frame(window, padding=16)
        content.pack(fill="both", expand=True)
        source_width, source_height = proposal["dimensions_px"]
        ttk.Label(content, text=f"Image {source_width} × {source_height} px").pack(anchor="w")
        ttk.Label(content, image=image).pack(pady=8)
        ttk.Label(content, wraplength=330, justify="left", text=(
            "Blanc : conservé. Noir : transparent. Gris : partiellement transparent. "
            "L’aperçu est adapté à la fenêtre.")).pack(anchor="w")
        actions = ttk.Frame(content)
        actions.pack(fill="x", pady=(12, 0))
        cancel = ttk.Button(actions, text="Annuler", command=finish)
        cancel.pack(side="left", padx=(0, 8))
        label = ("Rattacher le masque" if proposal["status"] == "RESUME_MASK_BINDING"
                 else "Créer le sujet")
        ttk.Button(actions, text=label, command=lambda: finish(True)).pack(side="left")
        window.wait_visibility()
        window.grab_set()
        cancel.focus_set()
        window.wait_window()
    finally:
        if window.winfo_exists():
            window.destroy()
    return accepted


class NativeFirstSubjectFlow:
    """One pending preview or confirmed write; caller supplies current UI guards.

    guard(path, revision) must reject stale selection, active writes, open
    brush and unverified project. checkpoint() includes the local notes draft
    so a modal reentrant edit cannot authorize an old confirmation.
    """

    def __init__(self, root, *, guard, checkpoint, on_saved, confirm_preview,
                 on_status, inspect_fn=inspect_first_alpha_subject,
                 confirm_fn=confirm_first_alpha_subject,
                 executor_factory=ThreadPoolExecutor):
        self.root = root
        self._guard, self._checkpoint = guard, checkpoint
        self._on_saved, self._on_status = on_saved, on_status
        self._confirm_preview = confirm_preview
        self._inspect, self._confirm = inspect_fn, confirm_fn
        self._pool_factory = executor_factory
        self._pool = None
        self._future = None
        self._closed = self._busy = False
        self._unreconciled_paths = set()
        self._generation = 0
        self._target = self._original_checkpoint = None

    @property
    def busy(self):
        return self._busy

    @property
    def requires_review(self):
        return self._target is not None and self.requires_review_for(self._target[0])

    def requires_review_for(self, project_path):
        return project_path in self._unreconciled_paths

    def _status(self, message):
        if not self._closed:
            self._on_status(message)

    def _context_valid(self):
        if self._closed or self._target is None:
            return False
        try:
            return self._guard(*self._target) is True
        except Exception:
            return False

    def start(self, *, project_path, expected_sha256):
        if (self._closed or self._busy or
                type(project_path) is not str or
                not Path(project_path).is_absolute() or
                self.requires_review_for(project_path) or
                type(expected_sha256) is not str or
                not _SHA.fullmatch(expected_sha256)):
            return False
        self._target = (project_path, expected_sha256)
        if not self._context_valid():
            return False
        try:
            self._original_checkpoint = self._checkpoint()
        except Exception:
            return False
        self._busy = True
        self._status("Analyse du PNG transparent en lecture seule…")
        return self._submit("inspect", dict(
            project_path=project_path, expected_sha256=expected_sha256))

    def _submit(self, phase, request):
        # Keep a queued task inert until both submit and Tk's completion poll
        # succeed. A failed launch cannot orphan a writer.
        launch = Event()
        authorized = False
        fn = self._inspect if phase == "inspect" else self._confirm

        def guarded():
            launch.wait()
            if not authorized:
                return None
            return fn(**request)

        try:
            if self._pool is None:
                self._pool = self._pool_factory(
                    max_workers=1, thread_name_prefix="smartsvg-first-subject")
            future = self._pool.submit(guarded)
            self._future = future
            self._generation += 1
            generation = self._generation
            self.root.after(50, lambda: self._receive(phase, generation, future))
            authorized = True
        except Exception:
            launch.set()
            pool, self._pool = self._pool, None
            if pool is not None:
                pool.shutdown(wait=False, cancel_futures=True)
            self._future = None
            self._busy = False
            self._status("Opération indisponible. Aucune nouvelle écriture lancée ; vous pouvez réessayer.")
            return False
        finally:
            launch.set()
        return True

    def _receive(self, phase, generation, future):
        if self._closed or not self._busy or generation != self._generation:
            return
        if not future.done():
            self.root.after(50, lambda: self._receive(phase, generation, future))
            return
        try:
            receipt = future.result()
        except Exception as exc:
            self._busy = False
            if phase == "write":
                self._unreconciled_paths.add(self._target[0])
                self._status("Écriture peut-être effectuée : réexaminer (F5) avant toute autre opération.")
            else:
                code = exc.code if isinstance(exc, NativeFirstSubjectError) else ""
                self._status(_MESSAGES.get(
                    code, "Aperçu refusé : vérifier le projet puis réexaminer (F5)."))
            return

        if phase == "inspect":
            self._handle_preview(receipt)
            return

        self._busy = False
        self._unreconciled_paths.add(self._target[0])
        if (type(receipt) is not dict or
                receipt.get("status") != "FIRST_SUBJECT_CREATED" or
                receipt.get("persisted") is not True or
                type(receipt.get("subject_id")) is not str or
                not _SUBJECT.fullmatch(receipt["subject_id"]) or
                type(receipt.get("project_sha256")) is not str or
                not _SHA.fullmatch(receipt["project_sha256"]) or
                not self._context_valid()):
            self._status("Résultat de sauvegarde non vérifiable : réexaminer (F5).")
            return
        try:
            self._on_saved(receipt)
        except Exception:
            self._status("Sujet probablement créé, mais relecture non confirmée : réexaminer (F5).")

    def _handle_preview(self, proposal):
        if (type(proposal) is not dict or
                proposal.get("status") not in
                ("ALPHA_PREVIEW_READY", "RESUME_MASK_BINDING") or
                proposal.get("project_sha256") != self._target[1] or
                type(proposal.get("candidate_sha256")) is not str or
                not _SHA.fullmatch(proposal["candidate_sha256"]) or
                proposal.get("preview_only") is not True or
                proposal.get("persisted") is not False or
                proposal.get("manual_confirmation_required") is not True or
                proposal.get("selection_kind") != "whole_rgba_alpha" or
                proposal.get("cricut_certified") is not False or
                type(proposal.get("dimensions_px")) is not list or
                len(proposal["dimensions_px"]) != 2 or
                any(type(x) is not int or x <= 0 for x in proposal["dimensions_px"]) or
                not self._context_valid()):
            self._busy = False
            self._status("Aperçu incohérent ou sélection changée : aucune modification.")
            return
        try:
            if self._checkpoint() != self._original_checkpoint:
                self._busy = False
                self._status("Notes ou sélection modifiées : aucune sauvegarde lancée.")
                return
            accepted = self._confirm_preview(proposal)
            if (accepted is not True or not self._context_valid() or
                    self._checkpoint() != self._original_checkpoint):
                self._busy = False
                self._status("Création annulée ou contexte modifié : archive inchangée.")
                return
        except Exception:
            self._busy = False
            self._status("Confirmation indisponible : archive inchangée.")
            return
        self._status("Sauvegarde et vérification du sujet en cours…")
        self._submit("write", dict(
            project_path=self._target[0],
            expected_sha256=self._target[1],
            candidate_sha256=proposal["candidate_sha256"], confirmed=True))

    def acknowledge_reinspection(self, project_path, *, healthy):
        """F5 clears an uncertain outcome only after an actual healthy reread."""
        if not self._busy and healthy is True:
            self._unreconciled_paths.discard(project_path)

    def shutdown(self):
        if self._closed:
            return
        self._closed = True
        self._generation += 1
        if self._pool is not None:
            # A confirmed writer cannot be cancelled or discarded on shutdown.
            self._pool.shutdown(wait=True)
            self._pool = None
