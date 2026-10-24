"""V21.9 native-resolution (not 760px) visual inspection of source and cut masks.

Only UI copies are published: masks and source passed to the manufacturing engine
are never mutated. No inference, retouching, or physical cutting claims.
"""
from __future__ import annotations
import json
import math
import os
from pathlib import Path
import re
import uuid
from time import time

import cv2
import numpy as np
from PIL import Image

from ..smartsvg_quality.geometry import inspect as quality_inspect

FOLDER = 'SmartSVG_Studio_Native_V219'
PATTERN = re.compile(r'ni_[0-9a-f]{24}_(?:image|mask[0-9]{2})\.png\Z')
MAX_BYTES = 192_000_000
MAX_SESSION_BYTES = 64_000_000
MAX_SESSIONS = 8
MAX_AGE_SECONDS = 48 * 3600
MAX_SPOTS_PER_OBJECT = 8

class NativeInspectionError(ValueError):
    pass


def validate(image, masks):
    a = np.asarray(image)
    m = np.asarray(masks)
    if a.ndim != 3 or a.shape[2] not in (3, 4) or m.ndim != 3 or a.shape[:2] != m.shape[1:] or not 1 <= m.shape[0] <= 32:
        raise NativeInspectionError('Inspecteur : IMAGE HxWxRGB(A) et MASK NxHxW alignés requis')
    h, w = a.shape[:2]
    if h < 1 or w < 1 or h*w > 5_000_000 or m.size > 50_000_000:
        raise NativeInspectionError('Inspecteur : plafond 5 Mp source / 50 Mp masques')
    if not np.issubdtype(a.dtype, np.number) or not np.issubdtype(m.dtype, np.number) or not np.isfinite(a).all() or not np.isfinite(m).all():
        raise NativeInspectionError('Inspecteur : image ou masques invalides (NaN/inf)')
    if m.min() < -.001 or m.max() > 1.001:
        raise NativeInspectionError('Inspecteur : les masques doivent rester entre 0 et 1')
    return a, m


