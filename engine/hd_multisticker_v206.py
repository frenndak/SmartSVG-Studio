"""V20.6: source-aware print resolution and multi-sticker export.

This additive module does not modify the V20.5 cut engines. Pixel enlargement is
explicitly reported as interpolation; there is no hallucinated detail or AI claim.
"""
from __future__ import annotations
import json, math, os, tempfile
from pathlib import Path
from uuid import uuid4
import cv2
import numpy as np
from PIL import Image, ImageDraw

PRESETS=('auto','affiche','logo_cartoon','planche_multi','capture_produit','scene_decorative')
CUTS=('sticker_contour','carte_rectangle')
DPI=(300,450)
MAX_SOURCE_PIXELS=20_000_000
MAX_OUTPUT_PIXELS=32_000_000

class ExportError(ValueError): pass

def _valid_image(pixels):
    if not isinstance(pixels,np.ndarray) or pixels.ndim!=3 or pixels.shape[2] not in (3,4):
        raise ExportError('Image RGB/RGBA [H,W,3/4] attendue')
    if pixels.dtype!=np.uint8 or pixels.size==0 or pixels.shape[0]*pixels.shape[1]>MAX_SOURCE_PIXELS:
        raise ExportError('Image absente, trop grande ou non uint8')
    return pixels

def _save_png(path,img,dpi=300):
    path=Path(path)
    with tempfile.NamedTemporaryFile(dir=path.parent,prefix='.v206_',suffix='.png',delete=False) as f: tmp=Path(f.name)
    try:
        img.save(tmp,'PNG',dpi=(dpi,dpi))
        os.replace(tmp,path)
    finally: tmp.unlink(missing_ok=True)

def _save_text(path,string):
    path=Path(path)
    with tempfile.NamedTemporaryFile(dir=path.parent,prefix='.v206_',suffix='.txt',mode='w',encoding='utf8',delete=False) as f:
        tmp=Path(f.name);f.write(string)
    try:os.replace(tmp,path)
    finally:tmp.unlink(missing_ok=True)

def _source_preset(rgb):
    h,w=rgb.shape[:2]
    nearblack=np.mean(np.max(rgb,axis=2)<32)
    nearwhite=np.mean(np.min(rgb,axis=2)>244)
    if nearblack>.38 and .9<w/h<1.8:return 'planche_multi'
    if w/h<.65 and nearblack>.35:return 'capture_produit'
    if nearwhite>.45:return 'logo_cartoon'
    if w/h<.62:return 'scene_decorative'
    return 'affiche'

def _crop_capture(rgb):
    """Find photo body of a phone screenshot; abstain if no unambiguous row band."""
    h,w=rgb.shape[:2]
    val=np.max(rgb,axis=2)
    row_fraction=np.mean(val>50,axis=1)
    active=row_fraction>.30
    regions=[];start=None
    for i,x in enumerate(active):
        if x and start is None:start=i
        if start is not None and (not x or i==h-1):
            end=i if not x else i+1
            if end-start>.17*h:regions.append((start,end))
            start=None
    if not regions:return rgb,(0,0,w,h),['CAPTURE_ZONE_PHOTO_NON_DETECTEE']
    y0,y1=max(regions,key=lambda t:t[1]-t[0]);pad=max(2,round(h*.006))
    y0=max(0,y0-pad);y1=min(h,y1+pad)
    if y1-y0>.90*h:return rgb,(0,0,w,h),['CAPTURE_INTERFACE_NON_ISOLEE']
    return rgb[y0:y1].copy(),(0,y0,w,y1),[]

def _crop_letterbox(rgb):
    """Remove full-width, nearly black padding bands; never crop internal dark art."""
    h,w=rgb.shape[:2]
    share=np.mean(np.max(rgb,axis=2)>35,axis=1)
    active=np.where(share>.08)[0]
    if not len(active):return rgb,(0,0,w,h),['LOGO_VIDE_OU_INDETECTABLE']
    y0=max(0,int(active[0])-2);y1=min(h,int(active[-1])+3)
    if (y0>h*.025 or h-y1>h*.025) and (y1-y0)>h*.15:
        return rgb[y0:y1].copy(),(0,y0,w,y1),[]
    return rgb,(0,0,w,h),[]

