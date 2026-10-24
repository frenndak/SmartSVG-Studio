"""G1.4: safe, explicit recovery of previously valid .smartsvg projects.

This is a framework-independent backend. It never silently replaces a corrupt
project, and it does not imply that saved SVG/PNG files are cut-certified.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from hashlib import sha256
import os
from pathlib import Path
import shutil
import tempfile

from .project_archive import LoadedProject, ProjectArchiveError, load_project, save_project


class RecoveryError(ValueError):
    """Stable code for a user-actionable project recovery failure."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


MESSAGES_FR = {
    'PROJECT_MISSING': (
        'Aucun projet sauvegardé trouvé.',
        'Créer un projet ou sélectionner un autre fichier .smartsvg.'),
    'PROJECT_HEALTHY': (
        'Le projet est lisible et ses ressources sont cohérentes.',
        'Continuer dans le projet.'),
    'PROJECT_RECOVERABLE': (
        'Le projet principal est absent ou endommagé, mais une sauvegarde précédente valide existe.',
        'Prévisualiser cette sauvegarde puis confirmer explicitement sa restauration.'),
    'PROJECT_UNRECOVERABLE': (
        'Le projet et sa sauvegarde précédente ne sont pas tous deux récupérables.',
        'Conserver les fichiers pour diagnostic ; aucune réparation automatique ne sera tentée.'),
    'PROJECT_LOCKED': (
        'Une autre opération de sauvegarde ou de restauration est en cours.',
        'Terminer l’autre opération et réessayer.'),
    'RECOVERY_CONFIRMATION_REQUIRED': (
        'La restauration modifierait le fichier principal.',
        'Confirmer la restauration après vérification du projet de secours.'),
    'RECOVERY_WOULD_OVERWRITE_VALID_PROJECT': (
        'Le projet principal est valide ; aucune restauration ne doit le remplacer automatiquement.',
        'Créer une copie manuelle avant toute opération de retour arrière.'),
    'NO_VALID_RECOVERY_SNAPSHOT': (
        'Aucune sauvegarde précédente valide n’est disponible.',
        'Conserver les fichiers existants et consulter le rapport de diagnostic.'),
    'INVALID_RECOVERY_PATH': (
        'Emplacement de projet non valide.',
        'Choisir un fichier .smartsvg dans un dossier existant.'),
    'PROJECT_CHANGED_DURING_SAVE': (
        'Le projet a été modifié pendant la sauvegarde.',
        'Conserver les versions existantes et relancer la sauvegarde.'),
    'BACKUP_CONFLICT': (
        'Une copie de secours existe déjà mais elle est endommagée ou appartient à un autre projet.',
        'Préserver ce fichier et choisir un nouvel emplacement après vérification.'),
    'SAVE_FAILED': (
        'La sauvegarde n’a pas pu être terminée.',
        'Vérifier l’espace disponible, les droits du dossier et le fichier de secours.'),
}


@dataclass(frozen=True)
class RecoveryReport:
    status: str
    primary: str
    previous: str
    message_fr: str
    action_fr: str
    project_id: str | None
    automatic_restore: bool = False
    physical_cut_verified: bool = False


def _location(path) -> Path:
    target = Path(path)
    if target.suffix.lower() != '.smartsvg' or not target.parent.is_dir():
        raise RecoveryError('INVALID_RECOVERY_PATH')
    return target


def _previous(target: Path) -> Path:
    return target.with_name(target.stem + '.previous.smartsvg')


def _lock_file(target: Path) -> Path:
    return target.with_name(target.name + '.lock')


def _diagnose(path: Path):
    if path.is_symlink():
        return 'invalid', None
    if not path.exists():
        return 'missing', None
    try:
        data = load_project(path)
        return 'valid', data
    except (ProjectArchiveError, OSError):
        return 'invalid', None


def inspect_project(path) -> RecoveryReport:
    """Read-only inspection; does not remove locks or repair a file."""
    target = _location(path)
    primary, main = _diagnose(target)
    previous, recovered = _diagnose(_previous(target))
    if primary == 'valid':
        status = 'PROJECT_HEALTHY'
    elif previous == 'valid':
        status = 'PROJECT_RECOVERABLE'
    elif primary == previous == 'missing':
        status = 'PROJECT_MISSING'
    else:
        status = 'PROJECT_UNRECOVERABLE'
    message, action = MESSAGES_FR[status]
    return RecoveryReport(
        status=status, primary=primary, previous=previous,
        message_fr=message, action_fr=action,
        project_id=(main or recovered).project_id if (main or recovered) else None,
    )


