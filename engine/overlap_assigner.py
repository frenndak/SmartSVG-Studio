"""Deterministic mask/path intersection classifier for supported VTracer SVG paths.

Supported absolute SVG commands: M, L, C, Z. Unknown syntax -> residual, never
misclassified. Raster masks are used for classification only: original vector
path data is never rewritten.
"""
import re
import cv2
import numpy as np

TOKENS=re.compile(r'[MmLlCcZz]|[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?')


def _polygons(d):
    tokens=TOKENS.findall(d)
    if not tokens: return None
    # Do not silently parse unsupported Q/A/S/H/V or relative commands.
    command_letters=re.findall(r'[A-Za-z]',d)
    if any(c not in ('M','L','C','Z') for c in command_letters):return None
    polygons=[];current=[];pt=None;start=None;pos=0;mode=None
    while pos<len(tokens):
        t=tokens[pos]
        if t in 'MLCZ' and len(t)==1:
            mode=t;pos+=1
            if mode=='Z':
                if len(current)>=3: polygons.append(np.asarray(current,dtype=np.float32))
                current=[];pt=start;mode=None
            continue
        if mode is None:return None
        n={'M':2,'L':2,'C':6}[mode]
        if pos+n>len(tokens) or any(re.fullmatch('[MLCZ]',x) for x in tokens[pos:pos+n]):return None
        x=list(map(float,tokens[pos:pos+n]));pos+=n
        if mode=='M':
            if current and len(current)>=3:polygons.append(np.asarray(current,dtype=np.float32))
            pt=np.asarray(x,dtype=np.float64);start=pt.copy();current=[pt.copy()];mode='L'
        elif mode=='L':
            if pt is None:return None
            pt=np.asarray(x,dtype=np.float64);current.append(pt.copy())
        elif mode=='C':
            if pt is None:return None
            p0=pt;p1=np.asarray(x[0:2]);p2=np.asarray(x[2:4]);p3=np.asarray(x[4:6])
            approx_len=np.linalg.norm(p1-p0)+np.linalg.norm(p2-p1)+np.linalg.norm(p3-p2)
            steps=max(3,min(48,int(np.ceil(approx_len/1.6))))
            for tval in np.linspace(1.0/steps,1.0,steps):
                q=(1-tval)**3*p0+3*(1-tval)**2*tval*p1+3*(1-tval)*tval*tval*p2+tval**3*p3
                current.append(q)
            pt=p3
    if current and len(current)>=3:polygons.append(np.asarray(current,dtype=np.float32))
    return polygons or None


def path_mask(d,shape,translate=(0,0)):
    """Return a local binary painted silhouette, or None on unsafe SVG syntax."""
    polygons=_polygons(d)
    if not polygons:return None
    h,w=map(int,shape);dx,dy=translate
    result=np.zeros((h,w),dtype=np.uint8)
    points=[]
    for poly in polygons:
        if not np.isfinite(poly).all():return None
        pts=np.rint(poly+np.asarray([dx,dy])).astype(np.int32)
        if pts.shape[0]>=3:points.append(pts)
    if not points:return None
    # cv2.fillPoly handles multi-contour even-odd fills; use one draw call.
    cv2.fillPoly(result,points,color=1,lineType=cv2.LINE_8)
    return result.astype(bool)


def assign_by_overlap(painted,proposals,min_share=.55,min_margin=.15):
    """Classification only when most of a path's *area* lies in one proposal.

    Ambiguous/low coverage paths stay residual. Does not invent probabilities.
    """
    if painted is None:return -1,{'raison':'forme_non_interpretable'}
    total=int(painted.sum())
    if total==0:return -1,{'raison':'forme_vide'}
    if not proposals:return -1,{'raison':'aucun_masque'}
    counts=[int(np.count_nonzero(painted & m)) for m in proposals]
    rankings=sorted(range(len(counts)),key=lambda i:(-counts[i],i))
    best=rankings[0];second=counts[rankings[1]] if len(rankings)>1 else 0
    share=counts[best]/total;margin=(counts[best]-second)/total
    info={'recouvrement_max_pct':round(share*100,2),'ecart_entre_candidats_pct':round(margin*100,2),
          'nb_pixels_chemin':total,'raison':'attribue' if share>=min_share and margin>=min_margin else 'indecidable'}
    return (best if info['raison']=='attribue' else -1),info