def _exterior_fill(mask):
    mask=np.uint8(mask>0)*255
    if not mask.any():return mask
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    filled=np.zeros_like(mask)
    cv2.drawContours(filled,contours,-1,255,thickness=cv2.FILLED)
    return filled

def _foreground_cell(cell):
    if cell.shape[2]==4:
        m=np.uint8(cell[...,3]>6)*255
    else:
        # Explicitly for near-black flat-background sticker sheets.
        rgb=cell[:,:,:3];m=np.uint8(np.max(rgb,axis=2)>29)*255
    # Remove isolated 1-2 px compression specks, but preserve claws/whiskers.
    n,labels,stats,_=cv2.connectedComponentsWithStats(m,8)
    threshold=max(3,int(m.size*.000025))
    m=np.uint8(np.isin(labels,[i for i in range(1,n) if stats[i,cv2.CC_STAT_AREA]>=threshold]))*255
    return _exterior_fill(m)

def _component_bounds(mask):
    ys,xs=np.where(mask>0)
    return (int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)) if len(xs) else None

def _make_single_backing(mask):
    """One cut island per item; convex hull only if contours remain disconnected."""
    mask=np.uint8(mask>0)*255
    n,_,_,_=cv2.connectedComponentsWithStats(mask,8)
    if n<=2:return mask,False
    cnt,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    points=np.concatenate(cnt,axis=0)
    hull=cv2.convexHull(points)
    solid=np.zeros_like(mask);cv2.fillConvexPoly(solid,hull,255)
    return solid,True

def _path_svg(alpha,physical_width,dpi):
    h,w=alpha.shape;contours,_=cv2.findContours(np.uint8(alpha>0)*255,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    paths=[]
    for c in contours:
        if len(c)<3:continue
        approx=cv2.approxPolyDP(c,epsilon=.0007*max(w,h),closed=True)
        if len(approx)<3:continue
        p=approx[:,0,:]
        paths.append('M'+' L'.join(f'{int(x)} {int(y)}' for x,y in p)+' Z')
    height=physical_width*h/w
    body=''.join('<path fill="black" d="'+p+'"/>' for p in paths)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{physical_width:.3f}mm" '
            f'height="{height:.3f}mm" viewBox="0 0 {w} {h}">'+body+'</svg>'),len(paths)

def _make_sticker(crop_rgb,crop_mask,width_mm,dpi,border_mm=1.2,allow_hull=True):
    """Return print RGBA, cut silhouette and quality diagnostics. No visual AI enhancement."""
    h,w=crop_rgb.shape[:2]
    target=max(w,int(math.ceil(width_mm*dpi/25.4))) # never discard source pixels
    scale=target/w
    out_h=max(1,int(round(h*scale)))
    radius=max(1,int(round(border_mm*dpi/25.4)))
    if target*out_h>MAX_OUTPUT_PIXELS:raise ExportError('Sortie trop volumineuse')
    src=Image.fromarray(crop_rgb[:,:,:3],'RGB')
    pixels=np.asarray(src.resize((target,out_h),Image.Resampling.LANCZOS))
    mask=cv2.resize(crop_mask,(target,out_h),interpolation=cv2.INTER_NEAREST)
    # A consistent white backing acts as the outer cut silhouette.
    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(radius*2+1,radius*2+1))
    backing=cv2.dilate(mask,kernel)
    backing,hull=_make_single_backing(backing) if allow_hull else (backing,False)
    ww=target+radius*2+6;hh=out_h+radius*2+6
    if ww*hh>MAX_OUTPUT_PIXELS:raise ExportError('Sortie marges trop volumineuse')
    off=radius+3
    alpha=np.zeros((hh,ww),np.uint8)
    alpha[off:off+out_h,off:off+target]=backing
    image=np.zeros((hh,ww,4),np.uint8)
    image[:,:,:3]=255
    image[:,:,3]=alpha
    sub=image[off:off+out_h,off:off+target]
    m=mask>0
    if crop_rgb.shape[2]==4:
        src_alpha=cv2.resize(crop_rgb[:,:,3],(target,out_h),interpolation=cv2.INTER_LINEAR).astype(np.float32)/255.
        premix=(pixels.astype(np.float32)*src_alpha[:,:,None]+255*(1-src_alpha[:,:,None])).astype(np.uint8)
        sub[:,:,:3][m]=premix[m]
    else:
        sub[:,:,:3][m]=pixels[m]
    # Native source pixel density is the limit of preserved detail.
    native_dpi=25.4*w/width_mm
    export_dpi=25.4*ww/(width_mm*ww/target) # equal to target-width basis
    warnings=[]
    if scale>1.35:warnings.append('AGRANDISSEMENT_INTERPOLATION_NE_CREE_PAS_DE_DETAIL')
    if native_dpi<200:warnings.append('SOURCE_MOINS_DE_200_PPP_A_CETTE_TAILLE')
    if hull:warnings.append('ILOTS_REUNIS_PAR_ENVELOPPE_CONVEXE_A_VERIFIER')
    # Entire file includes outer white border. Its actual physical width is larger.
    physical_width=ww/target*width_mm
    return Image.fromarray(image,'RGBA'),alpha,{
        'pixels_source_utiles':[w,h], 'dimensions_px_export':[ww,hh],
        'largeur_finale_avec_marge_mm':round(physical_width,2),
        'densite_export_cible_ppp':dpi,
        'densite_native_estimee_ppp':round(native_dpi,1),
        'facteur_interpolation':round(scale,3),'avertissements':warnings,
        'contour_convexe_secours':hull}

