"""Conservative, editable multicolour SVG conversion of *flat* artwork.

This is true vector geometry: one independently addressable <g> per palette
colour, with paths that can be selected/edited in a vector graphics editor.
It is not an image embedded in an SVG, nor semantic object reconstruction.
"""
from __future__ import annotations
import math
from pathlib import Path
import os
import re
import tempfile
import xml.etree.ElementTree as ET
import cv2
import numpy as np
from .palette_v21132 import local_kmeans_palette

MAX_PIXELS = 5_000_000
MAX_VECTOR_PIXELS = 600_000
MAX_PATHS = 1200
MAX_POINTS = 110_000
MAX_BYTES = 5_000_000

class VectorizationRefused(ValueError):
    pass


def _rgba_and_mask(image, mask):
    im=np.asarray(image)
    if im.ndim!=3 or im.shape[-1] not in (3,4) or im.dtype!=np.uint8:
        raise VectorizationRefused('Image RGB/RGBA uint8 attendue')
    h,w=im.shape[:2]
    if not h or not w or h*w>MAX_PIXELS:
        raise VectorizationRefused('Image absente ou plus de 5 mégapixels')
    if mask is None:
        if im.shape[2]==4 and (im[:,:,3]<250).any():
            mask=im[:,:,3]>=128
        else:
            raise VectorizationRefused('Masque nécessaire : la vectorisation des fonds opaques sans sujet n’est pas automatique')
    else:
        mask=np.asarray(mask)
        if mask.ndim!=2 or mask.shape!=(h,w) or mask.dtype.kind not in 'biuf' or not np.isfinite(mask).all():
            raise VectorizationRefused('Masque 2D de dimensions exactes requis')
        if mask.min()<-.001 or mask.max()>1.001:
            raise VectorizationRefused('Masque hors [0,1]')
        mask=mask>=.5
    if mask.mean()<.002 or mask.mean()>.94:
        raise VectorizationRefused('Masque vide ou quasi rectangulaire / couvrant tout le fond')
    return im[:,:,:3],np.uint8(mask)


