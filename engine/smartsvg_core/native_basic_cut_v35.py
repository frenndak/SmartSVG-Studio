"""W04: pure vector Basic Cut SVG polygon preview; never writes user files."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import math
import xml.etree.ElementTree as ET

_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", _NS)

class BasicCutError(ValueError):
    pass

@dataclass(frozen=True)
class BasicCutPreview:
    svg: bytes
    sha256: str
    width_mm: float
    height_mm: float
    ring_count: int
    verified_readback: bool
    physical_cut_tested: bool = False

def _num(value):
    if type(value) not in (int, float) or not math.isfinite(value) or abs(value) > 10000:
        raise BasicCutError("INVALID_NUMBER")
    return float(value)

def _fmt(n):
    return (f"{n:.4f}".rstrip("0").rstrip(".") or "0") if n else "0"

def _cross(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])

def _intersect(a,b,c,d):
    def on(p,q,r):
        return abs(_cross(p,q,r)) < 1e-8 and all(min(p[i],q[i])-1e-8 <= r[i] <= max(p[i],q[i])+1e-8 for i in (0,1))
    if any((on(a,b,c),on(a,b,d),on(c,d,a),on(c,d,b))):
        return True
    return (_cross(a,b,c)>0)!=(_cross(a,b,d)>0) and (_cross(c,d,a)>0)!=(_cross(c,d,b)>0)

def _ring(raw):
    if type(raw) not in (tuple,list) or not 3 <= len(raw) <= 4096:
        raise BasicCutError("INVALID_RING")
    points=[]
    for p in raw:
        if type(p) not in (tuple,list) or len(p)!=2:
            raise BasicCutError("INVALID_POINT")
        points.append((_num(p[0]),_num(p[1])))
    if points[0]==points[-1]:
        points.pop()
    if len(points)<3 or len(set(points))!=len(points):
        raise BasicCutError("DEGENERATE_RING")
    if abs(sum(_cross((0,0),a,b) for a,b in zip(points,points[1:]+points[:1]))) < 1e-7:
        raise BasicCutError("DEGENERATE_RING")
    n=len(points)
    for i in range(n):
        for j in range(i+2,n):
            if i==0 and j==n-1:
                continue
            if _intersect(points[i],points[(i+1)%n],points[j],points[(j+1)%n]):
                raise BasicCutError("SELF_INTERSECTING_RING")
    return points

def _inside(p,ring):
    x,y=p
    result=False
    for a,b in zip(ring,ring[1:]+ring[:1]):
        if (a[1]>y)!=(b[1]>y) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:
            result=not result
    return result

def preview_basic_cut(*, rings, width_mm, height_mm):
    """One outer polygon and up to 31 disjoint holes, in mm. No curves/raster/PTC."""
    width,height=_num(width_mm),_num(height_mm)
    if not 0.01 <= width <= 10000 or not 0.01 <= height <= 10000:
        raise BasicCutError("INVALID_SIZE")
    if type(rings) not in (tuple,list) or not 1 <= len(rings) <= 32:
        raise BasicCutError("INVALID_RING_COUNT")
    paths=[_ring(r) for r in rings]
    for ring in paths:
        if any(x<0 or y<0 or x>width or y>height for x,y in ring):
            raise BasicCutError("OUTSIDE_VIEWBOX")
    for i,ring in enumerate(paths):
        if i and not all(_inside(p,paths[0]) for p in ring):
            raise BasicCutError("HOLE_OUTSIDE")
        for other in paths[:i]:
            if any(_intersect(a,b,c,d) for a,b in zip(ring,ring[1:]+ring[:1]) for c,d in zip(other,other[1:]+other[:1])):
                raise BasicCutError("RINGS_INTERSECT")
        if i and any(_inside(ring[0],other) or _inside(other[0],ring) for other in paths[1:i]):
            raise BasicCutError("NESTED_HOLES")
    d=" ".join("M "+" L ".join(f"{_fmt(x)} {_fmt(y)}" for x,y in ring)+" Z" for ring in paths)
    view=f"0 0 {_fmt(width)} {_fmt(height)}"
    root=ET.Element(f"{{{_NS}}}svg",{"version":"1.1","width":_fmt(width)+"mm","height":_fmt(height)+"mm","viewBox":view})
    ET.SubElement(root,f"{{{_NS}}}path",{"d":d,"fill":"black","fill-rule":"evenodd"})
    svg=ET.tostring(root,encoding="utf-8",xml_declaration=True)
    check=ET.fromstring(svg)
    child=check.find(f"{{{_NS}}}path")
    if check.get("viewBox")!=view or child is None or child.get("d")!=d or child.get("fill-rule")!="evenodd":
        raise BasicCutError("READBACK_FAILED")
    return BasicCutPreview(svg,hashlib.sha256(svg).hexdigest(),width,height,len(paths),True)
