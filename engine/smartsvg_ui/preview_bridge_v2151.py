"""Optional ComfyUI output preview bridge, no custom HTTP endpoints.

Only reads existing QA PNG files inside a production root returned by the
current run. Writes *small* opaque preview PNGs to ComfyUI's managed output
folder so the official /view endpoint can display them. No arbitrary paths.
"""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import re
import uuid
import time

MAX_OWNED_PREVIEWS = 96
MAX_PREVIEW_AGE_SECONDS = 72 * 3600
from PIL import Image

MAX_INPUT_BYTES = 12_000_000
MAX_PREVIEW_PIXELS = 20_000_000
MAX_CARDS = 6


def _under(project, candidate):
    p=Path(candidate)
    if p.is_symlink():
        return None
    try:
        rp = p.resolve(strict=True)
        if not rp.is_relative_to(project.resolve(strict=True)) or not rp.is_file():
            return None
        return rp
    except (OSError,ValueError):
        return None


def preview_sources(report):
    """Accept only QA-generated file names, not user-supplied arbitrary paths."""
    if not isinstance(report,dict) or not isinstance(report.get('dossier'),str):
        return []
    root=Path(report['dossier'])
    if not root.is_dir() or root.is_symlink():
        return []
    qa=root/'05_CONTROLE_V21_2'
    if qa.is_symlink() or not qa.is_dir():
        return []
    names=['APERÇU_GLOBAL.png']+[f'OBJET_{i:02d}_AVANT_APRES.png' for i in range(1,MAX_CARDS+1)]
    sources=[]
    for name in names:
        f=_under(root,qa/name)
        if f is not None and f.stat().st_size<=MAX_INPUT_BYTES:
            sources.append((name, f))
    return sources


def publish_previews(report, output_directory, *, max_side=840):
    """Return official ComfyUI /view metadata or [] if unavailable.

    Copies are derived solely from the current report and fixed QA names,
    always use a small opaque image; no metadata, raw secrets or svg.
    """
    if not output_directory:
        return []
    if Path(output_directory).is_symlink():
        return []
    try:
        root=Path(output_directory).resolve()
        root.mkdir(parents=True,exist_ok=True)
        if not root.is_dir():return []
    except OSError:
        return []
    try:
        output=root/'SmartSVG_Studio_Previews'
        output.mkdir(parents=True,exist_ok=True)
    except OSError:
        return []
    if output.is_symlink():
        return []
    # Bounded retention: only clean up our own preview files, never a user file.
    # Large datasets can generate 7 tiny previews per processing session.
    try:
        old=sorted((x for x in output.iterdir()
                    if x.is_file() and not x.is_symlink()
                    and re.fullmatch(r'qa_[a-z0-9_]{2,35}\.png',x.name)),
                   key=lambda x: x.stat().st_mtime, reverse=True)
        # Hard storage cap: do not let frequent processing accumulate an
        # unbounded number of private preview duplicates in output/. Protect
        # recent previews while removing the oldest ones first.
        now=time.time()
        for i,stale in enumerate(old):
            if i>=MAX_OWNED_PREVIEWS or now-stale.stat().st_mtime>MAX_PREVIEW_AGE_SECONDS:
                stale.unlink(missing_ok=True)
    except OSError:
        pass  # non-essential cleanup
    # max_side is an internal parameter, not a user-facing setting. Bound it
    # anyway to avoid extremely large UI preview allocations.
    max_side=max(96,min(int(max_side),840))
    refs=[]
    for name,path in preview_sources(report):
        try:
            with Image.open(path) as opened:
                w,h=opened.size
                if not (0<w*h<=MAX_PREVIEW_PIXELS):
                    continue
                # Never copy the full source or user metadata, only a resized QA preview.
                preview=opened.convert('RGB')
            preview.thumbnail((max_side,max_side),Image.Resampling.LANCZOS)
            prefix='global' if name.startswith('APER') else name[0:8].lower()
            filename=f'qa_{prefix}_{uuid.uuid4().hex[:14]}.png'
            dest=output/filename
            preview.save(dest,format='PNG',optimize=True)
            refs.append({'filename':filename,'subfolder':'SmartSVG_Studio_Previews','type':'output'})
        except (OSError,ValueError,Image.DecompressionBombError):
            continue
    # Include newly created thumbnails in the cap as well. A run may add up
    # to seven files; keep each filename reported by this run accessible.
    try:
        current=set(x['filename'] for x in refs)
        owned=sorted((x for x in output.iterdir()
                      if x.is_file() and not x.is_symlink()
                      and re.fullmatch(r'qa_[a-z0-9_]{2,35}\.png',x.name)),
                     key=lambda x:x.stat().st_mtime,reverse=True)
        kept=0
        for stale in owned:
            if stale.name in current:
                kept+=1
            elif kept<MAX_OWNED_PREVIEWS:
                kept+=1
            else:
                stale.unlink(missing_ok=True)
    except OSError:
        pass
    return refs
