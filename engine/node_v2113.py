"""V21.13 selection + genuine editable vector layers (experimental)."""
from __future__ import annotations
import copy,json
import numpy as np
import torch
from .node_v21122 import NODE_CLASS_MAPPINGS as OLD,NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .smartsvg_compat.registry import merge_registry
from .smartsvg_vector.layers_v2113 import vectorize_flat_art, save_svg, VectorizationRefused


def select_subject(image,masks,index):
    if not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1 or image.shape[-1] not in (3,4):
        raise ValueError('Image IMAGE [1,H,W,3/4] requise')
    if not isinstance(masks,torch.Tensor) or masks.ndim not in (2,3) or masks.dtype not in (torch.float16,torch.float32,torch.float64):
        raise ValueError('Entrée MASK [N,H,W] requise')
    if masks.ndim==2:masks=masks[None]
    if tuple(masks.shape[1:])!=tuple(image.shape[1:3]) or masks.shape[0]>32:
        raise ValueError('Dimensions du masque différentes de celles de l’image ou plus de 32 sujets')
    if not isinstance(index,int) or isinstance(index,bool) or not 1<=index<=masks.shape[0]:
        raise ValueError(f'Indice de sujet hors limites 1..{masks.shape[0]}')
    mask=masks[index-1:index].detach().float().cpu()
    if not torch.isfinite(mask).all() or mask.min()<0 or mask.max()>1:
        raise ValueError('Masque non fini ou hors [0,1]')
    binary=np.uint8(mask[0].numpy()>=.5)
    import cv2
    n,lab,stats,_=cv2.connectedComponentsWithStats(binary,8)
    parts=[int(stats[i,cv2.CC_STAT_AREA]) for i in range(1,n) if stats[i,cv2.CC_STAT_AREA]>=8]
    area=int(binary.sum())
    if area<50 or area>binary.size*.94:raise ValueError('Masque vide ou couvrant presque toute l’image')
    report={'version':'21.13','indice_selectionne':index,'sujets_disponibles':int(masks.shape[0]),
            'surface_sujet_px':area,'nombre_fragments_8px_ou_plus':len(parts),
            'surface_fragments_px':sorted(parts,reverse=True),
            'fragments_detaches_a_verifier':len(parts)>1,
            'message':'Les îlots sont préservés, pas effacés silencieusement.'}
    return mask,report

class SmartSVGChooseSubjectV2113:
    CATEGORY='SmartSVG / 01 CRÉER'
    FUNCTION='run'
    RETURN_TYPES=('MASK','IMAGE','STRING')
    RETURN_NAMES=('masque_sujet','image_source','rapport_selection')
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'image':('IMAGE',),'masques_objets':('MASK',),
                            'numero_sujet':('INT',{'default':1,'min':1,'max':32,'step':1})}}
    def run(self,image,masques_objets,numero_sujet=1):
        mask,info=select_subject(image,masques_objets,numero_sujet)
        return {'result':(mask,image,json.dumps(info,ensure_ascii=False,allow_nan=False)),
                'ui':{'text':[f"Sujet {numero_sujet}/{info['sujets_disponibles']} sélectionné · {info['nombre_fragments_8px_ou_plus']} élément(s) séparé(s), à vérifier."]}}

class SmartSVGEditableColorsV2113:
    CATEGORY='SmartSVG / 03 VECTORISER'
    FUNCTION='run'
    RETURN_TYPES=('IMAGE','STRING','STRING')
    RETURN_NAMES=('apercu_couleurs','fichier_svg_editable','rapport_vectorisation')
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'image':('IMAGE',),
            'couleurs':('INT',{'default':8,'min':2,'max':16,'step':1}),
            'largeur_mm':('FLOAT',{'default':40.,'min':5.,'max':300.,'step':1.}),
            'dossier_sortie':('STRING',{'default':'','multiline':False,
               'tooltip':'Laisser vide pour utiliser ComfyUI/output/SmartSVG_Studio/SVG_Multicouche.'})},
            'optional':{'masque_sujet':('MASK',)}}
    def run(self,image,couleurs=8,largeur_mm=40.,dossier_sortie='',masque_sujet=None):
        if not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1 or image.shape[-1] not in (3,4):
            raise VectorizationRefused('Image ComfyUI [1,H,W,RGB(A)] requise')
        array=image[0].detach().float().cpu().numpy()
        if not np.isfinite(array).all() or array.min()<-.001 or array.max()>1.001:
            raise VectorizationRefused('Valeurs IMAGE incorrectes')
        rgb=np.uint8(np.rint(np.clip(array,0,1)*255))
        mask=None
        if masque_sujet is not None:
            if not isinstance(masque_sujet,torch.Tensor) or masque_sujet.ndim not in (2,3):
                raise VectorizationRefused('Masque ComfyUI invalide')
            if masque_sujet.ndim==3 and masque_sujet.shape[0]!=1:
                raise VectorizationRefused('Sélectionner d’abord un seul sujet avec SmartSVGChooseSubjectV2113')
            mask=masque_sujet[0].detach().float().cpu().numpy() if masque_sujet.ndim==3 else masque_sujet.detach().float().cpu().numpy()
        xml,preview,audit=vectorize_flat_art(rgb,mask,colors=int(couleurs),width_mm=largeur_mm)
        path=save_svg(xml,dossier_sortie)
        audit['fichier_svg_editable']=path
        return {'result':(torch.from_numpy(np.ascontiguousarray(preview,dtype=np.float32)/255.)[None],path,
                          json.dumps(audit,ensure_ascii=False,allow_nan=False)),
                'ui':{'text':[f"SVG MULTICOUCHE EXPÉRIMENTAL : {audit['calques_couleur']} couleurs, {audit['formes']} formes. Vérifier et éditer dans Inkscape ; ne remplace pas Print Then Cut."]}}

NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS=merge_registry(OLD,OLD_NAMES,{
    'SmartSVGChooseSubjectV2113':(SmartSVGChooseSubjectV2113,'01 · Choisir un sujet (et conserver ses fragments)'),
    'SmartSVGEditableColorsV2113':(SmartSVGEditableColorsV2113,'03 · SVG couleurs éditables — expérimental'),
})
