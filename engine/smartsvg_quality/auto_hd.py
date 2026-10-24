"""V21.7.1 conservative, automatic post-export PNG HD derivatives.

Never modifies the manufacturing PNG, alpha geometry, SVG, native cutout,
or source image. Work on CPU only; fallback is always the original export.
"""
from __future__ import annotations

import json
import os
import hashlib
from pathlib import Path
from uuid import uuid4

import cv2
import numpy as np
from PIL import Image, ImageFilter

from ..production_v211 import _resample_print

VERSION = '21.7.1'
TARGET_DPI = 600
MAX_SOURCE_PIXELS = 5_000_000
MAX_DERIVATIVE_PIXELS = 6_000_000
MAX_TOTAL_DERIVATIVE_PIXELS = 50_000_000
MAX_ITEMS = 32
FOLDER = '06_HD_AUTOMATIQUE_V21_7_1'


class QualityError(ValueError):
    pass


def _digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _provenance_file(output):
    return output.with_name(output.stem + '.provenance.json')


def _provenance(source, output, original_dpi):
    return {'schema': 1, 'source_sha256': _digest(source),
            'output_sha256': _digest(output), 'source_dpi': original_dpi,
            'target_dpi': TARGET_DPI, 'algorithm': VERSION}


def _reuse_existing(source, output, original_dpi):
    """Fail closed for old derivatives lacking provenance or changed input bytes."""
    meta_file = _provenance_file(output)
    if output.is_symlink() or meta_file.is_symlink():
        raise QualityError('Ancien PNG HD ou preuve symbolique refusé')
    if not output.is_file() or not meta_file.is_file():
        raise QualityError('Fichier HD préexistant sans preuve vérifiable : pas de remplacement')
    if meta_file.stat().st_size > 2048:
        raise QualityError('Preuve HD hors limites')
    try:
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
    except (ValueError, UnicodeError) as error:
        raise QualityError('Preuve HD illisible') from error
    if not isinstance(meta, dict) or set(meta) != {'schema','source_sha256','output_sha256','source_dpi','target_dpi','algorithm'}:
        raise QualityError('Preuve HD incompatible')
    if meta != _provenance(source, output, original_dpi):
        raise QualityError('Source ou PNG HD modifié : ancien fichier conservé sans réutilisation')
    with Image.open(source) as original, Image.open(output) as enhanced:
        width = round(original.width * TARGET_DPI / original_dpi)
        height = round(original.height * TARGET_DPI / original_dpi)
        if enhanced.format != 'PNG' or enhanced.mode != 'RGBA' or enhanced.size != (width,height):
            raise QualityError('Dimensions ou format du PNG HD modifiés')
        value = float((enhanced.info.get('dpi') or (0,))[0])
        if not 595 <= value <= 605:
            raise QualityError('Densité du PNG HD modifiée')
    return {'fichier_hd': str(output), 'dimensions_px': [width, height],
            'densite_cible_ppp': TARGET_DPI, 'methode': 'réutilisation vérifiée (SHA-256)',
            'alpha_original_non_modifie': True, 'svg_original_non_modifie': True}


def _save_provenance(source, output, original_dpi):
    meta_file = _provenance_file(output)
    if meta_file.is_symlink() or meta_file.exists():
        raise QualityError('Preuve HD existante : aucune modification autorisée')
    data = json.dumps(_provenance(source, output, original_dpi),sort_keys=True)
    fd = os.open(meta_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def _source_under_project(project: Path, raw_path: str) -> Path:
    if not isinstance(raw_path, str) or not raw_path or len(raw_path) > 4096:
        raise QualityError('Chemin PNG manquant ou invalide')
    file = Path(raw_path)
    if not file.is_absolute():
        raise QualityError('Chemin PNG non absolu')
    if file.is_symlink() or file.suffix.lower() != '.png':
        raise QualityError('Chemin PNG symbolique ou format incorrect')
    try:
        real = file.resolve(strict=True)
        real.relative_to(project)
    except (OSError, ValueError):
        raise QualityError('PNG hors du dossier du projet') from None
    if not real.is_file():
        raise QualityError('Fichier PNG introuvable')
    return real


def _safe_root(report: dict) -> Path:
    base = report.get('dossier')
    if not isinstance(base, str) or not base.strip():
        raise QualityError('Dossier projet absent')
    path = Path(base)
    if not path.is_absolute() or path.is_symlink() or not path.is_dir():
        raise QualityError('Dossier projet absent, relatif ou symbolique')
    return path.resolve(strict=True)


def _quality_signal(src: Image.Image) -> tuple[str, float]:
    """Bounded measurement. It only chooses whether *slight* sharpening is safe."""
    scale = min(1.0, 480 / max(src.size))
    size = tuple(max(1, round(d * scale)) for d in src.size)
    sample = src.convert('RGB').resize(size, Image.Resampling.BILINEAR)
    a = np.asarray(sample, np.uint8)
    gray = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY)
    high = np.abs(gray.astype(np.float32) - cv2.GaussianBlur(gray, (3, 3), 0))
    noise = float(np.median(high))
    if noise > 5.0:
        return 'reéchantillonnage seul : texture/bruit trop marqué', noise
    return 'accentuation douce et locale', noise