def _make_card(rgb,width_mm,dpi):
    h,w=rgb.shape[:2];target=max(w,round(width_mm*dpi/25.4));height=round(h*target/w)
    if target*height>MAX_OUTPUT_PIXELS:raise ExportError('Taille export trop volumineuse')
    rendered=Image.fromarray(rgb[:,:,:3],'RGB').resize((target,height),Image.Resampling.LANCZOS)
    # Add a thin white outside region so a rectangular Print Then Cut doesn't touch canvas edge.
    border=max(4,int(round(.8*dpi/25.4)))
    output=Image.new('RGBA',(target+2*border,height+2*border),'white')
    output.paste(rendered,(border,border))
    native_dpi=25.4*w/width_mm;scale=target/w
    return output,{
        'pixels_source_utiles':[w,h],'dimensions_px_export':list(output.size),
        'largeur_finale_avec_marge_mm':round(output.width/target*width_mm,2),
        'densite_export_cible_ppp':dpi,'densite_native_estimee_ppp':round(native_dpi,1),
        'facteur_interpolation':round(scale,3),
        'avertissements':(['AGRANDISSEMENT_INTERPOLATION_NE_CREE_PAS_DE_DETAIL'] if scale>1.35 else []),
        'type_coupe':'CADRE_RECTANGULAIRE'}

def _smart_boundaries(fg,n,axis):
    """Find a low-ink separation near each regular-grid boundary."""
    density=np.mean(fg,axis=axis).astype(np.float32)
    smoothed=np.convolve(density,np.ones(13,dtype=np.float32)/13,mode='same')
    length=len(smoothed);estimated=length/n
    result=[0]
    for k in range(1,n):
        want=k*estimated
        left=max(result[-1]+10,round(want-estimated*.32))
        right=min(length-10,round(want+estimated*.32))
        if right<=left:point=round(want)
        else:
            segment=smoothed[left:right]
            bottom=float(np.min(segment))
            candidates=np.where(segment<=bottom+max(.001, bottom*.10))[0]+left
            point=int(candidates[np.argmin(np.abs(candidates-want))])
        result.append(point)
    return result+[length]