def vectorize_flat_art(image, mask, *, colors=8, width_mm=40, max_side=900):
    """Return XML SVG and audit of a flat source, no filesystem side effects."""
    if isinstance(colors,bool) or not isinstance(colors,int) or not 2<=colors<=16:
        raise VectorizationRefused('Nombre de couleurs : 2 à 16')
    if isinstance(width_mm,bool) or not isinstance(width_mm,(float,int)) or not math.isfinite(width_mm) or not 5<=width_mm<=300:
        raise VectorizationRefused('Largeur physique : 5 à 300 mm')
    rgb, alpha = _rgba_and_mask(image,mask)
    full_h,full_w=rgb.shape[:2]
    yy,xx=np.nonzero(alpha)
    margin=max(4,round(max(int(xx.max()-xx.min()+1),int(yy.max()-yy.min()+1))*.025))
    crop_x0=max(0,int(xx.min())-margin);crop_x1=min(full_w,int(xx.max())+1+margin)
    crop_y0=max(0,int(yy.min())-margin);crop_y1=min(full_h,int(yy.max())+1+margin)
    rgb=rgb[crop_y0:crop_y1,crop_x0:crop_x1].copy()
    alpha=alpha[crop_y0:crop_y1,crop_x0:crop_x1].copy()
    h0,w0=rgb.shape[:2]
    scale=min(1.,max_side/max(h0,w0),math.sqrt(MAX_VECTOR_PIXELS/(h0*w0)))
    w=max(1,round(w0*scale));h=max(1,round(h0*scale))
    if (h,w)!=(h0,w0):
        rgb=cv2.resize(rgb,(w,h),interpolation=cv2.INTER_AREA)
        alpha=cv2.resize(alpha,(w,h),interpolation=cv2.INTER_NEAREST)
    region=alpha!=0
    pixels=rgb[region]
    if len(pixels)<80:
        raise VectorizationRefused('Trop peu de pixels significatifs')
    # Reject complex photographic sources instead of producing thousands of faux details.
    sample=pixels[::max(1,len(pixels)//35000)]
    diversity=np.unique(sample//16,axis=0).shape[0]
    if diversity>1900:
        raise VectorizationRefused('Image trop photographique pour un SVG de couleurs propres ; conserver le PNG Print Then Cut')
    if np.std(pixels.astype(np.float32),axis=0).max()<4:
        raise VectorizationRefused('Image pratiquement monochrome : utiliser un SVG de contour')
    # Deterministic k-means: subset for palette, then assign all pixels.
    subsample=sample[:30000].astype(np.float32)
    k=min(colors,len(np.unique(subsample.astype(np.uint8),axis=0)))
    if k<2:raise VectorizationRefused('Palette insuffisante')
    palette=local_kmeans_palette(subsample,k)
    # A small palette keeps the vector shapes inspectable; cluster assignment in chunks.
    label=np.full((h,w),-1,dtype=np.int16)
    px=pixels.astype(np.int16)
    cent=palette.astype(np.int16)
    classes=np.empty(len(px),dtype=np.int16)
    for start in range(0,len(px),16384):
        delta=px[start:start+16384,None,:].astype(np.int32)-cent[None,:,:].astype(np.int32)
        classes[start:start+16384]=np.argmin(np.sum(delta*delta,axis=2),axis=1)
    label[region]=classes
    # Stable palette order = luminance, useful for manual editing.
    order=sorted(range(k),key=lambda j:float(palette[j]@[.2126,.7152,.0722]))
    root=ET.Element('svg',{'xmlns':'http://www.w3.org/2000/svg','width':f'{float(width_mm):g}mm',
        'height':f'{float(width_mm)*h/w:.5f}mm','viewBox':f'0 0 {w} {h}',
        'version':'1.1'})
    ET.SubElement(root,'title').text='SmartSVG V21.13 — Couleurs vectorielles modifiables'
    description=ET.SubElement(root,'desc');description.text='SVG multicouche expérimental. Pas un fichier de Print Then Cut certifié. Éditer dans Inkscape avant découpe.'
    paths_total=0;points_total=0;colors_written=0;omitted=0
    for j in order:
        binary=np.uint8(label==j)*255
        # Small islands and holes remain geometry; no upscaling details invented.
        contours,hierarchy=cv2.findContours(binary,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
        if not contours:continue
        shapes=[]
        if hierarchy is None:continue
        H=hierarchy[0]
        for i,curve in enumerate(contours):
            if H[i][3]!=-1:continue
            if cv2.contourArea(curve)<5:omitted+=1;continue
            family=[curve]
            sub=int(H[i][2])
            while sub>=0:
                if cv2.contourArea(contours[sub])>=3: family.append(contours[sub])
                sub=int(H[sub][0])
            strokes=[]
            for part in family:
                arc=max(0.28,cv2.arcLength(part,True)*.0008)
                simplified=cv2.approxPolyDP(part,arc,True).reshape(-1,2)
                if len(simplified)<3:continue
                strokes.append('M '+' L '.join(f'{int(x)},{int(y)}' for x,y in simplified)+' Z')
                points_total+=len(simplified)
            if strokes:shapes.append(' '.join(strokes));paths_total+=1
            if paths_total>MAX_PATHS or points_total>MAX_POINTS:
                raise VectorizationRefused('Géométrie trop complexe : augmenter la simplification ou utiliser le PNG')
        if shapes:
            g=ET.SubElement(root,'g',{'id':f'couleur_{j+1:02d}','data-smartsvg-layer':'color',
                'fill':'#%02x%02x%02x'%tuple(map(int,palette[j])),'fill-rule':'evenodd'})
            for d in shapes:ET.SubElement(g,'path',{'d':d})
            colors_written+=1
    if colors_written<2 or not paths_total:
        raise VectorizationRefused('Trop peu de régions distinctes conservées')
    payload=ET.tostring(root,encoding='utf-8',xml_declaration=True)
    if len(payload)>MAX_BYTES:raise VectorizationRefused('SVG généré trop volumineux')
    preview=np.full((h,w,3),255,np.uint8)
    preview[region]=palette[label[region]]
    audit={'version':'21.13','usage':'SVG_MULTICOUCHE_EDITABLE_EXPERIMENTAL',
        'imprimable_identique_original':False,'qualite_semantique_certifiee':False,
        'svg_decoupe_cricut_certifie':False,'taille_originale':[full_w,full_h],'zone_sujet_originale':[crop_x0,crop_y0,crop_x1,crop_y1],
        'taille_travail':[w,h],'largeur_mm':float(width_mm),
        'calques_couleur':colors_written,'formes':paths_total,'points':points_total,
        'petites_formes_omises':omitted,'couleurs_demandees':colors,
        'differents_blocs_couleur_echantillon':int(diversity),
        'verification_visuelle_requise':True}
    return payload,preview,audit


def save_svg(svg, folder='', prefix='smartsvg_couleurs'):
    if not isinstance(svg,bytes) or not svg.startswith(b'<?xml'):raise ValueError('SVG XML attendu')
    if folder:
        path=Path(folder).expanduser()
        if not path.is_absolute():raise ValueError('Un dossier de sortie absolu est requis')
        if path.exists() and (path.is_symlink() or not path.is_dir()):raise ValueError('Dossier non sûr')
        path.mkdir(parents=True,exist_ok=True)
    else:
        try:
            import folder_paths
            path=Path(folder_paths.get_output_directory())/'SmartSVG_Studio'/'SVG_Multicouche'
            path.mkdir(parents=True,exist_ok=True)
        except ImportError:
            path=Path(tempfile.mkdtemp(prefix='smartsvg_multicouche_'))
    if not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}',prefix):raise ValueError('Nom SVG non sûr')
    for ix in range(1,1000):
        dest=path/f'{prefix}_{ix:03d}.svg'
        try: fd=os.open(dest,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        except FileExistsError:continue
        with os.fdopen(fd,'wb') as output:
            output.write(svg);output.flush();os.fsync(output.fileno())
        return str(dest)
    raise ValueError('Trop de versions dans le dossier de sortie')
