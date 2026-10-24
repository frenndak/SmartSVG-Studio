"""SmartSVG Studio V9 — print-and-cut first, editable vectors second.

V9 builds on V8, adds globally collision-aware sticker offset, deterministic
cut geometry matched to the actual printed transparency, and operational QA.
The 'editable' SVG is genuine vector color regions, NOT semantic Magic Layers.
"""
from pathlib import Path
import json
import math
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime

import numpy as np
import cv2
from PIL import Image
from . import engine_v8 as base

SVG_NS=base.SVG_NS
INK_NS=base.INK_NS


def _components(mask, min_area=60):
    n, labels, stats, centers=cv2.connectedComponentsWithStats(mask.astype(np.uint8),8)
    return [i for i in range(1,n) if int(stats[i,cv2.CC_STAT_AREA]) >= min_area]


def _silhouette(mask):
    """No transparent interior: Cricut must cut only the outermost outline."""
    mask=np.uint8(mask>127)*255
    cs,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    out=np.zeros_like(mask)
    for c in cs:
        if cv2.contourArea(c)>8:
            cv2.drawContours(out,[c],-1,255,-1)
    return out


def _recover_components(mask, cw, ch):
    """Try the smallest closure that restores a single sticker island.

    We do NOT use convex hull; that would destroy the snail's shape.
    """
    cur=_silhouette(mask)
    if len(_components(cur)) == 1:return cur,0
    for r in (2,3,4,6,8,11):
        ker=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1))
        trial=_silhouette(cv2.morphologyEx(cur,cv2.MORPH_CLOSE,ker))
        if len(_components(trial)) == 1:
            return trial,r
    return cur,-1


def _make_contours_svg(mask, sheet_width_mm, min_area=50):
    """One closed path per printed alpha island, no hidden holes / rasters.

    Using *linear* simplified segments avoids the invisible Catmull-Rom
    overshoot that could misalign standalone SVG cuts with PNG transparency.
    """
    h,w=mask.shape
    root=ET.Element(f'{{{SVG_NS}}}svg',{
      'width':f'{sheet_width_mm:.2f}mm','height':f'{sheet_width_mm*h/w:.2f}mm',
      'viewBox':f'0 0 {w} {h}','version':'1.1'})
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contours=[c for c in contours if cv2.contourArea(c)>=min_area]
    contours=sorted(contours,key=lambda c:(cv2.boundingRect(c)[1],cv2.boundingRect(c)[0]))
    counts=[]
    for i,c in enumerate(contours,1):
        p=cv2.approxPolyDP(c,.70,True).reshape(-1,2)
        if len(p)<3:continue
        d='M'+' L'.join(f'{x},{y}' for x,y in p)+' Z'
        ET.SubElement(root,f'{{{SVG_NS}}}path',{
           'id':f'contour_{i:02d}','d':d,'fill':'#000000',
           f'{{{INK_NS}}}label':f'Contour autocollant {i:02d}'})
        counts.append(len(p))
    return ET.tostring(root,encoding='unicode'),counts


def _actual_sticker_masks(folder, report, image_shape):
    """Rebuild sheet from the per-item masks, retaining original print RGB."""
    h,w=image_shape[:2]
    stickers=[]
    warnings=[]
    for item in report['items']:
        idx=item['index'];x0,y0,x1,y1=item['bbox']
        rgba=np.asarray(Image.open(folder/f'element_{idx:02d}_PRINT.png').convert('RGBA'))
        mask,r=_recover_components(rgba[:,:,3],x1-x0,y1-y0)
        c=len(_components(mask))
        if c!=1:
            warnings.append(f'Sticker {idx:02d}: {c} morceaux distincts; impossible de garantir une seule découpe')
        stickers.append({'index':idx,'bbox':(x0,y0,x1,y1),'rgba':rgba,'mask':mask,'closing_radius':r,'source_components':c})
    return stickers,warnings


