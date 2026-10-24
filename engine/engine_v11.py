"""SmartSVG Studio V11: per-sticker, fail-closed Print Then Cut geometry.

The editable SVG is only grouped by colors, not semantic parts. Every printed
opaque island is computed from the same exact mask as its standalone cut path.
No remote inference is performed here. RMBG is provided by the ComfyUI node.
"""
import json
import math
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import cv2
from PIL import Image
from . import engine_v9 as previous

SVG_NS = previous.SVG_NS
INK_NS = previous.INK_NS


class UnsafeCut(ValueError):
    """A file cannot be confidently interpreted as one contour per sticker."""


def _components(mask, minimum=1):
    n, labels, stats, _ = cv2.connectedComponentsWithStats(np.uint8(mask > 0), 8)
    ids = [j for j in range(1, n) if int(stats[j, cv2.CC_STAT_AREA]) >= minimum]
    return labels, stats, ids


def _prepare_mask(alpha, index):
    fg = np.uint8(alpha >= 127) * 255
    if not fg.any():
        raise UnsafeCut(f'Sticker {index:02d} vide : aucun contour exploitable')
    # Very small components are noise; report their removal rather than hiding it.
    noise_limit = max(3, int(fg.size * .000025))
    labels, stats, ids = _components(fg, 1)
    noise_pixels = int(sum(stats[j, cv2.CC_STAT_AREA] for j in ids
                           if stats[j, cv2.CC_STAT_AREA] < noise_limit))
    clean = np.zeros_like(fg)
    for j in ids:
        if stats[j, cv2.CC_STAT_AREA] >= noise_limit:
            clean[labels == j] = 255
    # Make internal transparent gaps opaque: only the OUTER contour is cut.
    clean = previous._silhouette(clean)
    # Morphology can connect tiny separated bits, but do not force far apart
    # subjects together with a convex hull. Disconnected = review required.
    close_radius = 0
    for radius in (0, 1, 2, 3, 4, 6, 8, 11):
        candidate = clean if radius == 0 else previous._silhouette(cv2.morphologyEx(
            clean, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                                            (2*radius+1, 2*radius+1))))
        _, _, kept = _components(candidate, 1)
        if len(kept) == 1:
            close_radius = radius
            clean = candidate
            break
    else:
        raise UnsafeCut(f'Sticker {index:02d}: {len(_components(clean,1)[2])} ilots non raccordables '
                        'sans inventer des ponts larges; impression bloquee pour eviter '
                        'plusieurs decoupes non souhaitees')
    # Report exactly how much the final cut geometry differs from the supplied
    # alpha silhouette. Large changes may mean loss of detached eyes/antennae.
    removed=int(np.count_nonzero((fg>0) & (clean==0)))
    added=int(np.count_nonzero((fg==0) & (clean>0)))
    area=int(np.count_nonzero(fg))
    lost_pct=100*removed/max(1,area)
    filled_pct=100*added/max(1,area)
    # Filling an interior hole is intentional (one OUTER Cricut contour),
    # but silently REMOVING visible artwork is not.
    if lost_pct>3.0:
        raise UnsafeCut(f'Sticker {index:02d}: perte du sujet de '
                        f'{lost_pct:.2f}% (seuil 3%).')
    return clean, {'sticker': index, 'micro_pixels_supprimes': noise_pixels,
                   'raccord_px': close_radius, 'pixels_opaques': int((clean > 0).sum()),
                   'perte_sujet_pct':round(lost_pct,3),
                   'trous_et_ponts_ajoutes_pct':round(filled_pct,3)}


def _load_items(folder, report, original_shape):
    h, w = original_shape[:2]
    items = []
    for row in report['items']:
        index = int(row['index'])
        x0, y0, x1, y1 = map(int, row['bbox'])
        if not (0 <= x0 < x1 <= w and 0 <= y0 < y1 <= h):
            raise UnsafeCut(f'Sticker {index:02d}: recadrage hors image')
        art_path = folder / f'element_{index:02d}_PRINT.png'
        if not art_path.is_file():
            raise UnsafeCut(f'Sticker {index:02d}: image source manquante')
        rgba = np.asarray(Image.open(art_path).convert('RGBA'))
        if rgba.shape[:2] != (y1-y0, x1-x0):
            raise UnsafeCut(f'Sticker {index:02d}: masque et recadrage incoherents')
        fg, stats = _prepare_mask(rgba[...,3], index)
        items.append({'idx': index, 'box': (x0,y0,x1,y1), 'rgb':rgba[...,:3], 'original_alpha':rgba[...,3],
                      'fg':fg, 'stats':stats})
    if not items:
        raise UnsafeCut('Aucun element reconnu')
    if len(items) != len({i['idx'] for i in items}):
        raise UnsafeCut('Identifiants sticker dupliques')
    return items


