"""Conservative static SVG Basic Cut preflight (V21.15.3).

This *does not* simulate Cricut Design Space nor validate a physical cut.
Only paths with a demonstrable closed, nonzero contour may pass the static gate.
Non-polygonal paths remain subject to human inspection.
"""
from __future__ import annotations
import math
import re
from xml.etree.ElementTree import Element

TOKEN = re.compile(r'[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')
SEPARATORS = re.compile(r'[\s,]*')
ALLOWED_TAGS = frozenset({'svg', 'g', 'path', 'title', 'desc'})
MAX_PATH_ELEMENTS = 5000
MAX_PATH_CHARS = 2_000_000

class CutPathError(ValueError):
    """A file cannot be trusted as a Basic Cut path at this preflight stage."""


def _tokens(d: str) -> list[str]:
    if not isinstance(d, str) or not d.strip() or len(d) > MAX_PATH_CHARS:
        raise CutPathError('tracé SVG vide ou trop long')
    out = []
    pos = 0
    while pos < len(d):
        pos = SEPARATORS.match(d, pos).end()
        if pos == len(d):
            break
        match = TOKEN.match(d, pos)
        if not match:
            raise CutPathError('syntaxe de tracé SVG inconnue')
        value = match.group()
        if value not in 'MmLlHhVvCcSsQqTtAaZz':
            number = float(value)
            if not math.isfinite(number) or abs(number) > 1_000_000:
                raise CutPathError('coordonnée de contour invalide')
        out.append(value)
        pos = match.end()
    return out


def _polygon_area(tokens: list[str]) -> float:
    """Signed polygon area magnitude for SVG M/L/Z commands, including relative."""
    i = 0
    mode = None
    x = y = 0.0
    subpath = []
    areas = []
    while i < len(tokens):
        if tokens[i] in 'MmLlZz' and len(tokens[i]) == 1:
            mode = tokens[i]
            i += 1
            if mode in 'Zz':
                if len(subpath) < 3:
                    raise CutPathError('contour SVG avec moins de trois sommets')
                twice = sum(ax * by - bx * ay for (ax, ay), (bx, by) in
                            zip(subpath, subpath[1:] + subpath[:1]))
                areas.append(abs(twice) / 2)
                x, y = subpath[0]
                subpath = []
                mode = None
                continue
        if mode not in ('M', 'm', 'L', 'l') or i + 1 >= len(tokens):
            raise CutPathError('commande ou coordonnées SVG incomplètes')
        if len(tokens[i]) == 1 and tokens[i] in 'MmLlZz':
            raise CutPathError('nombre de coordonnées SVG invalide')
        nx, ny = float(tokens[i]), float(tokens[i + 1])
        i += 2
        if mode.islower():
            nx += x
            ny += y
        x, y = nx, ny
        if mode in 'Mm' and subpath:
            raise CutPathError('nouvelle sous-forme sans fermeture')
        subpath.append((x, y))
        if mode == 'M':
            mode = 'L'
        elif mode == 'm':
            mode = 'l'
    if subpath or not areas:
        raise CutPathError('contour SVG non fermé')
    return sum(areas)


def inspect_cut_paths(root: Element) -> dict:
    """Inspect parsed XML and reject deceptive or unsafe Basic Cut markup.

    Geometry is checked exactly for M/L/Z polygonal paths. Other legal path
    commands require an explicit visual-review caveat; they are never claimed
    to be physically cut-tested.
    """
    if root.tag.rsplit('}', 1)[-1] != 'svg':
        raise CutPathError('racine non SVG')
    paths = []
    for element in root.iter():
        tag = element.tag.rsplit('}', 1)[-1]
        if tag not in ALLOWED_TAGS:
            raise CutPathError('élément incompatible avec SVG de contour: ' + tag)
        for key, value in element.attrib.items():
            name = key.rsplit('}', 1)[-1].lower()
            if (name.startswith('on') or name in ('href', 'style', 'transform')
                    or 'url(' in value.lower() or 'javascript:' in value.lower()):
                raise CutPathError('attribut actif, lien ou transformation SVG interdit')
        if tag == 'path':
            paths.append(element)
    if not paths or len(paths) > MAX_PATH_ELEMENTS:
        raise CutPathError('nombre de chemins SVG absent ou excessif')
    has_curves = False
    for path in paths:
        tokens = _tokens(path.get('d', ''))
        commands = [t for t in tokens if len(t) == 1 and t in 'MmLlHhVvCcSsQqTtAaZz']
        if sum(t in 'Mm' for t in commands) != sum(t in 'Zz' for t in commands) or not commands or commands[-1] not in 'Zz':
            raise CutPathError('sous-contour SVG ouvert')
        if all(t in 'MmLlZz' for t in commands):
            if _polygon_area(tokens) <= .001:
                raise CutPathError('contour SVG dégénéré ou sans surface')
        else:
            if len(tokens) < 8:
                raise CutPathError('géométrie SVG courbe insuffisante')
            has_curves = True
    return {'path_elements': len(paths), 'closed_paths_checked': True,
            'nonpolygonal_paths_require_visual_review': has_curves}
