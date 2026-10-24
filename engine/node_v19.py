"""V19 ComfyUI scene dispatcher; old stickers path stays on proven V18.1.

Segmentation models themselves remain provider nodes (SAM/Florence-2/Segment
in ComfyUI-RMBG). A connected MASK is consumed as source-space mask(s).
With no mask, optional registered RMBG supplies foreground-only extraction.
"""
from pathlib import Path
import gc
import numpy as np
import torch
import cv2
from .node_v181 import (SmartSVGStudioV181Expert, SmartSVGStudioV181Express,
                        NODE_CLASS_MAPPINGS as LEGACY_MAPPING,
                        NODE_DISPLAY_NAME_MAPPINGS as LEGACY_DISPLAY)
from .photo_v19 import process_photo


def _arr_image(image,mask_png=None):
    if image.ndim!=4 or image.shape[0]!=1 or image.shape[-1]<3:
        raise ValueError('Une image [1,H,W,3+] attendue')
    arr=np.uint8(np.clip(image[0].detach().cpu().numpy()[...,:3],0,1)*255+.5)
    alpha=None
    if mask_png is not None:
        if mask_png.ndim!=3 or mask_png.shape[0]!=1:
            raise ValueError('Le MASK LoadImage doit etre [1,H,W]')
        alpha=1-np.clip(mask_png[0].detach().cpu().numpy(),0,1)
        if alpha.shape!=arr.shape[:2]:raise ValueError('Masque PNG non aligne avec image')
        alpha=np.uint8(alpha*255+.5)
    return arr,alpha


def _detect_scene(rgb,alpha=None):
    h,w=rgb.shape[:2]
    if alpha is not None and np.mean(alpha<245)>.005:
        return 'stickers'
    # Conservative full-bleed photo/illustration detection; otherwise try legacy.
    if h*w>=300_000:
        small=cv2.resize(rgb,(96,96),interpolation=cv2.INTER_AREA)
        edges=np.concatenate([small[0],small[-1],small[:,0],small[:,-1]])
        white_fraction=float(np.mean(np.min(edges,axis=1)>235))
        if white_fraction<.25:return 'photo'
    return 'stickers'


class SmartSVGStudioV19Expert(SmartSVGStudioV181Expert):
    @classmethod
    def INPUT_TYPES(cls):
        old=super().INPUT_TYPES();d=dict(old['required']); opt=dict(old['optional'])
        d['type_fichier']=(['auto','stickers','photo'],{'default':'auto'})
        d['strategie_photo']=(['auto','masques_requis','boites_guidees','analyse_seule'],{'default':'auto'})
        d['boites_objets_json']=('STRING',{'default':'','multiline':True})
        return {'required':d,'optional':opt}

    def execute(self,image,dossier_sortie,type_entree='auto',type_creation='auto',ia_locale='auto',
                largeur_planche_mm=180,marge_sticker_mm=1.5,couleurs_svg_simplifie=10,
                mode_objets='auto',noms_objets='',repere_masques='planche',transformation_masques_json='',
                type_fichier='auto',strategie_photo='auto',boites_objets_json='',
                masque_png=None,masques_objets=None):
        rgb,alpha=_arr_image(image,masque_png)
        route=_detect_scene(rgb,alpha) if type_fichier=='auto' else type_fichier
        if route=='stickers':
            # Existing V18.1 print+cut production, no behavioral changes.
            return super().execute(image,dossier_sortie,type_entree=type_entree,type_creation=type_creation,
                        ia_locale=ia_locale,largeur_planche_mm=largeur_planche_mm,
                        marge_sticker_mm=marge_sticker_mm,couleurs_svg_simplifie=couleurs_svg_simplifie,
                        mode_objets=mode_objets,noms_objets=noms_objets,repere_masques=repere_masques,
                        transformation_masques_json=transformation_masques_json,
                        masque_png=masque_png,masques_objets=masques_objets)
        dest=str(dossier_sortie).strip()
        if not dest:
            import folder_paths
            dest=str(Path(folder_paths.get_output_directory())/'SmartSVG')
        ext=masques_objets.detach().cpu().numpy() if masques_objets is not None else None
        self._rmbg_stats=[]
        provider=None
        if strategie_photo=='auto' and ext is None and ia_locale!='desactiver':
            # RMBG: foreground-only, not actual recognition of constituent objects.
            provider=self._rmbg_mask
        try:
            result,preview=process_photo(rgb,dest,masks=ext,labels=noms_objets,
                boxes_json=boites_objets_json,mode=strategie_photo,foreground_provider=provider,
                alpha=alpha,width_mm=largeur_planche_mm,white_offset_mm=marge_sticker_mm,
                mask_origin='MASK_ComfyUI_source',require_provider=(ia_locale=='forcer' and ext is None))
        finally:
            self._rmbg_backend=None;self._rmbg_backend_class=None
            gc.collect()
            if torch.cuda.is_available():torch.cuda.empty_cache()
        qa=result['audit_v19']
        summary=(f'SmartSVG V19.1 Photo : {qa["nombre_objets_extraits"]} objet(s) exporte(s).\n'
                 f'Statut : {qa["statut"]}.\n'
                 f'Dossier : {result["output"]}\n'
                 'PNG originaux conserves; masques et transparences a examiner.\n'
                 'L extraction RMBG seule ne separe PAS automatiquement les objets semantiques.\n'
                 +('ATTENTION : '+' | '.join(qa['avertissements']) if qa['avertissements'] else ''))
        tensor=torch.from_numpy(np.asarray(preview,np.float32).copy()/255).unsqueeze(0)
        return tensor,summary

