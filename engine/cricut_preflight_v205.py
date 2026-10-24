"""V20.5 Cricut: non-destructive SVG / PNG production preflight.
Outputs are warnings and preview, NEVER Cricut validation or geometry alterations.
"""
from __future__ import annotations
from pathlib import Path
from uuid import uuid4
import xml.etree.ElementTree as ET
import json, math, os, re, tempfile
import numpy as np
import cv2
from PIL import Image,ImageDraw
FORMATS={'A4':(210.,297.),'Letter':(215.9,279.4),'personnalise':None}
OPERATIONS=('imprimer_decouper_contour','decouper_contour_seul','decouper_tous_les_traits','dessiner_au_stylo','tout_preparer')
NAMES={'imprimer_decouper_contour':'01_IMPRIMER_PUIS_DECOUPER_UNIQUEMENT_CONTOUR.png','decouper_contour_seul':'02_DECOUPER_SEULEMENT_CONTOUR_EXTERIEUR.svg','decouper_tous_les_traits':'03_DECOUPER_CHAQUE_TRAIT.svg','dessiner_au_stylo':'04_DESSINER_LES_TRAITS_STYLO.svg'}
IA_NAMES={'imprimer_decouper_contour':'01_IMPRIMER_DECOUPER_CONTOUR_IA_A_VERIFIER.png','decouper_contour_seul':'02_DECOUPER_CONTOUR_IA_A_VERIFIER.svg'}
class CricutPreflightError(ValueError):pass

def _safe(root,path):
    root=Path(root).absolute();path=Path(path).absolute()
    try:path.relative_to(root)
    except ValueError as e:raise CricutPreflightError('Fichier hors du projet') from e
    for x in (root,path,*path.parents):
        if x.is_symlink():raise CricutPreflightError('Lien symbolique non autorise')
    if not path.is_file():raise CricutPreflightError('Fichier inexistant: '+path.name)
    return path

def _size(v):
    if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not (20<=v<=280):
        raise CricutPreflightError('Largeur physique invalide')
    return float(v)