def _adaptive_compose(stickers, image_shape, physical_width_mm, preferred_mm):
    h,w=image_shape[:2]
    mm_per_px=physical_width_mm/w
    full=np.zeros((h,w),np.uint8)
    rgb=np.zeros((h,w,3),np.uint8)
    for it in stickers:
        x0,y0,x1,y1=it['bbox'];mask=it['mask']
        target=full[y0:y1,x0:x1]
        target[:]=np.maximum(target,mask)
        art=it['rgba'][:,:,:3]
        target_rgb=rgb[y0:y1,x0:x1]
        target_rgb[mask>0]=art[mask>0]
    # Before any offset, positions MUST be non-overlapping and countable.
    expected=len(stickers)
    base_count=len(_components(full, max(20,round(w*h*.000015))))
    warning=[]
    if base_count!=expected:
        warning.append(f'Avant marge: {base_count} silhouettes pour {expected} dessins ; regroupement par la bordure tente')
    candidates=[float(preferred_mm)]
    val=preferred_mm-.25
    while val>=0:
        candidates.append(round(float(val),2));val-=.25
    if 0.0 not in candidates:candidates.append(0.)
    chosen=None
    for mm in candidates:
        r=round(mm/mm_per_px)
        if r>0:
            kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1))
            cut=cv2.dilate(full,kernel)
        else:
            cut=full.copy()
        if len(_components(cut,max(20,round(w*h*.000015))))==expected:
            chosen=(mm,cut)
            break
    if chosen is None:
        chosen=(preferred_mm,cut)
        warning.append('La marge ne permet pas de retrouver une silhouette par sticker. Vérifier le contrôle visuel.')
    applied,final_mask=chosen
    if base_count!=expected and len(_components(final_mask,max(20,round(w*h*.000015))))==expected:
        warning=[x for x in warning if not x.startswith('Avant marge:')]
    if applied<preferred_mm:
        warning.append(f'Marge réduite automatiquement de {preferred_mm:.2f} à {applied:.2f} mm pour éviter une fusion')
    board=np.zeros((h,w,4),np.uint8)
    board[final_mask>0]=[255,255,255,255]
    board[full>0,:3]=rgb[full>0]
    # Do not lose nontransparent colored pixels in the original (mask is binary).
    board[full>0,3]=255
    return board,final_mask,applied,warning,base_count


def _qa_metrics(mask, expected, width_mm, paths, root_dir):
    h,w=mask.shape
    px_to_mm=width_mm/w
    n, labels, stats, _=cv2.connectedComponentsWithStats(mask,8)
    ids=_components(mask,max(20,round(w*h*.000015)))
    rows=[]
    for j in ids:
        x,y,ww,hh,area=[int(v) for v in stats[j]]
        rows.append({'x':x,'y':y,'largeur_mm':round(ww*px_to_mm,2),
                     'hauteur_mm':round(hh*px_to_mm,2),'surface_mm2':round(area*px_to_mm**2,1)})
    # For each large island, find the nearest other island using a distance transform.
    # For each scan pair, use the distance-to-foreground image, avoids NxM point sets.
    gap_mm=None
    if len(ids)>1:
        min_gap=1e9
        for j in ids:
            target=np.uint8(labels==j)
            # Distance from each other island to current one.
            dist=cv2.distanceTransform(1-target,cv2.DIST_L2,3)
            other=(mask>0)&(labels!=j)
            if np.any(other):
                min_gap=min(min_gap, float(np.min(dist[other])))
        gap_mm=round(min_gap*px_to_mm,2) if min_gap<1e9 else None
    edges=np.concatenate([mask[0],mask[-1],mask[:,0],mask[:,-1]])
    issues=[]
    if len(ids)!=expected:issues.append(f'ECHEC: {len(ids)} silhouettes au lieu de {expected}')
    if np.any(edges):issues.append('Attention: une silhouette touche le bord de la planche')
    if gap_mm is not None and gap_mm<1.0:issues.append(f'Attention: intervalle faible entre stickers ({gap_mm} mm)')
    if any(min(r['largeur_mm'],r['hauteur_mm'])<9 for r in rows):
        issues.append('Attention: sticker de moins de 9 mm sur un axe')
    if paths>5000:issues.append('Attention: SVG editable de plus de 5000 chemins (Cricut)')
    return {'attendus':expected,'contours':len(ids),'chemins_contour':len(ids),'points_contour':paths,
            'espacement_minimum_mm':gap_mm,'bords_touches':bool(np.any(edges)),
            'stickers':rows,'alertes':issues}


