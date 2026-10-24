"""Cricut-safe photo layers: lossless visible pixels and padded exterior contours.

No ML inference, no semantic labels and no guarantee of machine cutting behavior.
"""
from __future__ import annotations
import cv2
import numpy as np
from PIL import Image

class InvalidCutout(ValueError):
    pass


def mask_support(mask):
    """Include soft edges, not only pixels above the segmentation threshold."""
    if np.asarray(mask).ndim != 2:
        raise InvalidCutout('Masque 2D requis')
    return np.asarray(mask) > (0.5/255.0)


def cutout_with_white_border(rgb, mask, *, mm_per_px, white_offset_mm):
    """Return (source-faithful RGBA crop, opaque-white-border RGBA, bounds).

    Each cutout includes padding OUTSIDE the source image at its edges; holes
    inside the silhouette are white-filled so Cricut cuts only outer contours.
    """
    rgb=np.asarray(rgb)
    mask=np.asarray(mask,dtype=np.float32)
    if rgb.ndim!=3 or rgb.shape[-1]!=3 or rgb.shape[:2]!=mask.shape:
        raise InvalidCutout('Image / masque incompatibles')
    if not np.isfinite(mask).all() or np.min(mask)<0 or np.max(mask)>1:
        raise InvalidCutout('Masque non fini ou hors de 0..1')
    if mm_per_px<=0 or not 0<=white_offset_mm<=5:
        raise InvalidCutout('Marge physique invalide')
    support=mask_support(mask)
    if not bool(np.any(support)):
        raise InvalidCutout('Masque sans pixels visibles')
    yy,xx=np.where(support)
    x0,y0,x1,y1=int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)
    source_rgb=rgb[y0:y1,x0:x1].copy()
    source_mask=mask[y0:y1,x0:x1]
    h,w=source_mask.shape
    alpha=np.uint8(np.clip(source_mask*255,0,255)+.5)
    original=np.dstack([source_rgb,alpha])
    original[alpha==0,:3]=0
    radius=int(round(white_offset_mm/mm_per_px)) if white_offset_mm>0 else 0
    if radius>400:
        raise InvalidCutout('Bordure trop grande pour resolution demandee')
    padding=radius+3
    # Work locally: do not duplicate the entire photograph for every object.
    core=(source_mask>=.5).astype(np.uint8)
    count, contours = None, None
    contours,_=cv2.findContours(core,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    shape=np.zeros_like(core)
    if contours:
        cv2.drawContours(shape,contours,-1,255,-1)
    # The soft edge can protrude beyond the >=0.5 segmentation. Without this
    # union, hair/mousse pixels at alpha 0.2 disappear from the printable PNG
    # at zero offset. Preserve the ORIGINAL RGBA separately in every case.
    shape=cv2.bitwise_or(shape,(support[y0:y1,x0:x1].astype(np.uint8)*255))
    shape=cv2.copyMakeBorder(shape,padding,padding,padding,padding,cv2.BORDER_CONSTANT,value=0)
    if radius:
        kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*radius+1,2*radius+1))
        shape=cv2.dilate(shape,kernel)
    if not shape.any():
        raise InvalidCutout('Aucune silhouette imprimable')
    white=np.zeros((h+2*padding,w+2*padding,4),np.uint8)
    white[shape>0,:3]=255
    white[shape>0,3]=255
    a=source_mask[...,None]
    # Alpha-composite original pixels onto WHITE opaque underlay; white border
    # remains opaque, soft hair/mousse is pre-composited onto print white.
    composited=np.clip(source_rgb.astype(np.float32)*a+255*(1-a)+.5,0,255).astype(np.uint8)
    inset=white[padding:padding+h,padding:padding+w]
    inset[shape[padding:padding+h,padding:padding+w]>0,:3]=composited[shape[padding:padding+h,padding:padding+w]>0]
    # no decorative RGB stored outside alpha region
    return original,white,(x0,y0,x1,y1),{'rayon_marge_px':radius,
       'marge_voulue_mm':float(white_offset_mm),'padding_px':padding,
       'dimensions_png_cricut_pixels':[int(white.shape[1]),int(white.shape[0])],
       'trous_interieurs_remplis_blanc':True,'marge_hors_image_source_possible':True,
       'support_alpha_faible_inclus':True}