def _grid_component_groups(pixels,cols,rows):
    """Associate whole connected foreground components with their nearest grid cell.

    This avoids splitting ears, flames and leaves extending past a regular cell edge.
    Components crossing the centre of two cells remain an uncertain case.
    """
    if pixels.shape[2]==4 and np.any(pixels[:,:,3]<250):
        fg=np.uint8(pixels[:,:,3]>6)
    else:
        rgb=pixels[:,:,:3]
        # Infer simple background only from a border sample; do not silently
        # erase a photograph or a complicated patterned backdrop.
        border=np.concatenate((rgb[0],rgb[-1],rgb[:,0],rgb[:,-1]),axis=0)
        median=np.median(border,axis=0)
        if np.max(median)<50:
            fg=np.uint8(np.max(rgb,axis=2)>29)
        elif np.min(median)>210:
            fg=np.uint8(np.min(rgb,axis=2)<235)
        else:
            raise ExportError('Fond de planche non uniforme : utiliser un masque IA ou une planche à fond noir/blanc')
    xs=_smart_boundaries(fg,cols,axis=0)
    ys=_smart_boundaries(fg,rows,axis=1)
    n,labels,stats,centroids=cv2.connectedComponentsWithStats(fg,8)
    groups={(r,c):[] for r in range(rows) for c in range(cols)}
    for i in range(1,n):
        if stats[i,cv2.CC_STAT_AREA]<max(4,int(fg.size*.000004)):continue
        x,y=centroids[i]
        col=min(cols-1,max(0,int(np.searchsorted(xs,x,side='right')-1)))
        row=min(rows-1,max(0,int(np.searchsorted(ys,y,side='right')-1)))
        groups[row,col].append(i)
    for row in range(rows):
        for col in range(cols):
            ids=groups[row,col]
            if not ids:
                yield row,col,None,None
                continue
            x0=min(stats[i,cv2.CC_STAT_LEFT] for i in ids)
            y0=min(stats[i,cv2.CC_STAT_TOP] for i in ids)
            x1=max(stats[i,cv2.CC_STAT_LEFT]+stats[i,cv2.CC_STAT_WIDTH] for i in ids)
            y1=max(stats[i,cv2.CC_STAT_TOP]+stats[i,cv2.CC_STAT_HEIGHT] for i in ids)
            local=np.uint8(np.isin(labels[y0:y1,x0:x1],ids))*255
            yield row,col,(x0,y0,x1,y1),_exterior_fill(local)

def _grid_cells(pixels,cols,rows):
    h,w=pixels.shape[:2]
    xs=np.linspace(0,w,cols+1).astype(int);ys=np.linspace(0,h,rows+1).astype(int)
    for row in range(rows):
        for col in range(cols):
            yield row,col,(xs[col],ys[row],xs[col+1],ys[row+1])