def _organize_editable(folder, file_name, suffix, report):
    src=folder/file_name
    if not src.exists():return None
    dest=folder/f'planche_EDITABLE_{suffix}.svg'
    tree=ET.parse(src)
    root=tree.getroot()
    root.set('data-logiciel','SmartSVG V9')
    root.set('data-editabilite','formes couleurs, PAS composants semantiques')
    path_count=0
    for i,group in enumerate([el for el in list(root) if el.tag==f'{{{SVG_NS}}}g'],1):
        index=int(group.get('id','illustration_0').split('_')[-1]) if group.get('id','').startswith('illustration_') else i
        group.set('id',f'STICKER_{index:02d}')
        group.set(f'{{{INK_NS}}}groupmode','layer')
        group.set(f'{{{INK_NS}}}label',f'STICKER {index:02d} — deplacer comme un bloc')
        group.set('data-part','sticker')
        for j,child in enumerate([x for x in list(group) if x.tag==f'{{{SVG_NS}}}g'],1):
            if 'fond_blanc' in child.get('id',''):
                child.set('id',f'STICKER_{index:02d}_FOND');child.set(f'{{{INK_NS}}}label','Base blanche')
            else:
                child.set('id',f'STICKER_{index:02d}_COULEUR_{j:02d}')
                child.set(f'{{{INK_NS}}}label',f'Couleur {j:02d} — zones editables')
            for k,sub in enumerate([x for x in list(child) if x.tag==f'{{{SVG_NS}}}path'],1):
                path_count+=1
                sub.set('id',f'S{index:02d}_C{j:02d}_R{k:03d}')
    tree.write(dest,encoding='utf-8',xml_declaration=True)
    return {'fichier':dest.name,'chemins':path_count,'groupes_stickers':len(report['items'])}


def _save_review(folder, rgb, mask):
    h,w=mask.shape
    base_img=np.full((h,w,3),238,np.uint8)
    alpha=mask.astype(np.float32)/255.
    raw=np.asarray(Image.open(folder/'planche_IMPRIMER_DECOUPER.png').convert('RGBA'))
    base_img=np.uint8(np.clip(base_img*(1-alpha[:,:,None])+raw[:,:,:3]*alpha[:,:,None],0,255))
    cs,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(base_img,cs,-1,(230,30,65),2)
    Image.fromarray(base_img,'RGB').save(folder/'planche_CONTROLE_CONTOURS.png')


