#!/usr/bin/env python3
"""Basic static SVG preflight for Cricut-oriented files, NOT a Design Space certification.

Strict only for deliberately self-contained vector fixtures. No rendering,
flattening, geometry offset simulation or machine/knife modeling occurs here.
"""
from __future__ import annotations

import argparse
from io import BytesIO
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
VECTOR_ELEMENTS = {"path", "rect", "circle", "ellipse", "polygon", "polyline", "line"}
# Geometry inside these SVG containers is not directly rendered. Counting it
# would falsely pass a file containing definitions but no visible cut shapes.
NON_RENDERING_CONTAINERS = {"defs", "symbol", "clipPath", "mask", "pattern", "marker"}
FORBIDDEN = {"script", "style", "a", "foreignObject", "image", "use", "animate", "animateMotion",
             "animateTransform", "set", "filter", "feImage", "textPath"}
DIMENSION = re.compile(r"^(\d+(?:\.\d+)?)mm$")


class SVGRejected(ValueError):
    pass


def inspect_svg(path: Path, *, profile: str = "cut", max_bytes: int = 2_000_000) -> dict:
    if profile not in {"cut", "editable"}:
        raise SVGRejected("UNKNOWN_PROFILE")
    if not path.is_file() or path.stat().st_size > max_bytes or max_bytes <= 0:
        raise SVGRejected("FILE_MISSING_OR_TOO_LARGE")
    raw = path.read_bytes()
    if re.search(rb"<!\s*(?:DOCTYPE|ENTITY)\b", raw, re.IGNORECASE):
        raise SVGRejected("DTD_OR_ENTITY_DECLARATION")
    try:
        # ElementTree.fromstring() silently discards XML processing instructions,
        # including a prolog xml-stylesheet that could load external resources
        # when the same file is later opened by another SVG consumer.
        if any(True for _event, _node in ET.iterparse(BytesIO(raw), events=("pi",))):
            raise SVGRejected("PROCESSING_INSTRUCTION")
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise SVGRejected("INVALID_XML") from exc
    if root.tag != f"{{{SVG_NS}}}svg":
        raise SVGRejected("NOT_SVG_NAMESPACE")
    view = root.attrib.get("viewBox", "").replace(",", " ").split()
    try:
        coords = tuple(float(v) for v in view)
    except ValueError as exc:
        raise SVGRejected("INVALID_VIEWBOX") from exc
    if len(coords) != 4 or not all(math.isfinite(v) for v in coords) or coords[2] <= 0 or coords[3] <= 0:
        raise SVGRejected("INVALID_VIEWBOX")
    sizes = []
    for key in ("width", "height"):
        m = DIMENSION.fullmatch(root.attrib.get(key, ""))
        if m is None:
            raise SVGRejected("EXPLICIT_MM_REQUIRED")
        size_mm = float(m.group(1))
        if not math.isfinite(size_mm) or size_mm <= 0:
            raise SVGRejected("EXPLICIT_MM_REQUIRED")
        sizes.append(size_mm)
    shapes = []
    # An iterative traversal tracks non-rendering ancestors without relying on
    # ElementTree parent pointers (and avoids unbounded Python recursion).
    pending = [(root, False)]
    while pending:
        node, inside_definition = pending.pop()
        if not node.tag.startswith("{" + SVG_NS + "}"):
            raise SVGRejected("FOREIGN_XML_ELEMENT")
        tag = node.tag.split("}", 1)[1]
        if tag in FORBIDDEN:
            raise SVGRejected("EMBEDDED_RESOURCE_OR_ACTIVE_CONTENT")
        # display:none suppresses rendering of the whole subtree. Unlike
        # visibility:hidden, descendants cannot override this with CSS.
        # Reject escaped CSS earlier; match safe inline declarations here.
        style = node.attrib.get("style", "")
        display_none = node.attrib.get("display", "").strip().lower() == "none" or bool(
            re.search(r"(?:^|;)\s*display\s*:\s*none\s*(?:!important\s*)?(?:;|$)", style, re.I)
        )
        inside_definition = (inside_definition or tag in NON_RENDERING_CONTAINERS
                             or display_none)
        pending.extend((child, inside_definition) for child in reversed(node))
        for attr, val in node.attrib.items():
            local = attr.split("}", 1)[-1]
            lower = val.lower()
            # CSS escapes (e.g. u\\72l(...)) and comments can disguise active
            # references from a plain substring scan. This deliberately strict
            # static preflight cannot safely interpret arbitrary CSS: fail closed.
            if "\\" in val or "/*" in val or "*/" in val:
                raise SVGRejected("OBFUSCATED_CSS_REFERENCE")
            if local.lower().startswith("on") or attr.startswith("{" + XLINK_NS + "}"):
                raise SVGRejected("EVENT_OR_EXTERNAL_REFERENCE")
            if local in ("href", "src") or "url(" in lower or "javascript:" in lower or "data:" in lower:
                raise SVGRejected("EVENT_OR_EXTERNAL_REFERENCE")
        if tag in VECTOR_ELEMENTS:
            if tag == "path" and not node.attrib.get("d", "").strip():
                raise SVGRejected("EMPTY_PATH")
            if not inside_definition:
                shapes.append(tag)
    if not shapes:
        raise SVGRejected("NO_VECTOR_GEOMETRY")
    if profile == "editable" and len(shapes) < 2:
        raise SVGRejected("INSUFFICIENT_SEPARATE_VECTOR_OBJECTS")
    return {
        "status": "preflight_passed_not_machine_verified",
        "profile": profile,
        "width_mm": sizes[0],
        "height_mm": sizes[1],
        "view_box": list(coords),
        "vector_elements": len(shapes),
        "contains_embedded_raster": False,
        "design_space_import_verified": False,
        "physical_cut_verified": False,
        "vector_editability_guaranteed": False,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("svg", type=Path)
    p.add_argument("--profile", choices=("cut", "editable"), default="cut")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    try:
        data = inspect_svg(args.svg, profile=args.profile)
        print(json.dumps(data, indent=2) if args.json else
              f"PASS (static only): {data['vector_elements']} vector objects, {data['width_mm']} x {data['height_mm']} mm")
        return 0
    except SVGRejected as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