def _place_item_mask(owner, mask, x, y, idx, radius):
    h,w = owner.shape
    sh,sw = mask.shape
    # ROI dilation with r px of transparent padding around the original mask.
    rx0=max(0,x-radius); ry0=max(0,y-radius)
    rx1=min(w,x+sw+radius); ry1=min(h,y+sh+radius)
    roi = np.zeros((ry1-ry0,rx1-rx0), np.uint8)
    oy=y-ry0; ox=x-rx0
    roi[oy:oy+sh,ox:ox+sw] = mask
    if radius:
        kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(radius*2+1, radius*2+1))
        roi=cv2.dilate(roi,kernel)
    target=owner[ry0:ry1,rx0:rx1]
    overlap=(roi>0)&(target!=0)&(target!=idx)
    if np.any(overlap):
        return int(np.count_nonzero(overlap))
    target[roi>0]=idx
    return 0


def _candidate(items, shape, pad, radius):
    h,w=shape[:2];pl,pt,pr,pb=pad
    owner=np.zeros((h+pt+pb,w+pl+pr), np.uint16)
    for it in items:
        x0,y0,_,_=it['box']
        over=_place_item_mask(owner,it['fg'], x0+pl, y0+pt, it['idx'],radius)
        if over:
            return None, (it['idx'],over)
    # Guard against silently losing image at page boundaries.
    if np.any(owner[0]) or np.any(owner[-1]) or np.any(owner[:,0]) or np.any(owner[:,-1]):
        return None, ('bord', 1)
    # Different owners may touch diagonally even without overlapping pixels.
    # Cricut treats them as a connected alpha island, so require separation.
    if len(_components(np.uint8(owner>0),1)[2]) != len(items):
        return None, ('contours_adjacent', 1)
    for it in items:
        _, _, ids = _components(np.uint8(owner==it['idx']), 1)
        if len(ids)!=1:
            return None, (it['idx'],len(ids))
    return owner, None


def _compose(items, shape, width_mm, preferred_mm, pad_if_needed=True):
    h,w=shape[:2]
    if not (w>0 and h>0 and 30<=width_mm<=290 and 0<=preferred_mm<=6):
        raise ValueError('Dimensions / marge demandees invalides')
    px_mm=width_mm/w
    maxr=int(math.floor(preferred_mm / px_mm + 1e-9))
    pad = [0,0,0,0]  # left, top, right, bottom
    if pad_if_needed:
        for it in items:
            x0,y0,x1,y1=it['box']
            yy,xx=np.nonzero(it['fg'])
            if not len(xx):continue
            # Add *only* the missing pixels to preserve physical size.
            pad[0]=max(pad[0],max(0,maxr+2-(x0+int(xx.min()))))
            pad[1]=max(pad[1],max(0,maxr+2-(y0+int(yy.min()))))
            pad[2]=max(pad[2],max(0,maxr+2-(w-1-(x0+int(xx.max())))))
            pad[3]=max(pad[3],max(0,maxr+2-(h-1-(y0+int(yy.max())))))
    # Prefer exact mm values quantized to the nearest pixel, no arbitrary
    # pretended precision below native pixel resolution.
    candidates=[]
    for r in range(maxr,-1,-1):
        owner,reason=_candidate(items,shape,pad,r)
        if owner is not None:
            candidates.append((r,owner))
            break
    if not candidates:
        raise UnsafeCut('Impossible d obtenir exactement une silhouette independante par sticker, '
                        'meme avec une marge nulle. Images superposees ou masques incompatibles.')
    radius,owner=candidates[0]
    H,W=owner.shape
    board=np.zeros((H,W,4),np.uint8)
    board[owner>0]=[255,255,255,255]
    for it in items:
        x0,y0,x1,y1=it['box'];pl,pt=pad[:2]; x=x0+pl;y=y0+pt
        roi=board[y:y+(y1-y0), x:x+(x1-x0)]
        fg=it['fg']>0
        # The closing/filling mask may include formerly transparent pixels.
        # Preserve the white base there, not their arbitrary hidden RGB values.
        original_fg=fg & (it['original_alpha']>=127)
        roi[original_fg,:3]=it['rgb'][original_fg]
        roi[fg,3]=255
    if not np.array_equal(np.uint8(board[...,3]>0),np.uint8(owner>0)):
        raise UnsafeCut('Erreur interne: divergence entre image imprimee et masque de decoupe')
    width_eff=W*px_mm; height_eff=H*px_mm
    return board, owner, radius*px_mm, tuple(pad), width_eff, height_eff


