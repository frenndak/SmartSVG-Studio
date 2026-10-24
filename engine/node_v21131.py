"""V21.13.1: vector fidelity preview and click-to-select subject panel.

Existing nodes and outputs remain untouched. The new selection node creates
small in-memory previews only; clicks update its normal numeric widget and
require an explicit workflow re-run before manufacturing.
"""
from __future__ import annotations
import base64,copy,io,json
import cv2
import numpy as np
import torch
from PIL import Image
from .node_v2113 import (NODE_CLASS_MAPPINGS as OLD,
    NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES, SmartSVGChooseSubjectV2113,
    SmartSVGEditableColorsV2113)
from .smartsvg_vector.layers_v2113 import vectorize_flat_art,save_svg,VectorizationRefused
from .smartsvg_vector.qa_v21131 import analyse_svg,QualityRefused
from .smartsvg_compat.registry import merge_registry


def contact_sheet_previews(image,masks,*,max_bytes=500_000):
    """Return bounded real subject thumbnails, never crop original project files."""
    if not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1:
        return []
    if masks.ndim==2:masks=masks[None]
    h,w=image.shape[1:3]
    if tuple(masks.shape[1:])!=(h,w) or len(masks)>32 or h*w>5_000_000:return []
    src=np.uint8(np.rint(np.clip(image[0,:,:,:3].detach().cpu().numpy(),0,1)*255))
    result=[];used=0
    for i,m in enumerate(masks):
        b=np.uint8(m.detach().float().cpu().numpy()>=.5)
        points=cv2.findNonZero(b)
        if points is None:continue
        x,y,bw,bh=cv2.boundingRect(points)
        pad=max(3,int(max(bw,bh)*.06)); x0=max(0,x-pad);y0=max(0,y-pad)
        x1=min(w,x+bw+pad);y1=min(h,y+bh+pad)
        sample=src[y0:y1,x0:x1];sel=b[y0:y1,x0:x1]
        rw=max(1,round(sample.shape[1]*min(84/sample.shape[1],84/sample.shape[0])))
        rh=max(1,round(sample.shape[0]*min(84/sample.shape[1],84/sample.shape[0])))
        sample=cv2.resize(sample,(rw,rh),interpolation=cv2.INTER_AREA)
        sel=cv2.resize(sel,(rw,rh),interpolation=cv2.INTER_NEAREST)>0
        tile=np.full((88,88,3),234,np.uint8)
        oy=(88-rh)//2;ox=(88-rw)//2
        region=tile[oy:oy+rh,ox:ox+rw]
        region[sel]=sample[sel]
        with io.BytesIO() as buf:
            Image.fromarray(tile,'RGB').save(buf,format='PNG',optimize=True)
            enc=base64.b64encode(buf.getvalue()).decode('ascii')
        used+=len(enc)
        if used>max_bytes:break
        result.append({'numero':i+1,'image_data':'data:image/png;base64,'+enc})
    return result


class SmartSVGChooseSubjectV21131(SmartSVGChooseSubjectV2113):
    CATEGORY='SmartSVG / 01 CRÉER'
    def run(self,image,masques_objets,numero_sujet=1):
        response=super().run(image,masques_objets,numero_sujet)
        try:
            thumbs=contact_sheet_previews(image,masques_objets)
            response.setdefault('ui',{})['smartsvg_subjects_v21131']=[{
                'sujets':thumbs,'selection':int(numero_sujet),'clic_ne_fabrique_pas':True}]
            response['ui']['text'].append('Cliquer une vignette choisit le numéro ; relancer le workflow pour appliquer la sélection.')
        except (ValueError,TypeError,RuntimeError):
            # Missing previews must not fail a valid already computed mask.
            pass
        return response


class SmartSVGEditableColorsV21131(SmartSVGEditableColorsV2113):
    """Extra IMAGE carries the actual rendered-path comparison, not a mere quantized preview."""
    CATEGORY='SmartSVG / 03 VECTORISER'
    RETURN_TYPES=('IMAGE','IMAGE','STRING','STRING')
    RETURN_NAMES=('comparaison_svg','apercu_couleurs','fichier_svg_editable','rapport_qualite_json')
    @classmethod
    def INPUT_TYPES(cls):return copy.deepcopy(super().INPUT_TYPES())
    def run(self,image,couleurs=8,largeur_mm=40.,dossier_sortie='',masque_sujet=None):
        # Build once. Store only after all geometric checks have passed.
        if not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1 or image.shape[-1] not in (3,4):
            raise VectorizationRefused('IMAGE ComfyUI invalide')
        data=image[0].detach().cpu().float().numpy()
        if not np.isfinite(data).all() or data.min()<-.001 or data.max()>1.001:
            raise VectorizationRefused('IMAGE non finie ou hors 0..1')
        pixels=np.uint8(np.rint(np.clip(data,0,1)*255))
        if masque_sujet is None:
            if pixels.shape[-1]!=4:raise VectorizationRefused('Le masque du sujet est requis')
            mask=np.asarray(pixels[:,:,3],np.float32)/255.
        else:
            if not isinstance(masque_sujet,torch.Tensor) or masque_sujet.ndim not in (2,3):
                raise VectorizationRefused('MASK invalide')
            if masque_sujet.ndim==3 and masque_sujet.shape[0]!=1:
                raise VectorizationRefused('Sélectionner un seul sujet')
            mask=masque_sujet[0].detach().cpu().float().numpy() if masque_sujet.ndim==3 else masque_sujet.detach().cpu().float().numpy()
        xml,preview,audit=vectorize_flat_art(pixels,mask,colors=int(couleurs),width_mm=largeur_mm)
        try:comparison,qa=analyse_svg(pixels,mask,xml,audit)
        except QualityRefused as exc:raise VectorizationRefused('Le rendu SVG ne peut pas être vérifié : '+str(exc)) from exc
        filename=save_svg(xml,dossier_sortie)
        report={**audit,'comparaison_v21131':qa,'fichier_svg_editable':filename,
                'compatibilite_print_then_cut':'NE_PAS_UTILISER_A_LA_PLACE_DU_PNG',
                'certification_decoupe':False}
        return {'result':(torch.from_numpy(comparison.astype('float32')/255.)[None],
                    torch.from_numpy(preview.astype('float32')/255.)[None],
                    filename,json.dumps(report,ensure_ascii=False,allow_nan=False)),
                'ui':{'text':[f"SVG expérimental : {qa['formes_reconstruites']} formes contrôlées ; "
                        f"IoU silhouette ≈{qa['iou_silhouette_approx']:.3f}, "
                        f"erreur couleur ≈{qa['erreur_moyenne_couleurs_sur_recouvrement']:.1f}/255. "
                        'Inspection avant découpe indispensable.']}}

NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS=merge_registry(OLD,OLD_NAMES,{
 'SmartSVGChooseSubjectV21131':(SmartSVGChooseSubjectV21131,'01 · Choisir un sujet en cliquant son aperçu (V21.13.1)'),
 'SmartSVGEditableColorsV21131':(SmartSVGEditableColorsV21131,'03 · SVG multicouche + aperçu fidélité (V21.13.1)'),
})
