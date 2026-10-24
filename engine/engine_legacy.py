"""SmartSVG Auto - deterministic local image analysis and color-layer SVG generator.

Requires numpy, Pillow, OpenCV. GPU background removal is provided by ComfyUI-RMBG
via an injected mask function; the engine does not import model weights.
"""
import json
import math
import os
import re
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

import cv2
import numpy as np
from PIL import Image, ImageDraw

SVG_NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG_NS)


def bands_from_projection(rgb, axis):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    vibrant = ((hsv[..., 1] > 46) & (hsv[..., 2] > 60)).astype(np.uint8)
    cross = vibrant.sum(axis=0 if axis == 'x' else 1)
    denom = rgb.shape[0] if axis == 'x' else rgb.shape[1]
    n = cross.shape[0]
    kernel = max(7, round(n * 0.009) | 1)
    smooth = np.convolve(cross.astype(float), np.ones(kernel) / kernel, mode='same')
    active = smooth > max(4.0, denom * .014)
    inds = np.flatnonzero(active)
    if len(inds) == 0:
        return []
    intervals = []
    start = prev = int(inds[0])
    bridge = max(9, round(n * .01))
    for point in inds[1:]:
        point = int(point)
        if point - prev > bridge:
            intervals.append((start, prev + 1))
            start = point
        prev = point
    intervals.append((start, prev + 1))
    return [(a, b) for a, b in intervals if b - a >= n * .10]


def detect_layout(rgb, mode='auto'):
    """Return crop boxes and reason. Conservative grid detection avoids false positives."""
    h, w = rgb.shape[:2]
    if mode == 'unique':
        return [(0, 0, w, h)], 'single_forced'
    xs = bands_from_projection(rgb, 'x')
    ys = bands_from_projection(rgb, 'y')
    def regular(bands, n):
        if len(bands) < 2 or len(bands) > 8:
            return False
        sizes = np.array([b-a for a,b in bands], dtype=float)
        centers = np.array([(a+b)/2 for a,b in bands], dtype=float)
        separations = np.diff(centers)
        if not np.all(separations > 0):
            return False
        return (sizes.min() > n*.09 and sizes.std()/sizes.mean() < .28
                and separations.std()/separations.mean() < .19
                and (bands[-1][1] - bands[0][0]) > n*.65)
    valid_x, valid_y = regular(xs,w),regular(ys,h)
    likely = valid_x and valid_y and len(xs)*len(ys)>=4
    if mode == 'planche' and not likely:
        raise ValueError('Planche non reconnue automatiquement : utilise le mode image_unique ou une grille aux cases bien séparées.')
    if not likely:
        return [(0,0,w,h)], 'single_auto'
    pad_x = max(3, round(w*.003))
    pad_y = max(3, round(h*.003))
    boxes=[]
    for y0,y1 in ys:
        for x0,x1 in xs:
            boxes.append((max(0,x0-pad_x),max(0,y0-pad_y),min(w,x1+pad_x),min(h,y1+pad_y)))
    return boxes, f'grid_{len(xs)}x{len(ys)}'


def detect_transparent_layout(alpha, mode='auto'):
    """Support sparse, irregular transparent sticker sheets without assuming a grid.

    ComfyUI LoadImage.MASK gives the real alpha, so disjoint foreground
    components are more reliable than color projections. When components are
    too small or too numerous, refuse to guess instead of making tiny stickers.
    """
    if alpha is None or mode == 'unique':
        return None
    src=np.asarray(alpha)
    if src.ndim!=2 or not np.any(src < 250):
        return None
    solid=np.uint8(src>127)
    n,labels,stats,_=cv2.connectedComponentsWithStats(solid,8)
    h,w=solid.shape
    cutoff=max(20, int(h*w*.0002))
    good=[j for j in range(1,n) if stats[j,cv2.CC_STAT_AREA]>=cutoff]
    if len(good)<2 or len(good)>48:
        return None
    pad=max(2,round(min(h,w)*.003))
    boxes=[]
    for j in good:
        x,y,ww,hh,_=[int(x) for x in stats[j]]
        boxes.append((max(0,x-pad),max(0,y-pad),min(w,x+ww+pad),min(h,y+hh+pad)))
    # Avoid an ambiguous component partition with overlapping padded crops.
    for k,a in enumerate(boxes):
        for b in boxes[k+1:]:
            if min(a[2],b[2])>max(a[0],b[0]) and min(a[3],b[3])>max(a[1],b[1]):
                return None
    boxes.sort(key=lambda b:(b[1],b[0]))
    return boxes,f'alpha_{len(boxes)}_elements_irreguliers'