def _verify_and_write(folder, report, board, owner, width_mm, preferred_mm, margin, pad,
                      original_shape, items):
    H,W=owner.shape; expected=len(items)
    # Strict one-to-one validation. Never accept a count-only coincidence.
    actual_ids=np.unique(owner[owner>0])
    if len(actual_ids)!=expected or set(map(int,actual_ids)) != {it['idx'] for it in items}:
        raise UnsafeCut('QA: les contours ne correspondent pas un a un aux illustrations')
    for it in items:
        _,_,conn=_components(np.uint8(owner==it['idx']),1)
        if len(conn)!=1:
            raise UnsafeCut(f'QA: sticker {it["idx"]:02d} a {len(conn)} silhouettes')
    if not np.array_equal((board[...,3]>0),(owner>0)):
        raise UnsafeCut('QA: le masque du PNG et celui des contours ne correspondent pas')
    # Produce one cut path per sticker, with exactly matched placement.
    root=ET.Element(f'{{{SVG_NS}}}svg',{'version':'1.1',
        'width':f'{width_mm:.4f}mm','height':f'{width_mm*H/W:.4f}mm',
        'viewBox':f'0 0 {W} {H}'})
    outline_count=0;vertices=0;error_px=0.0
    for it in sorted(items,key=lambda o:o['idx']):
        fg=np.uint8(owner==it['idx'])*255
        cs,_=cv2.findContours(fg,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        if len(cs)!=1:
            raise UnsafeCut(f'QA contours: sticker {it["idx"]:02d} genere {len(cs)} chemins')
        contour=cs[0]
        # Validate the ACTUAL rasterization, not only the number of SVG paths.
        # If an approximation changes more than 0.5% of mask area, tighten it.
        best=None
        area=max(1,int(np.count_nonzero(fg)))
        for tolerance in (0.60,0.42,0.25,0.10,0.0):
            approx=cv2.approxPolyDP(contour,tolerance,True).reshape(-1,2)
            if len(approx)<3:continue
            simulated=np.zeros_like(fg)
            cv2.drawContours(simulated,[approx.reshape(-1,1,2)],-1,255,-1)
            mismatch=int(np.count_nonzero(simulated!=fg))
            if best is None or mismatch<best[0]:best=(mismatch,approx,tolerance)
            if mismatch/area<=0.005:break
        if best is None:
            raise UnsafeCut(f'Contour insuffisant: sticker {it["idx"]:02d}')
        mismatch,approx,chosen_tolerance=best
        mismatch_pct=100*mismatch/area
        if mismatch_pct>1.0:
            raise UnsafeCut(f'QA SVG: silhouette {it["idx"]:02d} differe de '
                            f'{mismatch_pct:.2f}% du masque imprimable')
        d='M'+' L'.join(f'{int(x)},{int(y)}' for x,y in approx)+' Z'
        ET.SubElement(root,f'{{{SVG_NS}}}path',{'id':f'CUT_{it["idx"]:02d}', 'd':d,
                     'fill':'#000000','data-usage':'decoupe-seule'})
        outline_count+=1;vertices+=len(approx)
        it['stats']['tolerance_contour_px']=chosen_tolerance
        it['stats']['difference_raster_contour_pct']=round(mismatch_pct,3)
    if outline_count!=expected:
        raise UnsafeCut('QA: nombre de chemins de decoupe incorrect')
    # Save SVG and PNG atomically so a crash cannot leave half-written files.
    tmp_svg=folder/'_smartsvg_v11_temp.svg';tmp_png=folder/'_smartsvg_v11_temp.png'
    ET.ElementTree(root).write(tmp_svg,encoding='utf-8',xml_declaration=True)
    # Embed an explicit nominal DPI. Cricut may still require verifying size
    # on canvas; the physical size is also recorded in the QA manifest.
    dpi=W/width_mm*25.4
    Image.fromarray(board,'RGBA').save(tmp_png,format='PNG',dpi=(dpi,dpi))
    ET.parse(tmp_svg)
    with Image.open(tmp_png) as check:
        if check.size!=(W,H):raise UnsafeCut('QA: taille PNG sortie incorrecte')
    os.replace(tmp_svg,folder/'planche_CONTOURS.svg')
    os.replace(tmp_png,folder/'IMPORT_CRICUT_IMPRIMER_DECOUPER.png')
    # Retire any older V9 aliases instead of leaving inconsistent cut PNG/SVG.
    import shutil
    shutil.copy2(folder/'IMPORT_CRICUT_IMPRIMER_DECOUPER.png',folder/'planche_IMPRIMER_DECOUPER.png')
    shutil.copy2(folder/'planche_CONTOURS.svg',folder/'planche_CONTOURS_12.svg')
    # Make preview from the same mask and art, never a different smoothing.
    preview=np.full((H,W,3),239,np.uint8)
    preview[owner>0]=board[owner>0,:3]
    for it in items:
        fg=np.uint8(owner==it['idx'])*255
        cs,_=cv2.findContours(fg,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(preview,cs,-1,(220,20,75),2)
    Image.fromarray(preview,'RGB').save(folder/'planche_CONTROLE_CONTOURS.png')
    # Adjust editable group translations and physical dimensions if we expanded canvas.
    for filename in ('planche_EDITABLE_SIMPLIFIE.svg','planche_EDITABLE_DETAILLE.svg'):
        p=folder/filename
        if not p.is_file():continue
        doc=ET.parse(p); svg=doc.getroot()
        svg.set('viewBox',f'0 0 {W} {H}')
        svg.set('width',f'{width_mm:.4f}mm')
        svg.set('height',f'{width_mm*H/W:.4f}mm')
        if pad[0] or pad[1]:
            for group in list(svg):
                if group.tag!=f'{{{SVG_NS}}}g':continue
                old=group.get('transform','')
                group.set('transform',f'translate({pad[0]},{pad[1]}) '+old)
        doc.write(p,encoding='utf-8',xml_declaration=True)
    # Physical QA
    px_mm=width_mm/W
    img=board
    margin_board=min([int((owner>0).any(axis=0).argmax()),
                      int((owner>0).any(axis=1).argmax()),
                      int(np.argmax((owner>0).any(axis=0)[::-1])),
                      int(np.argmax((owner>0).any(axis=1)[::-1]))])
    gaps=[]
    for it in items:
        target=np.uint8(owner==it['idx'])
        others=(owner>0)&(owner!=it['idx'])
        if np.any(others):
            dist=cv2.distanceTransform(1-target,cv2.DIST_L2,cv2.DIST_MASK_PRECISE)
            gaps.append(float(dist[others].min()))
    gap_mm=(round(min(gaps)*px_mm,3) if gaps else None)
    paths_count=0;vector_errors=[]
    for filename in ('planche_EDITABLE_SIMPLIFIE.svg','planche_EDITABLE_DETAILLE.svg'):
        p=folder/filename
        if not p.exists():continue
        svg=ET.parse(p).getroot()
        paths=list(svg.iter(f'{{{SVG_NS}}}path'))
        groups=[e for e in list(svg) if e.tag==f'{{{SVG_NS}}}g']
        if len(groups)!=expected:vector_errors.append(f'{filename}: {len(groups)} groupes au lieu de {expected}')
        ids=[node.get('id') for node in svg.iter() if node.get('id')]
        if len(ids)!=len(set(ids)):vector_errors.append(f'{filename}: identifiants SVG dupliques')
        if list(svg.iter(f'{{{SVG_NS}}}image')):vector_errors.append(f'{filename}: image matricielle embarquee')
        paths_count=max(paths_count,len(paths))
        if len(paths)>5000:vector_errors.append(f'{filename}: {len(paths)} chemins, plafond Cricut de 5000')
    # A4 on Explore series: guaranteed only against bounding box maximum,
    # not against the full non-rectangular sensor mark geometry.
    physical_height=width_mm*H/W
    fits_rect = ((width_mm<=183.0 and physical_height<=269.8) or
                 (physical_height<=183.0 and width_mm<=269.8))
    warnings=[]
    if not fits_rect:warnings.append('DIMENSIONS: hors de la boite englobante maximale Print Then Cut A4 Explore (18.3 x 26.98 cm)')
    if gap_mm is not None and gap_mm<1.0:warnings.append(f'ESPACEMENT FAIBLE: {gap_mm} mm entre les formes')
    if margin+1e-6 < preferred_mm:
        natural_mm=math.floor(preferred_mm/px_mm+1e-9)*px_mm
        if margin+1e-6 < natural_mm:
            warnings.append(f'MARGE REDUITE pour eviter des collisions: {preferred_mm:.2f} -> {margin:.2f} mm')
        else:
            warnings.append(f'MARGE ARRONDIE a la resolution source: {preferred_mm:.2f} -> {margin:.2f} mm')
    if margin_board < 2:warnings.append('BORD: moins de 2 pixels transparents autour de la planche')
    dpi=W/width_mm*25.4
    if dpi<200:warnings.append(f'IMPRESSION: resolution {dpi:.0f} DPI inferieure a 200 dpi')
    for it in items:
        if it['stats']['raccord_px']>=6:warnings.append(f'Sticker {it["idx"]:02d}: raccord morphologique large ({it["stats"]["raccord_px"]} px), verifier le dessin')
        if it['stats']['difference_raster_contour_pct']>2.0:warnings.append(f'Sticker {it["idx"]:02d}: ecart contour SVG / PNG {it["stats"]["difference_raster_contour_pct"]}%')
    warnings.extend(vector_errors)
    if any(it['stats']['pixels_opaques'] > .96*(it['fg'].size) for it in items):
        warnings.append('FOND SUSPECT: au moins une image est presque totalement opaque. Si le sujet ne remplit pas le cadre, revoir le detourage (ou raccorder le masque PNG).')
    for it in items:
        m=it['fg']>0
        edge=np.concatenate([m[0],m[-1],m[:,0],m[:,-1]])
        if edge.mean()>.09:
            warnings.append(f'Sticker {it["idx"]:02d}: silhouette touche largement le bord du recadrage ; details potentiellement coupes.')
    critical_warnings=[x for x in warnings if not x.startswith('MARGE ARRONDIE')]
    quality={'statut':'VALIDE_GEOMETRIQUEMENT' if not critical_warnings else 'AVERTISSEMENT',
            'dessins':expected,'contours_par_dessin':1, 'contours_total':outline_count,
            'chemins_svg_contour':outline_count, 'points_svg_contour':vertices,
            'marge_demandee_mm':preferred_mm,'marge_retenue_mm':round(margin,3),
            'taille_planche_mm':[round(width_mm,3),round(physical_height,3)],
            'resolution_impression_dpi':round(dpi),
            'espacement_minimum_mm':gap_mm,
            'pad_ajoute_px':list(pad), 'formats_a4_controle_boite_englobante':fits_rect,
            'verification_finale_dans_design_space_requise':True,
            'par_sticker':[it['stats'] for it in items], 'alertes':warnings}
    return quality


def process_v11(rgb,output_dir, *, layout='auto',intent='auto',ia_mode='auto',ai_masker=None,
                alpha=None,sheet_width_mm=180,margin_mm=1.5,editable_colors=10):
    rgb=np.asarray(rgb)
    if rgb.ndim!=3 or rgb.shape[2]!=3:
        raise ValueError('Image attendue : RGB HxWx3')
    if rgb.shape[0]*rgb.shape[1]>16_000_000:
        raise ValueError('Image de plus de 16 megapixels : reduire la resolution pour eviter un epuisement memoire')
    if alpha is None or np.all(np.asarray(alpha)>=250):
        if float(rgb.astype(np.float32).std(axis=(0,1)).max())<1.5:
            raise UnsafeCut('Image presque uniforme, aucun dessin identifiable : conversion refusee.')
    if ia_mode=='forcer' and ai_masker is None:
        raise UnsafeCut('IA forcee mais aucun moteur IA n est raccorde. '
                        'Activer ComfyUI-RMBG ou choisir le mode automatique.')
    # Run the legacy color/vector preparation, then *replace* its cut result with
    # validated per-item non-overlapping cut geometry (not V9's count-only check).
    report,_=previous.process_v9(rgb,output_dir,layout=layout,intent=intent,
        ia_mode=ia_mode,ai_masker=ai_masker,alpha=alpha,sheet_width_mm=sheet_width_mm,
        margin_mm=margin_mm,editable_colors=editable_colors)
    folder=Path(report['output'])
    if ia_mode=='forcer':
        failed=[str(i['index'])+': '+str(i.get('ai_status')) for i in report['items']
                if i.get('mask_used')!='IA_locale']
        if failed:
            # Guard existing intermediate print/cut outputs from being imported.
            for name in ('IMPORT_CRICUT_IMPRIMER_DECOUPER.png',
                         'planche_IMPRIMER_DECOUPER.png','planche_CONTOURS.svg',
                         'planche_CONTOURS_12.svg'):
                p=folder/name
                if p.exists():p.rename(folder/('NON_VALIDE_'+name))
            reason='IA forcee mais masque non utilise pour sticker(s): '+', '.join(failed)
            (folder/'BLOQUE_V11.json').write_text(json.dumps({'statut':'BLOQUE',
                'raison':reason},ensure_ascii=False,indent=2),encoding='utf-8')
            raise UnsafeCut(reason)
    try:
        items=_load_items(folder,report,rgb.shape)
        board,owner,margin,pad,width_eff,height_eff=_compose(items,rgb.shape,sheet_width_mm,margin_mm)
        quality=_verify_and_write(folder,report,board,owner,width_eff,margin_mm,margin,pad,rgb.shape,items)
        report['version']='10.0-beta'
        report['qa_v11']=quality
        report['fichier_a_importer']='IMPORT_CRICUT_IMPRIMER_DECOUPER.png'
        report['limite_IA']='RMBG detoure, ne reconstruit pas les objets en calques semantiques.'
        for it in report['items']:
            if it.get('ai_status','').startswith('echec_IA'):
                quality['alertes'].append(f'Sticker {it["index"]:02d}: erreur inference IA; '
                                         'contour heuristique utilise. Verifier visuellement.')
        if any(not e.startswith('MARGE ARRONDIE') for e in quality['alertes']) and quality['statut']=='VALIDE_GEOMETRIQUEMENT':
            quality['statut']='AVERTISSEMENT'
        report['alerts']=quality['alertes']
        (folder/'rapport_V11.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        msg=(f'SmartSVG Studio V11 — {quality["statut"]}\n'
             f'{len(items)} dessin(s) / {quality["contours_total"]} contour(s) independants\n'
             f'Fichier Cricut : IMPORT_CRICUT_IMPRIMER_DECOUPER.png\n'
             f'Taille physique : {width_eff:.1f} x {height_eff:.1f} mm\n'
             f'Marge appliquee : {margin:.2f} mm\n'
             f'Ne pas ajouter les contours.svg sur le PNG Print Then Cut.\n'
             'Verifier la taille et la preview dans Design Space, puis calibrer / tester la decoupe.\n'
             + '\n'.join('ATTENTION: '+w for w in quality['alertes']) + '\n')
        (folder/'LISEZ_MOI_CRICUT_V11.txt').write_text(msg,encoding='utf-8')
        return report,Image.open(folder/'planche_CONTROLE_CONTOURS.png').convert('RGB')
    except Exception as exc:
        # V9 intermediate output must never look like an approved V11 output.
        obsolete=folder/'IMPORT_CRICUT_IMPRIMER_DECOUPER.png'
        if obsolete.exists(): obsolete.rename(folder/'NE_PAS_IMPORTER_NON_VERIFIE.png')
        for orig,blocked in [('planche_IMPRIMER_DECOUPER.png','NON_VALIDE_planche.png'),
                             ('planche_CONTOURS.svg','NON_VALIDE_contours.svg'),
                             ('planche_CONTOURS_12.svg','NON_VALIDE_contours_legacy.svg')]:
            path=folder/orig
            if path.exists():path.rename(folder/blocked)
        error={'version':'10.0-beta','statut':'BLOQUE','raison':str(exc),
               'sortie':str(folder),'conseil':'Verifier le masque source ou la detection de planche; ne pas imprimer les sorties non verifiees.'}
        (folder/'BLOQUE_V11.json').write_text(json.dumps(error,ensure_ascii=False,indent=2),encoding='utf-8')
        raise UnsafeCut('SmartSVG V11 a bloque un fichier potentiellement mal decoupable. '
                        f'Diagnostic: {exc}. Voir {folder / "BLOQUE_V11.json"}') from exc
