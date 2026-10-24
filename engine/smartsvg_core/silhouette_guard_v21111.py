"""Conservative cutout shape checks shared by auto-masking and Cricut preflight.

Rectangular-looking cutouts must not be marked as a proven subject silhouette,
even if antialiasing removes a handful of corner pixels.
"""
from __future__ import annotations
import numpy as np


def near_rectangle(binary, *, threshold=0.985):
    """True if the occupied bbox is almost entirely opaque (incl. 1px defects)."""
    pixels=np.asarray(binary,dtype=np.bool_)
    if pixels.ndim!=2:raise ValueError('Silhouette 2D requise')
    yy,xx=np.nonzero(pixels)
    if not len(xx):return True
    bbox_area=(int(xx.max())-int(xx.min())+1)*(int(yy.max())-int(yy.min())+1)
    return len(xx)/bbox_area >= threshold