def exterior_mask(rgb):
    """Conservative removal of uniform edge-connected background, preserving enclosed white markings."""
    h,w=rgb.shape[:2]
    lab=cv2.cvtColor(rgb,cv2.COLOR_RGB2LAB).astype(np.float32)
    t=max(3, min(h,w)//30)
    edge=np.concatenate([lab[:t].reshape(-1,3),lab[-t:].reshape(-1,3),
                         lab[:,:t].reshape(-1,3),lab[:,-t:].reshape(-1,3)])
    bg=np.median(edge,axis=0)
    bg_error=np.linalg.norm(edge-bg,axis=1)
    reliability=float(np.mean(bg_error<17))
    dist=np.linalg.norm(lab-bg,axis=-1)
    # Only remove pixels close to dominant perimeter color, connected to an edge.
    close=(dist<18).astype(np.uint8)
    cc_count,labels,stats, _=cv2.connectedComponentsWithStats(close,8)
    border=np.concatenate([labels[0],labels[-1],labels[:,0],labels[:,-1]])
    ids,counts=np.unique(border,return_counts=True)
    bg_ids=ids[(ids!=0)&(counts>=max(5,t))]
    bgmask=np.isin(labels,bg_ids)
    fg=(~bgmask).astype(np.uint8)*255
    # Do not guess a transparent background if perimeter is highly mixed.
    if reliability<.60:
        return np.ones((h,w),dtype=np.uint8)*255, {'reliable':False,'edge_consistency':round(reliability,3)}
    # cleanup tiny isolated background mistakes only
    return fg, {'reliable':True,'edge_consistency':round(reliability,3)}


def classify(rgb, mode):
    if mode!='auto': return mode
    scale=cv2.resize(rgb,(min(rgb.shape[1],256),min(rgb.shape[0],256)))
    hsv=cv2.cvtColor(scale,cv2.COLOR_RGB2HSV)
    smooth=cv2.GaussianBlur(scale,(5,5),0)
    delta=np.mean(np.abs(scale.astype(np.float32)-smooth.astype(np.float32)))
    sample=scale[::3,::3]
    count=len(np.unique((sample//24).reshape(-1,3),axis=0))
    saturation=float(np.mean(hsv[...,1])/255)
    if count<65 and delta<9: return 'logo'
    if count<380 and saturation>.11: return 'cartoon'
    return 'illustration_complexe'


def consider_ai_mask(base_mask, ai_mask, rgb, reliable):
    if ai_mask is None:
        return base_mask, 'sans_IA', 'fond_uniforme_deja_propre' if reliable else 'modele_indisponible'
    h,w=base_mask.shape
    ai=np.asarray(ai_mask)
    if ai.ndim!=2 or ai.shape!=(h,w):
        ai=cv2.resize(ai.astype(np.float32),(w,h),interpolation=cv2.INTER_LINEAR)
    if float(np.max(ai))<=1.01: ai=ai*255
    ai=(ai>=100).astype(np.uint8)*255
    frac=float(np.count_nonzero(ai)/(h*w))
    if frac<.035 or frac>.97: return base_mask,'sans_IA','masque_IA_incoherent'
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
    vivid=((hsv[...,1]>80)&(hsv[...,2]>60))
    if np.count_nonzero(vivid)>50:
        recall=float(np.mean(ai[vivid]>0))
        if recall<.89: return base_mask,'sans_IA','IA_supprime_des_couleurs_importantes'
    # If easy bg is already reliably separated and AI is not a better, safer outline, keep original.
    if reliable:
        ref=np.count_nonzero(base_mask)
        lost=np.count_nonzero((base_mask>0)&(ai==0)) / max(1,ref)
        if lost>.08: return base_mask,'sans_IA','IA_supprime_plus_de_8pct_du_sujet'
        # conservative direct is preferable on light uniform clean backgrounds
        return base_mask,'sans_IA','fond_uniforme_deja_propre'
    return ai,'IA_locale','masque_valide'


def palette_quantize(rgb, mask, colors, clean=False):
    work=rgb.copy()
    if clean:
        work=cv2.medianBlur(work,3)
    sel=mask>0
    pts=work[sel]
    if len(pts)==0:
        return np.zeros(mask.shape,np.uint8),np.zeros((1,3),np.uint8)
    uniq,inv=np.unique((pts//3).astype('uint8'),axis=0,return_inverse=True)
    nclusters=int(min(max(1,colors),len(uniq)))
    if nclusters == 1:
        centers=np.array([np.median(pts,axis=0)],np.uint8)
    else:
        # Sample deterministically for stable result, then nearest-color assignment.
        sampled=pts[::max(1,len(pts)//3500)].astype(np.float32)
        cv2.setRNGSeed(42)
        _,_,centers=cv2.kmeans(sampled,nclusters,None,
                (cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER,15,.55),2,cv2.KMEANS_PP_CENTERS)
        centers=np.uint8(np.clip(centers.round(),0,255))
    # Assign in slices to cap memory for larger images.
    flat=work.reshape(-1,3)
    ids=np.zeros(len(flat),np.uint8)
    selection=np.flatnonzero(sel.reshape(-1))
    palette=centers.astype(np.int16)
    for start in range(0,len(selection),50000):
        indexes=selection[start:start+50000]
        d=(flat[indexes,None,:].astype(np.int16)-palette[None,:,:]).astype(np.int32)
        ids[indexes]=(d*d).sum(axis=2).argmin(axis=1).astype(np.uint8)
    return ids.reshape(mask.shape),centers


def contour_path(contour, epsilon, smooth=True):
    points=cv2.approxPolyDP(contour,epsilon,True).reshape(-1,2).astype(float)
    if len(points)<3: return '',0
    def xy(p):
        return f'{p[0]:.2f},{p[1]:.2f}'
    if not smooth or len(points)<5:
        terms=[f'M{xy(points[0])}']
        terms.extend(f'L{xy(p)}' for p in points[1:])
    else:
        # Closed Catmull-Rom to cubic Beziers: smooth, true vector geometry,
        # with no raster embedded. The original simplified contour controls it.
        n=len(points)
        terms=[f'M{xy(points[0])}']
        for i in range(n):
            p0=points[(i-1)%n];p1=points[i];p2=points[(i+1)%n];p3=points[(i+2)%n]
            c1=p1+(p2-p0)/6
            c2=p2-(p3-p1)/6
            terms.append(f'C{xy(c1)} {xy(c2)} {xy(p2)}')
    terms.append('Z')
    return ' '.join(terms),len(points)


def svg_from_mask(mask, width_mm, min_area_px=10, simplification=1.0, color='#202020'):
    h,w=mask.shape
    root=ET.Element(f'{{{SVG_NS}}}svg',{'width':f'{width_mm:.2f}mm','height':f'{width_mm*h/w:.2f}mm',
                    'viewBox':f'0 0 {w} {h}','version':'1.1'})
    contours,hier=cv2.findContours(mask,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    pathcount=0; npoints=0
    if hier is None:return ET.tostring(root,encoding='unicode'),0,0
    hier=hier[0]
    for i,c in enumerate(contours):
        if hier[i][3]!=-1 or cv2.contourArea(c)<min_area_px:continue
        path,n=contour_path(c,simplification)
        if not path: continue
        child=hier[i][2]
        while child!=-1:
            hole,nn=contour_path(contours[child],simplification)
            if hole and cv2.contourArea(contours[child])>=min_area_px: path+=' '+hole; n+=nn
            child=hier[child][0]
        ET.SubElement(root,f'{{{SVG_NS}}}path',{'d':path,'fill':color,'fill-rule':'evenodd'})
        pathcount+=1;npoints+=n
    return ET.tostring(root,encoding='unicode'),pathcount,npoints


def vector_layers(rgb, mask, width_mm, colors, min_detail_mm, clean):
    h,w=mask.shape
    idx,centers=palette_quantize(rgb,mask,colors,clean=clean)
    root=ET.Element(f'{{{SVG_NS}}}svg',{'width':f'{width_mm:.2f}mm','height':f'{width_mm*h/w:.2f}mm',
                'viewBox':f'0 0 {w} {h}','version':'1.1'})
    count=0; vertices=0; tiny=0
    min_px=max(2,min_detail_mm*w/max(width_mm,1))
    min_area=max(4,(min_px*min_px)*.6)
    # Sort by area largest first. Each color is an editable named group.
    regions=[(int(np.sum((idx==i)&(mask>0))),i) for i in range(len(centers))]
    for _,i in sorted(regions,reverse=True):
        binary=np.uint8((idx==i)&(mask>0))*255
        contours, hierarchy=cv2.findContours(binary,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
        if hierarchy is None:continue
        # stable group id and hex color
        col='#'+''.join(f'{int(c):02x}' for c in centers[i])
        group=ET.SubElement(root,f'{{{SVG_NS}}}g',{'id':f'couleur_{i:02d}', 'fill':col, 'data-color':col})
        hh=hierarchy[0]
        for j,c in enumerate(contours):
            if hh[j][3]!=-1:continue
            rect=cv2.boundingRect(c)
            area=cv2.contourArea(c)
            if area<min_area or min(rect[2],rect[3])<max(1.5,min_px*.5):tiny+=1;continue
            path,n=contour_path(c, max(.65,min_px*.32))
            if not path:continue
            child=hh[j][2]
            while child!=-1:
                hole,nn=contour_path(contours[child],max(.65,min_px*.32))
                if hole and cv2.contourArea(contours[child])>2: path+=' '+hole;n+=nn
                child=hh[child][0]
            ET.SubElement(group,f'{{{SVG_NS}}}path',{'d':path,'fill-rule':'evenodd'})
            count+=1;vertices+=n
    return ET.tostring(root,encoding='unicode'),{'paths':count,'vertices':vertices,'small_shapes_filtered':tiny,'colors':colors}


def foreground_silhouette(mask, width_mm):
    px=width_mm/max(1,mask.shape[1])
    k=max(1,int(round(.5/px)))
    ker=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*k+1,2*k+1))
    merged=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,ker)
    # remove stray points; retain separate flowers and leaf components
    return merged


def make_contact_sheet(previews):
    if not previews:return Image.new('RGB',(1,1),'white')
    box_w,box_h=280,290
    cols=min(4,len(previews));rows=math.ceil(len(previews)/cols)
    sheet=Image.new('RGB',(cols*box_w,rows*box_h),(245,245,245))
    d=ImageDraw.Draw(sheet)
    for i,(im,label) in enumerate(previews):
        canvas=Image.new('RGBA',(box_w-20,box_h-30),'white')
        mini=im.copy();mini.thumbnail((box_w-30,box_h-40),Image.Resampling.LANCZOS)
        canvas.alpha_composite(mini,((canvas.width-mini.width)//2,(canvas.height-mini.height)//2))
        x=(i%cols)*box_w;y=(i//cols)*box_h
        sheet.paste(canvas.convert('RGB'),(x+10,y+22))
        d.text((x+14,y+6),label,fill=(32,32,32))
    return sheet



def create_grouped_sheet(source, items, directory, *, sheet_width_mm=180, margin_mm=1.5):
    """Create one editable vector artboard and one Print-Then-Cut board.

    Editable = named object groups and paths by flat color (NOT semantic Magic Layers).
    Print = original pixels/white stickers; SVG cut = outer closed silhouettes.
    This function never embeds an image inside the editable SVG.
    """
    h,w=source.shape[:2]
    mm_per_px=sheet_width_mm/w
    border_px=max(1,round(margin_mm/mm_per_px))
    board=np.zeros((h,w,4),np.uint8)
    global_fg=np.zeros((h,w),np.uint8)
    art=np.zeros((h,w,3),np.uint8)
    root=ET.Element(f'{{{SVG_NS}}}svg',{
      'width':f'{sheet_width_mm:.2f}mm','height':f'{sheet_width_mm*h/w:.2f}mm',
      'viewBox':f'0 0 {w} {h}','version':'1.1'})
    paths=0
    masks_quality=[]
    for index,(x0,y0,x1,y1),rgb,mask,svg_layers in items:
        ch,cw=mask.shape
        # The same printed art and vector source are kept in their original sheet positions.
        node=ET.fromstring(svg_layers)
        obj=ET.SubElement(root,f'{{{SVG_NS}}}g',{
            'id':f'illustration_{index:02d}', 'data-label':f'Illustration {index:02d}',
            'transform':f'translate({x0},{y0})'})
        for group in list(node):
            if group.get('id'):
                group.set('id', f'illustration_{index:02d}_{group.get("id")}')
            obj.append(group)
            paths+=len(list(group))
        # Fill original foreground holes but do not select the exterior frame.
        base=np.asarray(mask>127,dtype=np.uint8)*255
        if cv2.countNonZero(base)==0:continue
        close_radius=max(2,min(7,round(cw*.012)))
        close_kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*close_radius+1,)*2)
        base=cv2.morphologyEx(base,cv2.MORPH_CLOSE,close_kernel)
        contours,_=cv2.findContours(base,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        filled=np.zeros_like(base)
        for contour in contours:
            if cv2.contourArea(contour)>max(15,.00025*cw*ch):
                cv2.drawContours(filled,[contour],-1,255,-1)
        # Assemble the ORIGINAL details on the full sheet, before adding border.
        # Dilation AFTER composition prevents the print/cut halo being clipped by a crop box.
        global_fg[y0:y1,x0:x1]=np.maximum(global_fg[y0:y1,x0:x1],filled)
        art[y0:y1,x0:x1][filled>0]=rgb[filled>0]
        merged=filled
        num_labels,labels,stats,_=cv2.connectedComponentsWithStats(merged,8)
        large=sum(1 for j in range(1,num_labels) if stats[j,cv2.CC_STAT_AREA]>max(25,.001*cw*ch))
        masks_quality.append({'illustration':index,'cut_components':large})
    # Add one globally computed halo: the 12 islands expand beyond crop boundaries,
    # but never include the background frame dotted lines.
    ker=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(border_px*2+1,)*2)
    cut=cv2.dilate(global_fg,ker)
    cut=cv2.morphologyEx(cut,cv2.MORPH_CLOSE,
            cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
    board[cut>0]=[255,255,255,255]
    board[global_fg>0,:3]=art[global_fg>0]
    board[global_fg>0,3]=255
    ET.ElementTree(root).write(directory/'planche_EDITABLE.svg',encoding='utf-8',xml_declaration=True)
    Image.fromarray(board,'RGBA').save(directory/'planche_IMPRIMER_DECOUPER.png')
    simplified, components, cut_vertices=svg_from_mask(cut,sheet_width_mm,
                min_area_px=max(40, (sheet_width_mm/180)*22),simplification=1.3, color='#000000')
    (directory/'planche_CONTOURS_12.svg').write_text(simplified,encoding='utf-8')
    # QA: draw red candidate cut lines on an opaque preview (not for Cricut import).
    composite=Image.new('RGBA',(w,h),(239,239,239,255))
    composite.alpha_composite(Image.fromarray(board,'RGBA'))
    qa=np.asarray(composite.convert('RGB')).copy()
    cs,_=cv2.findContours(cut,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(qa,cs,-1,(230,40,65),2)
    Image.fromarray(qa).save(directory/'planche_CONTROLE_CONTOURS.png')
    warnings=[]
    if components!=len(items):
        warnings.append(f'ATTENTION: {components} silhouettes trouvees pour {len(items)} illustrations. Une correction peut etre necessaire.')
    if paths>5000:
        warnings.append('ATTENTION: plus de 5000 chemins SVG; Cricut refuse potentiellement le fichier editable.')
    # Calques de couleur ne valent pas séparation sémantique des yeux/coquilles/etc.
    warnings.append('SVG editable regroupe par illustration/couleur, NON par concepts (corps/yeux/coquille).')
    return {'editable_svg':'planche_EDITABLE.svg',
            'print_then_cut_png':'planche_IMPRIMER_DECOUPER.png',
            'cut_contours_svg':'planche_CONTOURS_12.svg',
            'outline_qa_png':'planche_CONTROLE_CONTOURS.png',
            'artwork_groups':len(items),'vector_paths':paths,'cut_contours':components,
            'cut_vertices':cut_vertices,'border_mm':margin_mm,
            'sheet_width_mm':sheet_width_mm,'sheet_height_mm':round(sheet_width_mm*h/w,2),
            'per_illustration':masks_quality,'warnings':warnings}


def process_image(rgb, output_dir, *, layout='auto', intent='auto', ai_mode='auto', ai_masker=None,
                  width_mm=80, batch_limit=48, input_alpha=None, sheet_width_mm=180, margin_mm=1.5):
    """Process one uploaded source image; returns report & PIL preview.

    ai_masker accepts RGB ndarray and returns a [H,W] mask or raises on unavailable models.
    It is called selectively; rejected masks never overwrite original source.
    """
    assert rgb.ndim==3 and rgb.shape[2]==3
    if input_alpha is not None:
        input_alpha=np.asarray(input_alpha)
        if input_alpha.shape!=rgb.shape[:2]:
            raise ValueError('Le masque alpha ne correspond pas aux dimensions de l image')
    alpha_layout=detect_transparent_layout(input_alpha,layout) if layout in ('auto','planche') else None
    if alpha_layout is not None:
        boxes,layout_type=alpha_layout
    else:
        boxes,layout_type=detect_layout(rgb, layout)
    if len(boxes)>batch_limit: raise ValueError('Trop de vignettes : limite de securite de 48.')
    out=Path(output_dir).expanduser()
    out.mkdir(parents=True,exist_ok=True)
    root=out / ('SmartSVG_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    root.mkdir()
    results=[];previews=[];sheet_data=[]
    for index,(x0,y0,x1,y1) in enumerate(boxes,1):
        item=rgb[y0:y1,x0:x1].copy()
        name=f'element_{index:02d}'
        chosen=classify(item,intent)
        heuristic,quality=exterior_mask(item)
        if input_alpha is not None and np.min(input_alpha)<245:
            heuristic=np.asarray(input_alpha[y0:y1,x0:x1],dtype=np.uint8)
            quality={'reliable':True,'edge_consistency':1.0}
        ai_mask=None;ai_status='non_necessaire'
        must_call=ai_mode=='forcer' or (ai_mode=='auto' and not quality['reliable'])
        if must_call and ai_masker is not None:
            try:
                ai_mask=ai_masker(item)
                ai_status='inference_terminee'
            except Exception as e:
                ai_status='echec_IA:'+str(e)[:160]
        # In forced mode, a valid AI mask must actually be used. The upstream
        # V10 behavior always rejected AI on a clean background, making
        # 'forcer' ineffective for most cartoon stickers.
        use_reliable=(quality['reliable'] if ai_mode!='forcer' else False)
        mask,mask_source,mask_reason=consider_ai_mask(heuristic,ai_mask,item,use_reliable)
        if ai_mode=='desactiver': mask=heuristic;mask_source='sans_IA';mask_reason='IA_desactivee'
        if np.mean(mask>0)<.015:
            mask=np.ones(item.shape[:2],np.uint8)*255
            mask_source='sans_IA';mask_reason='masque_vide_rejete'
        im_rgba=np.dstack([item,mask]).astype(np.uint8)
        im=Image.fromarray(im_rgba,'RGBA')
        # Print Then Cut: keep source details; resize not applied.
        png_path=root/f'{name}_PRINT.png'
        im.save(png_path)
        colors={'logo':6,'cartoon':12,'illustration_complexe':20,'photo':12,'silhouette':2}.get(chosen,12)
        clean_layers = chosen!='illustration_complexe'
        svg_layers,metric_layers=vector_layers(item,mask,width_mm,colors,.65,clean=clean_layers)
        layer_path=root/f'{name}_COULEURS.svg'
        layer_path.write_text(svg_layers,encoding='utf-8')
        cutmask=foreground_silhouette(mask,width_mm)
        cut_svg,npaths,nverts=svg_from_mask(cutmask,width_mm,
                    min_area_px=max(4,(.35*item.shape[1]/max(width_mm,1))**2), simplification=max(.75,.3*item.shape[1]/max(width_mm,1)))
        cut_path=root/f'{name}_DECOUPE.svg'
        cut_path.write_text(cut_svg,encoding='utf-8')
        # print SVG uses PNG referenced? Never embed raster masquerading as editable SVG.
        preview=im.copy()
        previews.append((preview,name))
        sheet_data.append((index,(x0,y0,x1,y1),item,mask,svg_layers))
        dpi_eff=round(item.shape[1]*25.4/max(width_mm,1))
        issues=[]
        if metric_layers['paths']>300:issues.append('beaucoup_de_formes_pour_decoupe_multicouche')
        if metric_layers['paths']>5000:issues.append('depassement_potentiel_Cricut')
        if dpi_eff<150:issues.append('resolution_limitee_pour_impression_grand_format')
        if not quality['reliable'] and mask_source=='sans_IA':issues.append('detourage_a_verifier')
        result={'index':index,'bbox':[x0,y0,x1,y1],'classification':chosen,
                'ai_called':must_call,'ai_status':ai_status,'mask_used':mask_source,'mask_reason':mask_reason,
                'color_svg':layer_path.name,'cut_svg':cut_path.name,'print_png':png_path.name,
                'metrics':metric_layers,'cut_paths':npaths,'cut_vertices':nverts,
                'effective_print_dpi_at_width':dpi_eff,'warnings':issues}
        results.append(result)
    sheet_metrics = create_grouped_sheet(rgb, sheet_data, root, sheet_width_mm=sheet_width_mm, margin_mm=margin_mm)
    report={'version':'7.0-local-prototype','input_size':list(rgb.shape[1::-1]),
            'layout':layout_type,'elements':len(results),'output':str(root),'items':results,'sheet':sheet_metrics,
            'notes':['SVG_COULEURS = groupes par couleur, pas elements semantiques (oeil/coquille...).',
                     'SVG_DECOUPE = contour silhouette, non confondre avec des calques.' ,
                     'PNG_PRINT = dessin source detoure, a utiliser pour impression puis decoupe.',
                     'Les droits sur les illustrations source restent a verifier avant une vente.']}
    (root/'rapport.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    contact=make_contact_sheet(previews)
    contact.save(root/'apercu.png')
    return report,contact