def _enhance_rgb_preserving_alpha(src: Image.Image, size: tuple[int, int]) -> tuple[Image.Image, str, float]:
    """Lanczos-premultiplied resampling and RGB-only bounded interior sharpening."""
    base = _resample_print(src, size)
    if base.mode != 'RGBA':
        base = base.convert('RGBA')
    method, noise = _quality_signal(src)
    if method.startswith('reéchantillonnage'):
        return base, method, noise

    clean = np.asarray(base, dtype=np.uint8).copy()
    original = Image.fromarray(clean[..., :3], 'RGB')
    sharp = np.asarray(original.filter(ImageFilter.UnsharpMask(radius=0.85, percent=37, threshold=4)))
    original_arr = clean[..., :3]
    distance = np.abs(sharp.astype(np.int16) - original_arr.astype(np.int16))
    # Upper bound prevents oversharpened outlines and color shifts.
    if float(np.mean(distance)) > 3.0 or float(np.mean(distance > 24)) > .01:
        return base, 'reéchantillonnage seul : accentuation refusée (écart excessif)', noise
    opaque = (clean[..., 3] >= 253).astype(np.uint8)
    safe = cv2.erode(opaque, np.ones((5, 5), np.uint8), iterations=1).astype(bool)
    clean[..., :3][safe] = sharp[safe]
    return Image.fromarray(clean, 'RGBA'), method, noise


def _alpha_compatible(original: Image.Image, enhanced: Image.Image) -> bool:
    """Fail closed if anti-aliasing creates or erases meaningful cut regions."""
    a = np.asarray(original.getchannel('A')) >= 128
    b = np.asarray(enhanced.getchannel('A').resize(original.size, Image.Resampling.BOX)) >= 128
    area = int(np.count_nonzero(a))
    if area < 16:
        return False
    intersection = int(np.count_nonzero(a & b))
    union = int(np.count_nonzero(a | b))
    return intersection / max(1, union) >= .985


def _derive(srcpath: Path, dest: Path, dpi: int) -> dict:
    with Image.open(srcpath) as im:
        if im.format != 'PNG' or im.width <= 0 or im.height <= 0:
            raise QualityError('Source non PNG')
        count = im.width * im.height
        if count > MAX_SOURCE_PIXELS:
            raise QualityError('PNG source trop volumineux pour le mode HD automatique')
        original = im.convert('RGBA')
    if dpi not in (300, 450):
        raise QualityError('Densité PNG d’origine inconnue')
    size = (max(1, round(original.width * TARGET_DPI / dpi)),
            max(1, round(original.height * TARGET_DPI / dpi)))
    output_pixels = size[0] * size[1]
    if output_pixels > MAX_DERIVATIVE_PIXELS:
        raise QualityError('Limite mémoire HD par image')
    if size[0] <= original.width:
        raise QualityError('Résolution d’origine déjà suffisante')
    converted, method, noise = _enhance_rgb_preserving_alpha(original, size)
    if not _alpha_compatible(original, converted):
        raise QualityError('Forme du masque changée au contrôle conservateur')
    temp = dest.with_name('.hd_v2171_' + uuid4().hex + '.png')
    try:
        converted.save(temp, format='PNG', dpi=(TARGET_DPI, TARGET_DPI), optimize=True)
        with Image.open(temp) as checked:
            if checked.size != size or checked.mode != 'RGBA':
                raise QualityError('Contrôle du PNG HD créé non conforme')
            # Pillow may slightly round the stored dpi value in the PNG pHYs chunk.
            if not 595 <= (checked.info.get('dpi') or (0,))[0] <= 605:
                raise QualityError('Densité du PNG HD invalide')
        os.replace(temp, dest)
    finally:
        temp.unlink(missing_ok=True)
    return {'fichier_hd': str(dest), 'dimensions_px': list(size),
            'densite_cible_ppp': TARGET_DPI, 'methode': method,
            'indice_bruit': round(noise, 2), 'pixels_hd': output_pixels,
            'alpha_original_non_modifie': True, 'svg_original_non_modifie': True}


