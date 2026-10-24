"""Small, read-only cross-check between exported PNG and SVG dimensions.

Design Space may choose a different import size. The inspection is informational.
"""
from __future__ import annotations
from pathlib import Path
import math
from ..smartsvg_vector.metadata import svg_physical_width


def report_dimension_disagreements(report, *, tolerance_mm=0.6):
    """Uses metadata already in the report; never opens/changes production PNGs."""
    out=[]
    for i, item in enumerate(report.get('objets',[]),1):
        if not isinstance(item,dict):continue
        details=item.get('controle_physique_v211',{})
        if not isinstance(details,dict):continue
        png_mm=details.get('largeur_png_mm_si_ppp_respectes')
        svg_mm=details.get('largeur_svg_mm')
        if not isinstance(png_mm,(int,float)) or not isinstance(svg_mm,(int,float)):
            continue
        if not math.isfinite(png_mm) or not math.isfinite(svg_mm):
            out.append(f'OBJET_{i}_TAILLE_NON_FINIE')
        elif abs(png_mm-svg_mm)>tolerance_mm:
            out.append(f'OBJET_{i}_PNG_SVG_TAILLES_INCOHERENTES')
    return out