def find_spots(mask, other_masks=None, *, width_mm=40.0):
    """Rank *inspection hints*; they do not establish a safe Cricut contour.

    Results are source pixel coordinates; source-image absolute positions are never
    inferred from a resized QA thumbnail.
    """
    binary = np.uint8(np.asarray(mask) >= .5)
    h, w = binary.shape
    spots = []
    def add(kind, x, y, severity, detail):
        if 0 <= x < w and 0 <= y < h:
            spots.append({'type':kind, 'x':int(x), 'y':int(y), 'priorite':severity, 'detail':detail})
    count, labels, stats, centres = cv2.connectedComponentsWithStats(binary,8)
    comps=sorted(range(1,count),key=lambda k:int(stats[k,cv2.CC_STAT_AREA]), reverse=True)
    if not comps:
        add('MASQUE_VIDE',w//2,h//2,0,'Aucune zone à découper; export non validé')
        return spots
    for index in comps[1:]:
        cx,cy=centres[index]; add('ILOT_DETACHE',int(round(cx)),int(round(cy)),1,'Zone isolée : contrôler si elle doit être découpée')
    # The border can be touched by any component, not just the largest one.
    # Mark actual selected pixels rather than bounding-box corners (which may
    # be in the background for concave objects).
    edges=[(0,0),(w-1,0),(0,h-1),(w-1,h-1)]
    for axis,value in ((0,0),(0,h-1),(1,0),(1,w-1)):
        strip=binary[value,:] if axis==0 else binary[:,value]
        nz=np.flatnonzero(strip)
        if len(nz):
            middle=int(nz[len(nz)//2]);x,y=(middle,value) if axis==0 else (value,middle)
            add('BORD_IMAGE',x,y,1,'Une zone sélectionnée touche le bord de l’image')
    contours,hierarchy=cv2.findContours(binary,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is not None:
        for j,entry in enumerate(hierarchy[0]):
            if entry[3] >= 0:
                mu=cv2.moments(contours[j]);
                if mu['m00']>0:
                    cx=int(mu['m10']/mu['m00']);cy=int(mu['m01']/mu['m00'])
                else:
                    x,y,bw,bh=cv2.boundingRect(contours[j]);cx=x+bw//2;cy=y+bh//2
                add('TROU_INTERIEUR',cx,cy,2,'Trou intérieur : vérifier sa découpe ou son maintien')
    if other_masks is not None:
        overlap = binary.astype(bool) & np.asarray(other_masks,dtype=bool)
        if np.any(overlap):
            yy,xx=np.nonzero(overlap);mid=len(xx)//2
            add('MASQUES_CHEVAUCHANTS',int(xx[mid]),int(yy[mid]),0,'Deux sujets partagent des pixels : risque de découpe double')
    # Narrow necks: use distance transform on foreground (>=1 pixel), prioritize
    # only true topology changes after a light opening, not all ordinary edges.
    if len(comps) == 1:
        kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
        eroded=cv2.erode(binary,kernel)
        groups=cv2.connectedComponents(eroded,8)[0]-1
        if groups > 1:
            lost=binary.astype(bool)&(~eroded.astype(bool));yy,xx=np.nonzero(lost)
            if len(xx):add('PASSAGE_FIN_POSSIBLE',int(np.median(xx)),int(np.median(yy)),3,'Segment étroit probable, inspection nécessaire')
    # Sort stable and suppress nearby duplicate markers of the same kind.
    spots.sort(key=lambda s:(s['priorite'],s['type'],s['y'],s['x']))
    out=[]
    for spot in spots:
        if all(s['type']!=spot['type'] or (s['x']-spot['x'])**2+(s['y']-spot['y'])**2>32**2 for s in out):
            out.append(spot)
        if len(out)>=MAX_SPOTS_PER_OBJECT:break
    return out


def analyse(image,masks,*,width_mm=40.0):
    a,m=validate(image,masks)
    if isinstance(width_mm,bool) or not isinstance(width_mm,(int,float)) or not math.isfinite(width_mm) or not 5<=width_mm<=300:
        raise NativeInspectionError('Inspecteur : largeur finale entre 5 et 300 mm')
    qa=quality_inspect(m,width_mm=width_mm)
    binary=(m >= .5)
    # O(N*H*W) time once, rather than allocating and scanning N copies of
    # N-1 complete masks (up to 50 million elements EACH for large sheets).
    occupancy=(np.sum(binary,axis=0,dtype=np.uint8) if len(m)>1 else None)
    result=[]
    for idx in range(len(m)):
        other=(occupancy > binary[idx] if occupancy is not None else None)
        obj=qa['objets'][idx]
        result.append({'objet':idx+1,'etat':obj['etat'],'alertes':obj['alertes'],
                       'points':find_spots(m[idx],other,width_mm=width_mm)})
    return {'version':'21.9','resolution':{'largeur_px':int(a.shape[1]),'hauteur_px':int(a.shape[0])},
            'nombre_objets':int(len(m)),'statut':qa['statut'],'qa_geometrie':qa,
            'objets':result,'apercu_natif_possible':True,
            'limites':'Diagnostic non destructif avant export. Import dans Design Space et découpe Cricut physique non validés.'}


def _owned_files(folder):
    return sorted((p for p in folder.iterdir() if p.is_file() and not p.is_symlink() and PATTERN.fullmatch(p.name)),
                  key=lambda p:p.stat().st_mtime,reverse=True)


def clean(folder,keep_token=None):
    """Drop expired sessions and strictly bound total bytes and session count."""
    files=_owned_files(folder)
    sessions={}
    for p in files:
        token=p.name.split('_')[1];sessions.setdefault(token,[]).append(p)
    sets=sorted(sessions.items(),key=lambda item:max(p.stat().st_mtime for p in item[1]),reverse=True)
    retained=0;total=0;now=time()
    for token,group in sets:
        size=sum(p.stat().st_size for p in group)
        newest=max(p.stat().st_mtime for p in group)
        keep=(token==keep_token or (now-newest<=MAX_AGE_SECONDS and retained<MAX_SESSIONS and total+size<=MAX_BYTES))
        if keep:
            retained+=1;total+=size
        else:
            for p in group:p.unlink(missing_ok=True)


def publish_native(image,masks,output_directory):
    """Copy bounded inspection-only PNGs; no arbitrary external path or filename accepted."""
    a,m=validate(image,masks)
    if not output_directory:return None
    base=Path(output_directory)
    if base.is_symlink():return None
    root=base.resolve()
    if not root.is_dir():return None
    folder=root/FOLDER
    if folder.is_symlink():return None
    token=uuid.uuid4().hex[:24]
    created=[]
    try:
        folder.mkdir(exist_ok=True)
        if not folder.resolve().is_relative_to(root):return None
        clean(folder)
        refs=[];size=0
        for index in range(len(m)+1):
            # Stream each temporary PNG separately so a 32-mask inspection
            # does not keep 33 decoded 5-Mp images resident at once.
            if index==0:
                label='image'
                pixels=np.rint(np.clip(a[:,:,:3],0,1)*255).astype(np.uint8)
                im=Image.fromarray(pixels,'RGB')
            else:
                label=f'mask{index-1:02d}'
                pixels=np.rint(np.clip(m[index-1],0,1)*255).astype(np.uint8)
                im=Image.fromarray(pixels,'L')
            filename=f'ni_{token}_{label}.png';dest=folder/filename
            if dest.exists() or dest.is_symlink():raise OSError('Unexpected file collision')
            created.append(dest)
            try:
                im.save(dest,format='PNG',optimize=True)
            finally:
                im.close();del pixels
            size+=dest.stat().st_size
            if size>MAX_SESSION_BYTES:raise NativeInspectionError('Aperçu natif trop volumineux : copie annulée')
            refs.append({'filename':filename,'subfolder':FOLDER,'type':'output'})
        clean(folder,keep_token=token)
        return {'image':refs[0],'masks':refs[1:],'largeur_px':int(a.shape[1]),
                'hauteur_px':int(a.shape[0]), 'octets':size}
    except (OSError,ValueError,Image.DecompressionBombError,NativeInspectionError):
        for p in created:p.unlink(missing_ok=True)
        return None
