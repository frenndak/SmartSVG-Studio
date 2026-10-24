"""Safe, bounded SVG root metadata inspection, without following external references."""
from __future__ import annotations
from pathlib import Path
import re
import xml.etree.ElementTree as ET

MAX_SVG_BYTES=8_000_000
MM=re.compile(r'^\s*(\d+(?:\.\d+)?)\s*mm\s*$',re.I)


def svg_physical_width(path):
    p=Path(path)
    if not p.is_file() or p.is_symlink() or p.stat().st_size>MAX_SVG_BYTES:
        raise ValueError('SVG absent, lien symbolique ou trop volumineux')
    content=p.read_bytes()
    if b'<!DOCTYPE' in content.upper() or b'<!ENTITY' in content.upper():
        raise ValueError('DTD ou entité non autorisée dans le SVG')
    try:element=ET.fromstring(content)
    except ET.ParseError as exc:raise ValueError('SVG XML invalide') from exc
    if element.tag.rsplit('}',1)[-1]!='svg':
        raise ValueError('La racine doit être svg')
    value=element.attrib.get('width','')
    match=MM.fullmatch(value)
    return float(match.group(1)) if match else None
