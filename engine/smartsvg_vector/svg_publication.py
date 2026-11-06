"""Publish the existing editable SVG export only after a complete synced write.

This is the historical save_svg writer extracted from the raster-dependent
module. It publishes opaque generated XML bytes; it is not an SVG preflight,
export contract router, project writer or physical-cut qualification.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import tempfile


def save_svg(svg, folder='', prefix='smartsvg_couleurs'):
    if not isinstance(svg, bytes) or not svg.startswith(b'<?xml'):
        raise ValueError('SVG XML attendu')
    if not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}', prefix):
        raise ValueError('Nom SVG non sûr')
    if folder:
        path = Path(folder).expanduser()
        if not path.is_absolute():
            raise ValueError('Un dossier de sortie absolu est requis')
        if path.exists() and (path.is_symlink() or not path.is_dir()):
            raise ValueError('Dossier non sûr')
        path.mkdir(parents=True, exist_ok=True)
    else:
        try:
            import folder_paths
            path = Path(folder_paths.get_output_directory())/'SmartSVG_Studio'/'SVG_Multicouche'
            path.mkdir(parents=True, exist_ok=True)
        except ImportError:
            path = Path(tempfile.mkdtemp(prefix='smartsvg_multicouche_'))

    descriptor, name = tempfile.mkstemp(prefix='.smartsvg_svg_', suffix='.tmp', dir=path)
    staging = Path(name)
    try:
        output = os.fdopen(descriptor, 'wb')
        descriptor = None  # ownership transferred to the file object
        with output:
            output.write(svg)
            output.flush()
            os.fsync(output.fileno())
        digest = hashlib.sha256()
        with staging.open('rb') as source:
            for chunk in iter(lambda: source.read(1024*1024), b''):
                digest.update(chunk)
        if digest.digest() != hashlib.sha256(svg).digest():
            raise ValueError('Copie SVG incoherente ; aucun fichier publie')

        for ix in range(1, 1000):
            dest = path/f'{prefix}_{ix:03d}.svg'
            try:
                os.link(staging, dest)
            except FileExistsError:
                continue
            except OSError as exc:
                # POSIX rename replaces an existing target. Windows rename
                # refuses one and can publish complete staging without links.
                if os.name != 'nt':
                    raise ValueError('Publication atomique impossible sans liens physiques') from exc
                try:
                    os.rename(staging, dest)
                except FileExistsError:
                    continue
                except OSError as rename_exc:
                    raise ValueError('Publication atomique impossible sur ce systeme de fichiers') from rename_exc
            return str(dest)
        raise ValueError('Trop de versions dans le dossier de sortie')
    finally:
        if descriptor is not None:
            os.close(descriptor)
        staging.unlink(missing_ok=True)