def process_v9(rgb, output_dir, *, layout='auto',intent='auto',ia_mode='auto',ai_masker=None,
               alpha=None,sheet_width_mm=180,margin_mm=1.5,editable_colors=10,
               collision_safety=True):
    report,contact=base.process_v8(rgb,output_dir,layout=layout,intent=intent,
            ia_mode=ia_mode,ai_masker=ai_masker,alpha=alpha,sheet_width_mm=sheet_width_mm,
            margin_mm=margin_mm,editable_colors=editable_colors)
    folder=Path(report['output'])
    stickers,mask_warnings=_actual_sticker_masks(folder,report,rgb.shape)
    if collision_safety:
        board,cut,applied,margin_warnings,base_count=_adaptive_compose(
             stickers,rgb.shape,sheet_width_mm,margin_mm)
    else:
        board=np.asarray(Image.open(folder/'planche_IMPRIMER_DECOUPER.png').convert('RGBA'))
        cut=_silhouette(board[:,:,3]);applied=margin_mm;margin_warnings=[];base_count=None
    Image.fromarray(board,'RGBA').save(folder/'planche_IMPRIMER_DECOUPER.png')
    shutil.copyfile(folder/'planche_IMPRIMER_DECOUPER.png',folder/'IMPORT_CRICUT_IMPRIMER_DECOUPER.png')
    svg,vertices=_make_contours_svg(cut,sheet_width_mm)
    (folder/'planche_CONTOURS.svg').write_text(svg,encoding='utf-8')
    (folder/'planche_CONTOURS_12.svg').write_text(svg,encoding='utf-8')
    _save_review(folder,rgb,cut)
    edit1=_organize_editable(folder,'planche_VECTORIEL_SIMPLIFIE.svg','SIMPLIFIE',report)
    edit2=_organize_editable(folder,'planche_VECTORIEL_DETAILLE.svg','DETAILLE',report)
    editable_paths=(edit1['chemins'] if edit1 else 0)
    q=_qa_metrics(cut,len(stickers),sheet_width_mm,editable_paths,folder)
    q['marge_demandee_mm']=margin_mm;q['marge_appliquee_mm']=applied
    q['silhouettes_avant_marge']=base_count
    q['raccords_morphologiques_par_sticker']={str(it['index']):it['closing_radius'] for it in stickers}
    q['alertes'] += mask_warnings + margin_warnings
    report['version']='9.0-beta'
    report['print_then_cut']={'fichier':'IMPORT_CRICUT_IMPRIMER_DECOUPER.png',
               'un_seul_import':True,'nb_stickers':len(stickers),
               'impression':'Depuis Design Space uniquement (repères machine automatiques)'}
    report['svg_editables']={'simplifie':edit1,'detaille':edit2,
              'limite':'Groupe par dessin et par couleur. Pas une IA de calques semantiques equivalent a Canva Magic Layers.'}
    report['qa_v9']=q
    report['alerts']=q['alertes']
    report['ia_locale']={'mode':ia_mode,'choix_par_sticker':[
       {'sticker':i['index'],'statut':i['mask_used'],'explication':i['mask_reason'],
        'inference':i['ai_status']} for i in report['items']]}
    report['recommendation']='Importe IMPORT_CRICUT_IMPRIMER_DECOUPER.png. Pour editabilité, utilise planche_EDITABLE_SIMPLIFIE.svg.'
    (folder/'rapport_V9.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    txt=f'''SMARTSVG STUDIO V9 - GUIDE EXPRESS\n\nRESULTAT PRINCIPAL : IMPORT_CRICUT_IMPRIMER_DECOUPER.png\nNombre de stickers : {len(stickers)}\nContours effectifs : {q['contours']}\nMarge: demande {margin_mm:.2f} mm / utilisee {applied:.2f} mm\n\n1. Design Space > Televerser > PNG > Imprimer puis decouper.\n2. Controle les contours d'abord dans planche_CONTROLE_CONTOURS.png.\n3. Choisis tes dimensions dans Design Space. Imprime DEPUIS Design Space, jamais ce PNG directement depuis Windows.\n4. Ne superpose pas planche_CONTOURS.svg au PNG : contour doublé.\n5. Pour recolorer ou deplacer des vecteurs : planche_EDITABLE_SIMPLIFIE.svg, puis Aplatir avant l'impression.\n   Chaque sticker est un groupe avec de vrais chemins de couleur. Il ne s'agit PAS de calques semantiques.\n6. La precision finale necessite calibration de la Cricut et essai de decoupe.\n\nCONTROLE QUALITE : {q['contours']}/{len(stickers)}\n''' + '\n'.join('! '+x for x in q['alertes'])
    (folder/'LISEZ_MOI_CRICUT_V9.txt').write_text(txt,encoding='utf-8')
    return report,Image.open(folder/'planche_CONTROLE_CONTOURS.png').convert('RGB')