@contextmanager
def _project_lock(target: Path):
    """OS advisory lock. Kernel releases it after process death (no stale PID)."""
    lock_path = _lock_file(target)
    if lock_path.is_symlink():
        raise RecoveryError('PROJECT_LOCKED')
    try:
        # A persistent *empty* sidecar is fine: lock ownership is held by the OS.
        with open(lock_path, 'a+b') as handle:
            if os.name == 'nt':
                import msvcrt
                if lock_path.stat().st_size == 0:
                    handle.write(b'0')
                    handle.flush()
                handle.seek(0)
                try:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                except OSError as exc:
                    raise RecoveryError('PROJECT_LOCKED') from exc
            else:
                import fcntl
                try:
                    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError as exc:
                    raise RecoveryError('PROJECT_LOCKED') from exc
            try:
                yield
            finally:
                if os.name == 'nt':
                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(handle, fcntl.LOCK_UN)
    except RecoveryError:
        raise
    except OSError as exc:
        raise RecoveryError('SAVE_FAILED') from exc


def _file_sha(path: Path) -> str:
    digest = sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _atomic_copy(source: Path, destination: Path) -> None:
    """Copy into a sibling temp, revalidate ZIP and only then publish."""
    if source.is_symlink() or destination.is_symlink():
        raise RecoveryError('SAVE_FAILED')
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix='.smartsvg-recover-', suffix='.tmp',
            dir=destination.parent, delete=False,
        ) as handle:
            tmp = Path(handle.name)
            with source.open('rb') as origin:
                shutil.copyfileobj(origin, handle, 1024 * 1024)
            handle.flush()
            os.fsync(handle.fileno())
        load_project(tmp)
        if _file_sha(source) != _file_sha(tmp):
            raise RecoveryError('PROJECT_CHANGED_DURING_SAVE')
        if destination.is_symlink():
            raise RecoveryError('SAVE_FAILED')
        os.replace(tmp, destination)
        tmp = None
        try:
            fd = os.open(destination.parent, os.O_RDONLY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
        except OSError:
            pass  # best effort on Windows/unsupported FS
    except (OSError, ProjectArchiveError) as exc:
        raise RecoveryError('SAVE_FAILED') from exc
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)


def save_with_recovery(path, project: LoadedProject, *, expected_sha256=None) -> dict:
    """Preserve last valid primary before overwrite; no destructive fallback.

    Calling G1.3 save_project (rather than silently overwriting backup files)
    keeps its validation, readback and atomic replace semantics.
    """
    target = _location(path)
    with _project_lock(target):
        primary, current = _diagnose(target)
        if primary == 'invalid':
            raise RecoveryError('NO_VALID_RECOVERY_SNAPSHOT')
        if expected_sha256 is not None:
            if primary != 'valid' or _file_sha(target) != expected_sha256:
                raise RecoveryError('PROJECT_CHANGED_DURING_SAVE')
        if primary == 'valid':
            if current.project_id != project.project_id:
                raise RecoveryError('PROJECT_CHANGED_DURING_SAVE')
            backup_state, backup_project = _diagnose(_previous(target))
            if backup_state == 'invalid' or (
                backup_state == 'valid' and
                backup_project.project_id != current.project_id
            ):
                # Never destroy a foreign or potentially salvageable old backup.
                raise RecoveryError('BACKUP_CONFLICT')
            # Preserves the last-known-good primary even if new save fails.
            _atomic_copy(target, _previous(target))
        try:
            saved = save_project(target, project, overwrite=(primary == 'valid'))
            # Verify actual published file, not only in-memory bytes.
            verified = load_project(target)
            if verified.project_id != project.project_id:
                raise RecoveryError('PROJECT_CHANGED_DURING_SAVE')
        except ProjectArchiveError as exc:
            raise RecoveryError('SAVE_FAILED') from exc
        return {**saved, 'previous_available': primary == 'valid',
                'physical_cut_verified': False}


def recover_previous(path, *, confirmed: bool = False) -> dict:
    """Explicitly restore backup only when primary is missing or invalid."""
    target = _location(path)
    if not confirmed:
        raise RecoveryError('RECOVERY_CONFIRMATION_REQUIRED')
    with _project_lock(target):
        primary, _ = _diagnose(target)
        previous_path = _previous(target)
        previous, snapshot = _diagnose(previous_path)
        if primary == 'valid':
            raise RecoveryError('RECOVERY_WOULD_OVERWRITE_VALID_PROJECT')
        if previous != 'valid':
            raise RecoveryError('NO_VALID_RECOVERY_SNAPSHOT')
        if target.is_symlink():
            raise RecoveryError('SAVE_FAILED')
        _atomic_copy(previous_path, target)
        restored = load_project(target)
        if restored.project_id != snapshot.project_id:
            raise RecoveryError('PROJECT_CHANGED_DURING_SAVE')
        return {'status': 'restored_from_previous', 'project_id': restored.project_id,
                'previous_retained': True, 'physical_cut_verified': False}


def recovery_message(code: str) -> dict[str, str]:
    """Stable text/next-action mapping for future Express error panel."""
    if code not in MESSAGES_FR:
        code = 'SAVE_FAILED'
    message, action = MESSAGES_FR[code]
    return {'code': code, 'message_fr': message, 'action_fr': action}