class SmartSVGStudioV19Express(SmartSVGStudioV19Expert):
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'image':('IMAGE',),
            'dossier_sortie':('STRING',{'default':r'C:\Users\Public\Documents\Cricut_SVG','multiline':False}),
            'largeur_planche_mm':('INT',{'default':180,'min':30,'max':290,'step':5}),
            'type_fichier':(['auto','stickers','photo'],{'default':'auto'}),
            'ia_locale':(['auto','forcer','desactiver'],{'default':'auto'})},
            'optional':{'masque_png':('MASK',),'masques_objets':('MASK',)}}
    FUNCTION='execute_express'
    OUTPUT_NODE=True
    CATEGORY='SmartSVG / Cricut'
    def execute_express(self,image,dossier_sortie,largeur_planche_mm=180,type_fichier='auto',
                       ia_locale='auto',masque_png=None,masques_objets=None):
        return self.execute(image,dossier_sortie,largeur_planche_mm=largeur_planche_mm,
                type_fichier=type_fichier,ia_locale=ia_locale,masque_png=masque_png,
                masques_objets=masques_objets)

NODE_CLASS_MAPPINGS={**LEGACY_MAPPING,
    'SmartSVGStudioV19Express':SmartSVGStudioV19Express,
    'SmartSVGStudioV19Expert':SmartSVGStudioV19Expert}
NODE_DISPLAY_NAME_MAPPINGS={**LEGACY_DISPLAY,
    'SmartSVGStudioV19Express':'SmartSVG V19 Express — Cricut et photos',
    'SmartSVGStudioV19Expert':'SmartSVG V19 Expert — extraction photo par masques'}


# V19.1 aliases keep existing V19 workflows valid while offering an explicitly
# versioned node class for new graphs. No duplicate plugin installation needed.
class SmartSVGStudioV191Expert(SmartSVGStudioV19Expert):
    pass

class SmartSVGStudioV191Express(SmartSVGStudioV19Express):
    pass

NODE_CLASS_MAPPINGS.update({
    'SmartSVGStudioV191Express':SmartSVGStudioV191Express,
    'SmartSVGStudioV191Expert':SmartSVGStudioV191Expert,
})
NODE_DISPLAY_NAME_MAPPINGS.update({
    'SmartSVGStudioV191Express':'SmartSVG V19.1 Express — Cricut / photos corrige',
    'SmartSVGStudioV191Expert':'SmartSVG V19.1 Expert — masques objets / contours corriges',
})