def _png(path,width):
    if path.stat().st_size>65_000_000:raise CricutPreflightError('PNG trop volumineux')
    with Image.open(path) as im:
        w,h=im.size
        if not w or not h or w*h>20_000_000:raise CricutPreflightError('Dimensions PNG non acceptees')
        a=np.asarray(im.getchannel('A'),dtype=np.uint8) if 'A' in im.getbands() else np.full((h,w),255,np.uint8)
        rgb=np.asarray(im.convert('RGB'))
    opaque=(a>0).astype(np.uint8)
    n,labels,stats,_=cv2.connectedComponentsWithStats(opaque,8)
    cnt,tree=cv2.findContours(opaque*255,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    holes=sum(1 for x in tree[0] if x[3]>=0) if tree is not None else 0
    touch=bool(opaque[0].any() or opaque[-1].any() or opaque[:,0].any() or opaque[:,-1].any())
    density=round(25.4*w/width,1)
    measure={'format':'PNG','largeur_px':w,'hauteur_px':h,'largeur_estimee_mm':round(width,3),
             'hauteur_estimee_mm':round(width*h/w,3),'densite_estimee_ppp':density,
             'nombre_ilots':n-1,'nombre_trous_transparents':holes,'alpha_touche_bord':touch,
             'pixels_semi_transparents':int(np.count_nonzero((a>0)&(a<255)))}
    issues=[]
    if n==1:issues.append('PNG_ENTIEREMENT_TRANSPARENT')
    if np.all(opaque):issues.append('PNG_OPAQUE_RISQUE_DE_COUPE_RECTANGULAIRE')
    if n>2:issues.append('PLUSIEURS_ILOTS_POTENTIELLEMENT_DECOUPES')
    if holes:issues.append('TROUS_TRANSPARENTS_DECOUPE_INTERIEURE_POSSIBLE')
    if touch:issues.append('DECOUPE_TOUCHE_BORD_IMAGE')
    if density<150:issues.append('RESOLUTION_ESTIMEE_INFERIEURE_150_PPP')
    elif density<240:issues.append('RESOLUTION_ESTIMEE_INFERIEURE_240_PPP')
    return measure,issues,a,rgb

def _svg(path,operation):
    if path.stat().st_size>3_000_000:raise CricutPreflightError('SVG trop volumineux')
    raw=path.read_bytes();upper=raw.upper()
    if b'<!DOCTYPE' in upper or b'<!ENTITY' in upper:raise CricutPreflightError('DTD/entites SVG interdites')
    try:tree=ET.fromstring(raw)
    except ET.ParseError as e:raise CricutPreflightError('SVG XML invalide') from e
    if tree.tag.rsplit('}',1)[-1]!='svg':raise CricutPreflightError('Racine SVG incorrecte')
    def mm(x):
        if not isinstance(x,str) or not re.fullmatch(r'[0-9]+(?:\.[0-9]+)?mm',x):raise CricutPreflightError('Dimension mm manquante')
        y=float(x[:-2]);
        if not math.isfinite(y) or not .01<y<10000:raise CricutPreflightError('Dimension mm invalide')
        return y
    w,h=mm(tree.get('width')),mm(tree.get('height'))
    try:vb=[float(x) for x in re.split(r'[\s,]+',tree.get('viewBox','').strip())]
    except ValueError as e:raise CricutPreflightError('viewBox incorrect') from e
    if len(vb)!=4 or not all(map(math.isfinite,vb)) or min(vb[2:])<=0 or abs(w/h-vb[2]/vb[3])>.015:
        raise CricutPreflightError('viewBox proportions incoherentes')
    paths=[]
    for element in tree.iter():
        tag=element.tag.rsplit('}',1)[-1]
        if tag not in ('svg','path','g','title','desc'):raise CricutPreflightError('Element SVG interdit: '+tag)
        for key in element.attrib:
            if key.rsplit('}',1)[-1].lower() in ('href','onclick','onload','style'):
                raise CricutPreflightError('Attribut SVG non pris en charge')
        if tag=='path':
            d=element.get('d','')
            if len(d)>1_000_000 or not re.fullmatch(r'[0-9\-+.,\seEMmLlHhVvCcSsQqTtAaZz]*',d):
                raise CricutPreflightError('Path malforme')
            paths.append(d)
    subs=sum(len(re.findall('[Mm]',x)) for x in paths)
    closed=sum(len(re.findall('[Zz]',x)) for x in paths)
    if subs>50_000:raise CricutPreflightError('Trop de chemins')
    detail={'format':'SVG','largeur_mm':round(w,3),'hauteur_mm':round(h,3),'sous_chemins':subs,'fermetures':closed,'viewBox':vb}
    issues=[]
    if subs==0:issues.append('SVG_VIDE')
    if operation=='decouper_contour_seul':
        if subs>1:issues.append('CONTOUR_AVEC_PLUSIEURS_SOUS_CHEMINS')
        if closed<subs:issues.append('CONTOUR_EXTERIEUR_OUVERT')
    if operation=='decouper_tous_les_traits' and subs>=80:issues.append('NOMBREUX_CHEMINS_ATTENTION_PETITES_PIECES')
    if operation=='dessiner_au_stylo' and subs>1500:issues.append('STYLO_TROP_FRAGMENTE')
    return detail,issues

def _preview(alpha,rgb):
    h,w=alpha.shape;scale=min(1,850/w,900/h)
    size=max(1,round(w*scale)),max(1,round(h*scale))
    aa=cv2.resize(alpha,size,interpolation=cv2.INTER_NEAREST)
    rr=cv2.resize(rgb,size,interpolation=cv2.INTER_AREA)
    display=np.uint8((rr*(aa[...,None]/255.)+245*(1-aa[...,None]/255.)).clip(0,255))
    cnt,_=cv2.findContours(np.uint8(aa>0)*255,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(display,cnt,-1,(240,50,70),2)
    img=Image.new('RGB',(size[0],size[1]+42),'white');img.paste(Image.fromarray(display),(0,42))
    ImageDraw.Draw(img).text((10,12),'PREVOL CRICUT : CONTOUR CANDIDAT EN ROUGE - A VERIFIER',fill=(110,35,55))
    return img

def audit_project(root,operation='imprimer_decouper_contour',width_mm=90.,paper='A4',source='historique',chosen_file=None):
    root=Path(root).absolute()
    if not root.is_dir() or root.is_symlink():raise CricutPreflightError('Dossier projet non disponible')
    if operation not in OPERATIONS or paper not in FORMATS or source not in ('historique','ia_candidat'):
        raise CricutPreflightError('Operation, support ou source invalide')
    width=_size(width_mm);mode='imprimer_decouper_contour' if operation=='tout_preparer' else operation
    if chosen_file is not None:path=Path(chosen_file)
    elif source=='ia_candidat' and mode in IA_NAMES:path=root/'08_SEGMENTATION_IA_V20_2'/IA_NAMES[mode]
    else:path=root/'08_CHOIX_CRICUT'/NAMES[mode]
    path=_safe(root,path)
    card=_safe(root,root/'02_ZONE_UTILE'/'carte_redressee.png')
    with Image.open(card) as im:original_w=im.width
    if not original_w:raise CricutPreflightError('Largeur image originale incorrecte')
    preview=None
    if path.suffix.lower()=='.png':
        with Image.open(path) as im:scaled_width=width*im.width/original_w
        detail,issues,a,rgb=_png(path,scaled_width);preview=_preview(a,rgb)
    elif path.suffix.lower()=='.svg':detail,issues=_svg(path,mode)
    else:raise CricutPreflightError('Extension non prise en charge')
    ww=detail.get('largeur_estimee_mm',detail.get('largeur_mm'));hh=detail.get('hauteur_estimee_mm',detail.get('hauteur_mm'))
    if FORMATS[paper]:
        pw,ph=FORMATS[paper]
        if not ((ww<=pw and hh<=ph) or (ww<=ph and hh<=pw)):issues.append('DEPASSE_FORMAT_PAPIER')
    if mode=='imprimer_decouper_contour':issues.append('ZONE_PRINT_THEN_CUT_A_CONFIRMER_DANS_DESIGN_SPACE')
    if mode in ('imprimer_decouper_contour','decouper_contour_seul'):issues.append('SILHOUETTE_NON_CERTIFIEE')
    high={'PNG_ENTIEREMENT_TRANSPARENT','DECOUPE_TOUCHE_BORD_IMAGE','PLUSIEURS_ILOTS_POTENTIELLEMENT_DECOUPES','CONTOUR_EXTERIEUR_OUVERT','DEPASSE_FORMAT_PAPIER'}
    return {'version':'20.5-beta','statut':'RISQUE_ELEVE' if high.intersection(issues) else 'A_VERIFIER',
        'validation_humaine_obligatoire':True,'cricut_physique_testee':False,'import_design_space_effectue':False,
        'operation':operation,'fichier':str(path),'format_papier':paper,'largeur_originale_mm':width,
        'dimensions':detail,'avertissements':issues,'consigne':'Importer une seule variante; verifier dimensions et apercu dans Design Space.'},preview

def atomic_qa(root,report,preview):
    dest=Path(root).absolute()/'09_PREFLIGHT_CRICUT_V20_5'
    if dest.is_symlink():raise CricutPreflightError('Symlink QA interdit')
    dest.mkdir(exist_ok=True)
    suffix=uuid4().hex
    def write_atomic(target,callback):
        with tempfile.NamedTemporaryFile(dir=dest,prefix='.pending_cricut_',suffix=target.suffix,delete=False) as f:
            tmp=Path(f.name)
        try:callback(tmp);os.replace(tmp,target)
        finally:tmp.unlink(missing_ok=True)
    if preview is not None:
        image=dest/('apercu_'+suffix+'.png')
        write_atomic(image,lambda p:preview.save(p,format='PNG'))
        report['apercu']=str(image)
    target=dest/('rapport_'+suffix+'.json')
    write_atomic(target,lambda p:p.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8'))
    report['rapport_enregistre']=str(target)
    return report
