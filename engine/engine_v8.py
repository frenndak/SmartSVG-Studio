"""SmartSVG Studio V8: quality-gated assets for ComfyUI / Cricut.

Preserves V7's deterministic foreground reconstruction and dynamic RMBG interface,
then adds a simplified *true-vector* editable SVG, explicit layer IDs,
print/cut quality metrics, and a consolidated user-facing manifest.
"""
import json
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import cv2
from PIL import Image

from . import engine_legacy as core

SVG_NS = core.SVG_NS
INK_NS = "http://www.inkscape.org/namespaces/inkscape"
# Official Inkscape namespace (without 'www'):
INK_NS = "http://www.inkscape.org/namespaces/inkscape"
ET.register_namespace('inkscape', INK_NS)


def _annotate_svg(path):
    """Names every editable color path, preserving curves, fill and grouping."""
    root=ET.parse(path)
    total=0
    for group in root.getroot().iter(f'{{{SVG_NS}}}g'):
        gid=group.get('id','groupe')
        group.set(f'{{{INK_NS}}}label',gid.replace('_',' '))
        k=0
        for child in group:
            if child.tag==f'{{{SVG_NS}}}path':
                k+=1
                child.set('id', f'{gid}_zone_{k:03d}')
                child.set('data-kind','zone-de-couleur')
                total+=1
    root.write(path,encoding='utf-8',xml_declaration=True)
    return total


