"""R15 read-only PR path inventory. Not a semantic or complete-diff verdict."""
from dataclasses import asdict, dataclass
from hashlib import sha256
import json

from .smartsvg_controller_observation import ObservationError, _sha, branch_observation
from .smartsvg_controller_preflight import _valid_path

REPO = "frenndak/SmartSVG-Studio"
MAX_FILES = 3000
STATUSES = frozenset(("added", "modified", "removed", "renamed", "copied", "changed"))


@dataclass(frozen=True)
class FileObservation:
    filename: str
    previous_filename: str | None
    status: str
    blob: str
    patch_digest: str | None


@dataclass(frozen=True)
class ScopeObservation:
    number: int
    head: str
    main: str
    base: str
    files: tuple
    paths: tuple
    excluded_paths: tuple
    engine_changed: bool
    base_matches_main: bool
    inventory_digest: str
    qualification: str = "PATHS_ONLY"


def _identity(pr, number, head):
    if (pr.get("number") != number or pr.get("state") != "open"
            or pr.get("head", {}).get("sha") != head
            or (pr.get("head", {}).get("repo") or {}).get("full_name") != REPO
            or (pr.get("base", {}).get("repo") or {}).get("full_name") != REPO
            or pr.get("base", {}).get("ref") != "main"
            or pr.get("user", {}).get("login") != "frenndak"):
        raise ObservationError("unexpected PR identity")
    count = pr.get("changed_files")
    if type(count) is not int or not 1 <= count <= MAX_FILES:
        raise ObservationError("unknown or unsupported file count")
    return (_sha(pr["base"]["sha"]), pr["head"]["ref"], count)


def _file(row):
    name, previous = row.get("filename"), row.get("previous_filename")
    status = row.get("status")
    if (not isinstance(name, str) or not name
            or status not in STATUSES
            or (status in ("renamed", "copied") and
                (not isinstance(previous, str) or not previous or previous == name))
            or (status not in ("renamed", "copied") and previous is not None)):
        raise ObservationError("invalid file metadata")
    patch = row.get("patch")
    if patch is not None and not isinstance(patch, str):
        raise ObservationError("invalid patch metadata")
    # GitHub may omit or truncate patch text. Never infer complete diff.
    return FileObservation(name, previous, status, _sha(row.get("sha")),
                           sha256(patch.encode()).hexdigest() if patch is not None else None)


def inspect_scope(get, number, *, head, main):
    """Collect count-checked file metadata and re-read mutable identities.

    The PR files endpoint has a 3000-file ceiling; it is not a complete
    content or semantic review. A stale base is reported, never silently
    treated as current main. Both sides of a rename/copy are inspected.
    """
    if type(number) is not int or number < 1:
        raise ObservationError("invalid PR number")
    _sha(head)
    _sha(main)
    if get("/branches/main")["commit"]["sha"] != main:
        raise ObservationError("main changed")
    path = "/pulls/" + str(number)
    pr = get(path)
    identity = _identity(pr, number, head)
    base, _, count = identity
    if branch_observation(get, pr)["status"] != "MATCH":
        raise ObservationError("branch divergence")
    rows, seen = [], set()
    for page in range(1, 31):
        batch = get(f"{path}/files?per_page=100&page={page}")
        if not isinstance(batch, list) or len(batch) > 100:
            raise ObservationError("invalid file page")
        for row in batch:
            item = _file(row)
            if item.filename in seen:
                raise ObservationError("duplicate file")
            seen.add(item.filename)
            rows.append(item)
        if len(rows) > count:
            raise ObservationError("file count drift")
        if len(batch) < 100 or len(rows) == count:
            break
    if len(rows) != count:
        raise ObservationError("incomplete file inventory")
    # Re-read both PR projection and real ref before returning.
    latest = get(path)
    if (_identity(latest, number, head) != identity
            or branch_observation(get, latest)["status"] != "MATCH"
            or get("/branches/main")["commit"]["sha"] != main):
        raise ObservationError("scope observation drift")
    files = tuple(sorted(rows, key=lambda r:r.filename))
    paths = tuple(sorted({p for r in files for p in (r.filename,r.previous_filename)
                          if p is not None}))
    excluded = tuple(p for p in paths if not _valid_path(p))
    material = [number,head,main,base,[asdict(r) for r in files]]
    digest = sha256(json.dumps(material,sort_keys=True,separators=(",",":"),
                              ensure_ascii=True).encode()).hexdigest()
    return ScopeObservation(number,head,main,base,files,paths,excluded,
                            any(p.startswith("engine/") for p in paths),
                            base == main,digest)
