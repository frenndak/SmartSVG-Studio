"""Hash current file content as Git would store it, including checkout EOL rules.

No HEAD shortcut: an unstaged content edit must change the computed blob.
Standalone non-Git snapshots retain exact raw-byte checks.
"""
from hashlib import sha1
from pathlib import Path
import re
import subprocess


def file_blob(path):
    path = Path(path).resolve(strict=True)
    raw = path.read_bytes()
    try:
        root = subprocess.run(
            ["git", "-C", str(path.parent), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=10,
        )
    except FileNotFoundError:
        root = None
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("Cannot inspect Git provenance") from exc
    if root is None or root.returncode != 0:
        return sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    try:
        repo = Path(root.stdout.strip()).resolve(strict=True)
        relative = path.relative_to(repo).as_posix()
        result = subprocess.run(
            ["git", "-C", str(repo), "hash-object", "--path=" + relative, str(path)],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        raise ValueError("Cannot hash current Git file content") from exc
    digest = result.stdout.strip()
    if result.returncode or re.fullmatch(r"[0-9a-f]{40}", digest) is None:
        raise ValueError("Git content hash failed")
    return digest