def automatic_hd(report: dict, original_dpi: int) -> dict:
    """Create derivatives for each manufacturing PNG, with explicit skip reasons.

    A nonessential HD failure never invalidates the original production.
    """
    result = {'version': VERSION, 'mode': 'automatique_conservateur',
              'statut': 'ignore', 'cible_ppp': TARGET_DPI,
              'total': 0, 'produits': 0, 'reutilises': 0, 'ignores': 0, 'fichiers': [],
              'contours_svg_et_png_fabrication_preserves': True,
              'confirmation_decoupe_physique': False,
              'note': 'Option HD complémentaire : vérifier la taille dans Cricut Design Space.'}
    try:
        root = _safe_root(report)
        objects = report.get('objets', [])
        if not isinstance(objects, list) or len(objects) > MAX_ITEMS:
            raise QualityError('Nombre de sujets hors limites (32 max)')
        dpi = int(original_dpi)
        if dpi not in (300, 450):
            raise QualityError('Densité originale non prise en charge')
        if not objects:
            result['note'] = 'Aucun objet à améliorer ; production historique conservée.'
            return result
        destdir = root / FOLDER
        if destdir.is_symlink():
            raise QualityError('Dossier HD symbolique interdit')
        destdir.mkdir(exist_ok=True)
        if destdir.resolve() != (root / FOLDER).resolve() or not destdir.resolve().is_relative_to(root):
            raise QualityError('Dossier HD hors du projet')
        result['total'] = len(objects)
        budget = MAX_TOTAL_DERIVATIVE_PIXELS
        for i, obj in enumerate(objects, 1):
            record = {'objet': i, 'statut': 'ignore'}
            result['fichiers'].append(record)
            try:
                if not isinstance(obj, dict):
                    raise QualityError('Objet du rapport malformé')
                source = _source_under_project(root, obj.get('fichier_png_cricut') or obj.get('png'))
                with Image.open(source) as im:
                    estimated = round(im.width * TARGET_DPI / dpi) * round(im.height * TARGET_DPI / dpi)
                if estimated > budget:
                    raise QualityError('Budget mémoire global HD atteint')
                dest = destdir / f'sujet_{i:03d}_HD.png'
                if dest.exists() or dest.is_symlink():
                    meta = _reuse_existing(source, dest, dpi)
                    record.update(meta)
                    record.update({'statut': 'reutilise', 'fichier_original': str(source)})
                    result['reutilises'] += 1
                else:
                    if _provenance_file(dest).exists() or _provenance_file(dest).is_symlink():
                        raise QualityError('Preuve HD orpheline : pas de remplacement')
                    meta = _derive(source, dest, dpi)
                    try:
                        _save_provenance(source, dest, dpi)
                    except BaseException:
                        # Do not leave an untraceable derivative that blocks reruns.
                        dest.unlink(missing_ok=True)
                        _provenance_file(dest).unlink(missing_ok=True)
                        raise
                    budget -= meta.pop('pixels_hd')
                    record.update(meta)
                    record.update({'statut': 'produit', 'fichier_original': str(source)})
                    result['produits'] += 1
            except (QualityError, OSError, ValueError, RuntimeError, MemoryError,
                    Image.DecompressionBombError) as exc:
                record['raison'] = str(exc)[:180]
                result['ignores'] += 1
        result['statut'] = ('complete' if result['produits'] + result['reutilises'] == result['total']
                            else 'partielle' if result['produits'] + result['reutilises'] else 'ignore')
        # Independent report: historical fabrication reports remain byte-identical.
        file = destdir / 'RAPPORT_HD_V21_7_1.json'
        if not file.is_symlink():
            temp = destdir / ('.rapport_' + uuid4().hex + '.tmp')
            try:
                temp.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
                os.replace(temp, file)
            finally:
                temp.unlink(missing_ok=True)
    except (QualityError, OSError, ValueError, RuntimeError, MemoryError) as exc:
        result['statut'] = 'ignore'
        result['note'] = 'HD désactivée sans toucher aux fichiers de fabrication : ' + str(exc)[:180]
    return result
