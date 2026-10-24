"""Conservative screenshot cropping, with explicit no-crop fallback.

Crop should happen BEFORE segmentation, brush edits and Cricut export so IMAGE
and MASK pixel coordinate systems remain aligned. No generative content.
"""
from __future__ import annotations
import numpy as np

MAX_PIXELS = 5_000_000

class PreparationError(ValueError):
    pass


def _validate(rgb):
    a=np.asarray(rgb)
    if a.ndim != 3 or a.shape[2] not in (3,4) or min(a.shape[:2])<1 or a.shape[0]*a.shape[1]>MAX_PIXELS:
        raise PreparationError('Préparation : image RGB(A) unique, maximum 5 Mp')
    if not np.isfinite(a).all() or a.min() < -.001 or a.max() > 1.001:
        raise PreparationError('Préparation : couleurs invalides')
    return a


def crop_manual(image, left=0, right=0, top=0, bottom=0):
    a=_validate(image);h,w=a.shape[:2]
    params=(left,right,top,bottom)
    if any(type(x) is not int or x<0 or x>45 for x in params):
        raise PreparationError('Recadrage : marges en pourcentages entiers entre 0 et 45')
    x0=round(left*w/100);x1=w-round(right*w/100)
    y0=round(top*h/100);y1=h-round(bottom*h/100)
    if (x1-x0)<max(12,int(.20*w)) or (y1-y0)<max(12,int(.20*h)):
        raise PreparationError('Recadrage : conserver au moins 20 % de chaque dimension')
    return (x0,y0,x1,y1)


def crop_black_bands(image):
    """Crop only if significant near-perfect black bars bracket dominant content.

    A screenshot can contain UI at top/bottom; we locate the LONGEST non-black
    segment surrounded by black-bar runs, ignoring shorter bars not safely
    distinguishable from drawing content. For undecidable input, return unchanged.
    """
    a=_validate(image);h,w=a.shape[:2]
    if h<160 or w<140: return (0,0,w,h),'Image petite : aucun recadrage automatique'
    # Ignore alpha; alpha photos from the loader may be empty/white matte.
    rgb=a[...,:3]
    almost_black=(rgb<=12/255).all(axis=2)
    coverage=almost_black.mean(axis=1)
    is_bar=coverage >= .985
    # fill very short interruptions caused by minor UI text/noise? No: conservative.
    segments=[];start=0;value=bool(is_bar[0])
    for i in range(1,h):
        if bool(is_bar[i])!=value:
            segments.append((value,start,i));start=i;value=bool(is_bar[i])
    segments.append((value,start,h))
    min_bar=max(16,round(h*.045))
    candidates=[]
    for idx,(bar,begin,end) in enumerate(segments):
        if bar or end-begin<h*.26:continue
        left=segments[idx-1] if idx else None
        right=segments[idx+1] if idx+1<len(segments) else None
        # Require black bands on BOTH sides for this conservative auto mode.
        if not(left and right and left[0] and right[0] and left[2]-left[1]>=min_bar and right[2]-right[1]>=min_bar):
            continue
        # Ensure the region contains genuine non-black content, not noise.
        colorful=rgb[begin:end]
        if float(np.mean(colorful))<.065 or float(np.std(colorful))<.09:continue
        candidates.append((end-begin,begin,end))
    if len(candidates)!=1:
        return (0,0,w,h),'Bandes insuffisantes ou ambiguës : image conservée (recadrage manuel possible)'
    _,top,bottom=candidates[0]
    if top<1 or bottom>=h or bottom-top<.26*h:
        return (0,0,w,h),'Recadrage incertain : image conservée'
    return (0,top,w,bottom),'Bandes noires franches détectées : recadrage vertical prudent'


def prepare(image,mode='Conserver original', *,left=0,right=0,top=0,bottom=0):
    a=_validate(image);h,w=a.shape[:2]
    if mode=='Conserver original':
        box=(0,0,w,h);note='Aucun recadrage'
    elif mode=='Retirer bandes noires (prudent)':
        box,note=crop_black_bands(a)
    elif mode=='Recadrage manuel (%)':
        box=crop_manual(a,left,right,top,bottom);note='Marges manuelles appliquées'
    else:raise PreparationError('Mode de préparation inconnu')
    x0,y0,x1,y1=box
    out=a[y0:y1,x0:x1,:]
    return out,{'version':'21.7','mode':mode,'source_px':[w,h],
      'sortie_px':[x1-x0,y1-y0],'zone_px':[x0,y0,x1,y1],
      'modifie':box!=(0,0,w,h),'message':note,'avertissement':'Faire le recadrage avant segmentation et retouche des masques.'}