def _preview(images,cols,cell=(180,200)):
    if not images:raise ExportError('Aucun apercu a composer')
    rows=math.ceil(len(images)/cols);out=Image.new('RGB',(cols*cell[0],rows*cell[1]),'#e7e7e7')
    painter=ImageDraw.Draw(out)
    for i,p in enumerate(images):
        v=p.copy();v.thumbnail((cell[0]-14,cell[1]-28),Image.Resampling.LANCZOS)
        x=i%cols*cell[0]+(cell[0]-v.width)//2;y=i//cols*cell[1]+7
        out.paste(v,(x,y),v if v.mode=='RGBA' else None)
        painter.text((i%cols*cell[0]+6,(i//cols+1)*cell[1]-17),f'{i+1:02d}',fill='#333333')
    return out

def _save_sheet(objects,path,dpi,columns=6):
    """Transparent one-layer Print Then Cut candidate; each object's white halo is its cut island."""
    if not objects:raise ExportError('Planche vide')
    space=int(round(3.0*dpi/25.4))
    maxw=max(im.width for im in objects);maxh=max(im.height for im in objects)
    rows=math.ceil(len(objects)/columns)
    sheetw=columns*maxw+(columns+1)*space
    sheeth=rows*maxh+(rows+1)*space
    if sheetw*sheeth>MAX_OUTPUT_PIXELS:
        return {'statut':'TROP_GRAND','avertissement':'Planche non produite; exporter les PNG individuels'}
    sheet=Image.new('RGBA',(sheetw,sheeth),(0,0,0,0))
    for i,im in enumerate(objects):
        col=i%columns;row=i//columns
        x=space+(maxw+space)*col+(maxw-im.width)//2
        y=space+(maxh+space)*row+(maxh-im.height)//2
        sheet.alpha_composite(im,(x,y))
    _save_png(path,sheet,dpi)
    alpha=np.asarray(sheet.getchannel('A'))>0
    n,_,stats,_=cv2.connectedComponentsWithStats(np.uint8(alpha),8)
    return {'statut':'CREATION_OK','fichier':str(path),'taille_px':list(sheet.size),
            'taille_estimee_mm':[round(sheet.width*25.4/dpi,1),round(sheet.height*25.4/dpi,1)],
            'ilots_alpha_detectes':n-1,'objets':len(objects),
            'a_verifier':'Si le nombre ilots differe du nombre objets, ne pas lancer Print Then Cut.'}

def run_v206(pixels,destination,preset='auto',width_mm=40,dpi=300,mode_coupe='sticker_contour',grille='6x4'):
    _valid_image(pixels)
    if preset not in PRESETS or mode_coupe not in CUTS or dpi not in DPI or grille not in ('6x4','4x3','3x3','auto'):
        raise ExportError('Profil, grille ou resolution incorrects')
    if isinstance(width_mm,bool) or not math.isfinite(float(width_mm)) or not (15<=float(width_mm)<=180):
        raise ExportError('Largeur de sortie en mm invalide')
    destination=Path(destination).expanduser().absolute()
    if destination.is_symlink():raise ExportError('Dossier de sortie symbolique interdit')
    destination.mkdir(parents=True,exist_ok=True)
    if not destination.is_dir():raise ExportError('Dossier de sortie invalide')
    root=destination/('SmartSVG_V20_6_'+uuid4().hex[:10]);root.mkdir()
    rgb=pixels[...,:3].copy();choice=_source_preset(rgb) if preset=='auto' else preset
    report={'version':'20.6-beta','preset_demande':preset,'preset_applique':choice,
            'source_dimensions':list(pixels.shape[:2][::-1]),'largeur_element_mm':width_mm,
            'densite_export_ppp':dpi,'mode_coupe':mode_coupe,
            'dossier':str(root),'validation_cricut_physique':False,
            'avertissements_generaux':['Verifer taille et operation dans Design Space avant impression.'],
            'objets':[]}
    _save_png(root/'SOURCE_ORIGINALE.png',Image.fromarray(pixels),dpi)
    rgba=pixels
    if choice=='capture_produit':
        crop,coords,warns=_crop_capture(rgb)
        if rgba.shape[2]==4:crop=rgba[coords[1]:coords[3],coords[0]:coords[2]]
        rgba=crop
        report['recadrage_capture']=list(coords)
        report['avertissements_generaux']+=warns
    if choice=='logo_cartoon':
        clipped,coords,warns=_crop_letterbox(rgb)
        if rgba.shape[2]==4:
            rgba=rgba[coords[1]:coords[3],coords[0]:coords[2]]
        else:
            rgba=clipped
        report['recadrage_bandes_logo']=list(coords)
        report['avertissements_generaux']+=warns
    if choice=='planche_multi':
        if grille=='6x4':cols,rows=6,4
        elif grille=='4x3':cols,rows=4,3
        elif grille=='3x3':cols,rows=3,3
        else:cols,rows=6,4;report['avertissements_generaux'].append('GRILLE_AUTO_ESTIMATION_6X4_VERIFIER')
        individual=root/'INDIVIDUELS';individual.mkdir()
        images=[];count_missing=0
        for row,col,bounds,maskcrop in _grid_component_groups(rgba,cols,rows):
            if bounds is None:
                count_missing+=1;continue
            x0,y0,x1,y1=bounds
            rgbcrop=rgba[y0:y1,x0:x1]
            if np.count_nonzero(maskcrop)<max(20,int(maskcrop.size*.003)):
                count_missing+=1;continue
            sticker,cut,qa=_make_sticker(rgbcrop,maskcrop,width_mm,dpi)
            idx=row*cols+col+1
            target=individual/f'{idx:02d}_L{row+1}_C{col+1}_CRICUT.png'
            svg=individual/f'{idx:02d}_CONTOUR_SEUL.svg'
            _save_png(target,sticker,dpi)
            svgtext,paths=_path_svg(cut,qa['largeur_finale_avec_marge_mm'],dpi)
            _save_text(svg,svgtext)
            qa.update({'numero':idx,'case':[row+1,col+1],'contour_nombre_chemins':paths,
                       'png':str(target),'svg_contour':str(svg)})
            if paths!=1:qa['avertissements'].append('DECOUPE_NON_UNIQUE')
            report['objets'].append(qa);images.append(sticker)
        report['grille_lignes_colonnes']=[rows,cols]
        report['cases_vides']=count_missing
        if count_missing:report['avertissements_generaux'].append('CERTAINES_CASES_SANS_PERSONNAGE')
        report['aperçu_visuel_non_cricut']=str(root/'APERÇU_24_PERSONNAGES.png')
        _save_png(root/'APERÇU_24_PERSONNAGES.png',_preview(images,cols),dpi)
        # Two printable candidates at the exact requested object size. A single 6x4
        # page at 32-40 mm/person often exceeds A4 Print Then Cut dimensions.
        report['planches_cricut']=[]
        for start_idx in range(0,len(images),12):
            chunk=images[start_idx:start_idx+12]
            sheet_path=root/f'PLANCHE_CRICUT_{start_idx//12+1:02d}_A_VERIFIER.png'
            summary=_save_sheet(chunk,sheet_path,dpi,columns=4)
            if summary.get('statut')=='CREATION_OK':
                w_mm,h_mm=summary['taille_estimee_mm']
                if w_mm>175 or h_mm>250:
                    summary['statut']='DIMENSIONS_A4_A_VERIFIER'
                    report['avertissements_generaux'].append('PLANCHE_POTENTIELLEMENT_TROP_GRANDE_DESIGN_SPACE')
                if summary.get('ilots_alpha_detectes')!=len(chunk):
                    report['avertissements_generaux'].append('ATTENTION_NOMBRE_DE_DECOUPES_INCOHERENT')
            report['planches_cricut'].append(summary)
        out_image=_preview(images,cols)
    elif rgba.shape[2]==4 and np.any(rgba[:,:,3]<255) and mode_coupe=='sticker_contour':
        # The input already has transparency. Honor it rather than making an opaque card.
        native_mask=np.uint8(rgba[:,:,3]>1)*255
        bounds=_component_bounds(native_mask)
        if bounds is None:raise ExportError('Source entierement transparente')
        x0,y0,x1,y1=bounds
        sticker,cut,qa=_make_sticker(rgba[y0:y1,x0:x1],native_mask[y0:y1,x0:x1],width_mm,dpi)
        out_png=root/'01_IMPRIMER_DECOUPER_SILHOUETTE.png';_save_png(out_png,sticker,dpi)
        contour=root/'02_CONTOUR_SEUL.svg'
        svgstr,paths=_path_svg(cut,qa['largeur_finale_avec_marge_mm'],dpi)
        _save_text(contour,svgstr)
        qa.update({'png':str(out_png),'svg_contour':str(contour),'contour_nombre_chemins':paths,
                   'source_alpha':'SOURCE_AVEC_TRANSPARENCE_UTILISEE'})
        report['objets']=[qa]
        out_image=sticker.copy();out_image.thumbnail((700,700),Image.Resampling.LANCZOS)
    else:
        # Complex scenes / posters deliberately use a rectangular cut; semantic object
        # isolation requires real segmentation and is NOT inferred from colors alone.
        image,qa=_make_card(rgba,width_mm,dpi)
        if choice=='logo_cartoon':
            qa['avertissements'].append('DETROUAGE_CARACTERE_NON_AUTOMATIQUE_DANS_CE_PROFIL')
        if choice=='capture_produit':
            qa['avertissements'].append('DETROUAGE_CANARD_NON_VALIDE: CADRE_IMPRIME_PAR_DEFAUT')
        if mode_coupe=='sticker_contour':
            qa['avertissements'].append('IMAGE_COMPLEXE: COUPE_RECTANGULAIRE; MASQUE_IA_REQUIS_POUR_SUJET')
        png=root/'01_IMPRIMER_DECOUPER_CADRE.png';_save_png(png,image,dpi)
        alpha=np.asarray(image.getchannel('A'))
        svgstr,paths=_path_svg(alpha,qa['largeur_finale_avec_marge_mm'],dpi)
        svg=root/'02_CONTOUR_CADRE.svg';_save_text(svg,svgstr)
        qa.update({'png':str(png),'svg_contour':str(svg),'contour_nombre_chemins':paths})
        report['objets']=[qa]
        out_image=image.copy();out_image.thumbnail((700,700),Image.Resampling.LANCZOS)
    report['nombre_objets_exportes']=len(report['objets'])
    _save_text(root/'RAPPORT_V20_6.json',json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False))
    return report,out_image