def _simplified_layer_svg(report, source, root_dir, n_colors=10):
    """One editable color-layered SVG artboard; each person stays an SVG group.

    Note: these groups are not semantic reconstruction of the depicted objects.
    """
    h,w=source.shape[:2]
    board=ET.Element(f'{{{SVG_NS}}}svg',{'width':f"{report['sheet']['sheet_width_mm']:.2f}mm",
                'height':f"{report['sheet']['sheet_height_mm']:.2f}mm",'viewBox':f'0 0 {w} {h}','version':'1.1'})
    metrics={'paths':0,'regions_filtered':0,'palette_per_element':n_colors,'characters':len(report['items'])}
    for item in report['items']:
        idx=item['index']
        x0,y0,x1,y1=item['bbox']
        art=np.asarray(Image.open(root_dir/f'element_{idx:02d}_PRINT.png').convert('RGBA'))
        rgb=art[:,:,:3]
        mask=art[:,:,3]
        # Intent-dependent adjustment: pictograms use few colors, illustrations more.
        classification=item['classification']
        colors=(max(3,n_colors//2) if classification in ('logo','silhouette') else
                n_colors if classification=='cartoon' else min(n_colors+4,24))
        svg,stats=core.vector_layers(rgb,mask,report['sheet']['sheet_width_mm']*(x1-x0)/w,
                        colors, min_detail_mm=.85,clean=True)
        node=ET.fromstring(svg)
        obj=ET.SubElement(board,f'{{{SVG_NS}}}g',{'id':f'illustration_{idx:02d}',
                f'{{{INK_NS}}}label':f'Illustration {idx:02d}',
                'transform':f'translate({x0},{y0})','data-type':'sticker'})
        for palette_group in list(node):
            palette_group.set('id', f'illustration_{idx:02d}_{palette_group.get("id", "couleur")}')
            obj.append(palette_group)
        metrics['paths']+=stats['paths']
        metrics['regions_filtered']+=stats['small_shapes_filtered']
    destination=root_dir/'planche_VECTORIEL_SIMPLIFIE.svg'
    ET.ElementTree(board).write(destination,encoding='utf-8',xml_declaration=True)
    _annotate_svg(destination)
    return destination.name,metrics


def _analyze_cut_sheet(path,expected, physical_width_mm):
    img=np.asarray(Image.open(path).convert('RGBA'))
    alpha=(img[:,:,3]>127).astype(np.uint8)*255
    n,lab,stats,centers=cv2.connectedComponentsWithStats(alpha,8)
    area_limit=max(20,int(alpha.size*.000025))
    blobs=[]
    for i in range(1,n):
        area=int(stats[i,cv2.CC_STAT_AREA])
        if area<area_limit: continue
        x,y,w,h=[int(v) for v in stats[i,:4]]
        blobs.append({'bbox_px':[x,y,w,h],'area_px':area,'width_mm':round(w*physical_width_mm/alpha.shape[1],2),
                      'height_mm':round(h*physical_width_mm/alpha.shape[1],2)})
    contours,_=cv2.findContours(alpha,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    holes,_=cv2.findContours(alpha,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    # enclosed transparent holes create unwanted cut lines in some import modes
    _,hier=cv2.findContours(alpha,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    internal=0
    if hier is not None:
        internal=sum(int(h[3]>=0) for h in hier[0])
    issues=[]
    if len(blobs)!=expected:
        issues.append(f'{len(blobs)} silhouettes significatives contre {expected} dessins : risque de decoupe multiple ou de fusion')
    if internal:
        issues.append(f'{internal} cavite(s) transparentes detectees : verifier les decoupes internes')
    if any(x['width_mm']<9 or x['height_mm']<9 for x in blobs):
        issues.append('Certains stickers mesurent moins de 9 mm dans une dimension : test de decoupe necessaire')
    # Transparent sheet border, otherwise Cricut would likely cut a rectangle.
    edges=np.concatenate([alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]])
    if np.any(edges>0):
        issues.append('Le dessin touche le bord du canevas : risque de contours coupes')
    return {'elements_attendus':expected,'silhouettes_distinctes':len(blobs),
            'trous_transparents':internal,'elements':blobs,'alertes':issues,
            'resolution_px':[int(img.shape[1]),int(img.shape[0])]}


def _add_white_bases(svg_path, report, output):
    """A solid vector ground below reduced palette regions fills anti-alias gaps.
    Every base is itself an editable path, never a bitmap. White is appropriate
    to sticker paper, not to transparent fabrication layers.
    """
    doc=ET.parse(svg_path)
    root=doc.getroot()
    made=0
    for item in report['items']:
        idx=item['index']
        group=root.find(f"./{{{SVG_NS}}}g[@id='illustration_{idx:02d}']")
        if group is None:continue
        arr=np.asarray(Image.open(output/f'element_{idx:02d}_PRINT.png').convert('RGBA'))
        mask=np.uint8(arr[:,:,3]>127)*255
        contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        base=ET.Element(f'{{{SVG_NS}}}g',{'id':f'illustration_{idx:02d}_fond_blanc',
                  f'{{{INK_NS}}}label':'Fond blanc vectoriel - modifiable',
                  'fill':'#ffffff','data-type':'fond-vectoriel'})
        for cnt in contours:
            if cv2.contourArea(cnt)<20:continue
            p,_=core.contour_path(cnt,max(.7,arr.shape[1]*.0035))
            if p:
                ET.SubElement(base,f'{{{SVG_NS}}}path',{'d':p})
                made+=1
        group.insert(0,base)
    doc.write(svg_path,encoding='utf-8',xml_declaration=True)
    return made


def _seal_internal_holes(folder, width_mm):
    """Print-Then-Cut should cut OUTER boundaries only, not tiny alpha holes."""
    filename=folder/'planche_IMPRIMER_DECOUPER.png'
    rgba=np.asarray(Image.open(filename).convert('RGBA')).copy()
    fg=np.uint8(rgba[:,:,3]>127)*255
    outlines,_=cv2.findContours(fg,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    if not outlines:return 0
    filled=np.zeros_like(fg)
    cv2.drawContours(filled,outlines,-1,255,-1)
    created=(filled>0)&(fg==0)
    if not np.any(created):return 0
    rgba[created]=[255,255,255,255]
    Image.fromarray(rgba,'RGBA').save(filename)
    # Keep the standalone contour SVG synchronized with the actual print alpha.
    svg,count,verts=core.svg_from_mask(filled,width_mm,min_area_px=40,simplification=1.3)
    (folder/'planche_CONTOURS_12.svg').write_text(svg,encoding='utf-8')
    gray=np.full((rgba.shape[0],rgba.shape[1],3),239,dtype=np.uint8)
    alpha=rgba[:,:,3:4].astype(np.float32)/255
    gray=np.uint8(np.clip(gray*(1-alpha)+rgba[:,:,:3]*alpha,0,255))
    cv2.drawContours(gray,outlines,-1,(230,40,65),2)
    Image.fromarray(gray,'RGB').save(folder/'planche_CONTROLE_CONTOURS.png')
    return int(np.count_nonzero(created))


def process_v8(image_rgb,output_dir, *, layout='auto',intent='auto',ia_mode='auto',ai_masker=None,
               alpha=None,sheet_width_mm=180,margin_mm=1.5,editable_colors=10):
    """Returns (report, PIL preview). One run = one folder for all outputs.

    ai_masker is supplied by ComfyUI node and only used when model exists and
    background is uncertain; AI mask is rejected when it erases colored artwork.
    """
    report, contact=core.process_image(image_rgb,output_dir,layout=layout,intent=intent,ai_mode=ia_mode,
                 ai_masker=ai_masker,width_mm=80,input_alpha=alpha,
                 sheet_width_mm=sheet_width_mm,margin_mm=margin_mm)
    folder=Path(report['output'])
    holes_filled=_seal_internal_holes(folder,sheet_width_mm)
    # Generic alias: works for one illustration or many.
    shutil.copyfile(folder/'planche_CONTOURS_12.svg',folder/'planche_CONTOURS.svg')
    report['sheet']['cut_contours_svg']='planche_CONTOURS.svg'
    legacy_svg=folder/'planche_EDITABLE.svg'
    legacy_svg.rename(folder/'planche_VECTORIEL_DETAILLE.svg')
    detail_bases=_add_white_bases(folder/'planche_VECTORIEL_DETAILLE.svg',report,folder)
    vector_stats=_annotate_svg(folder/'planche_VECTORIEL_DETAILLE.svg')
    report['sheet']['editable_svg']='planche_VECTORIEL_DETAILLE.svg'
    simple_file,simple_stats=_simplified_layer_svg(report,image_rgb,folder,editable_colors)
    simple_bases=_add_white_bases(folder/simple_file,report,folder)
    _annotate_svg(folder/simple_file)
    simple_stats['chemins_fond_blanc']=simple_bases
    cut_report=_analyze_cut_sheet(folder/'planche_IMPRIMER_DECOUPER.png',
                             report['elements'],sheet_width_mm)
    # Clear user-oriented names while keeping legacy files for compatibility.
    # Additional file is a guide, not a replacement for Design Space validation.
    guide=("SMARTSVG STUDIO V8 - GUIDE CRICUT\n\n"
        "1. Pour garder les couleurs et les details : importe planche_IMPRIMER_DECOUPER.png.\n"
        "   Choisis Imprimer puis decouper. Ne rajoute pas planche_CONTOURS_12.svg par-dessus.\n"
        "2. Pour recolorer ou deplacer des formes vectorielles : importe planche_VECTORIEL_SIMPLIFIE.svg\n"
        "   ou planche_VECTORIEL_DETAILLE.svg. Les groupes de couleur sont editables.\n"
        "   Avant l'impression, utilise Aplatir / Flatten : seul le contour exterieur sera decoupe.\n"
        "3. Le SVG contient de VRAIS chemins ; ce n'est pas un PNG cache dans un SVG.\n"
        "   Les zones sont classees par personnage et couleur, PAS par concepts (oeil, coquille...).\n"
        "4. planche_CONTOURS.svg sert au controle ou a une decoupe pure ; pas a superposer\n"
        "   au PNG pour Print Then Cut sans gestion manuelle de l'alignement.\n"
        "5. Controle planche_CONTROLE_CONTOURS.png et rapport_V8.json.\n"
        "6. Effectue la calibration Print Then Cut et un essai sur papier ordinaire.\n")
    (folder/'LISEZ_MOI_CRICUT.txt').write_text(guide,encoding='utf-8')
    report['version']='8.0-local-beta'
    cut_report['pixels_de_trous_rebouches']=holes_filled
    report['qualite_decoupe']=cut_report
    report['vectorisation']={
       'detaille':{'fichier':'planche_VECTORIEL_DETAILLE.svg','paths':vector_stats},
       'simplifie':{'fichier':simple_file,**simple_stats},
       'limitation':'Objets classes par dessin et couleur, sans detection semantique fiable des yeux, coquilles, etc.'}
    report['export_recommande']='planche_IMPRIMER_DECOUPER.png' if intent not in ('logo','silhouette') else 'planche_VECTORIEL_SIMPLIFIE.svg'
    report['guide']='LISEZ_MOI_CRICUT.txt'
    report['alerts']=cut_report['alertes']
    # Human readable quick manifest. Users need not click through 30 files.
    (folder/'rapport_V8.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report,contact
