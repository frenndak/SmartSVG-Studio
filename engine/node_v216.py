"""V21.6: brush-mask editor feeding the unchanged Express V21.5.1 engine."""
from __future__ import annotations
import json
import numpy as np
import torch
from .node_v2151 import NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .smartsvg_compat.registry import merge_registry
from .smartsvg_editor.strokes import StrokeError, decode, edit_fingerprint, apply_strokes, MAX_INSTANCES, MAX_PIXELS, MAX_TOTAL_MASK_PIXELS
from .smartsvg_editor.previews import publish


def _output_directory():
    try:
        import folder_paths
        return folder_paths.get_output_directory()
    except (ImportError, AttributeError, RuntimeError):
        return None


class SmartSVGMaskEditorV216:
    """Source image + optional N mask instances -> edited N masks, preserving floats."""
    CATEGORY='SmartSVG / 01 CRÉER'
    RETURN_TYPES=('MASK','IMAGE','STRING')
    RETURN_NAMES=('masques_corriges','image_source','diagnostic_retouches')
    FUNCTION='run'
    OUTPUT_NODE=True  # permits first preview/edit pass with downstream Express muted
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'image':('IMAGE',),
            'retouches_json':('STRING',{'default':'','multiline':True,'tooltip':'Sauvegarde automatique des traits via l’éditeur graphique. Ne pas éditer manuellement.'}),
        }, 'optional':{'masque_base':('MASK',)}}

    def run(self,image,retouches_json='',masque_base=None):
        if not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1 or image.shape[-1] not in (3,4):
            raise StrokeError('Retouche V21.6 : IMAGE attendue [1,H,W,RGB/RGBA]')
        h,w=int(image.shape[1]),int(image.shape[2])
        if h<1 or w<1 or h*w>MAX_PIXELS:
            raise StrokeError('Retouche V21.6 : image > 5 Mp ; réduire la source avant le nœud')
        rgb=image[0].detach().float().cpu().numpy()
        if masque_base is None:
            base=np.zeros((1,h,w),dtype=np.float32)
        else:
            if not isinstance(masque_base,torch.Tensor) or masque_base.ndim!=3:
                raise StrokeError('Retouche V21.6 : MASK attendu [N,H,W]')
            if tuple(masque_base.shape[1:])!=(h,w) or not 1<=masque_base.shape[0]<=MAX_INSTANCES:
                raise StrokeError('Retouche V21.6 : masque de taille différente / plus de 32 sujets')
            if masque_base.numel()>MAX_TOTAL_MASK_PIXELS:
                raise StrokeError('Retouche V21.6 : trop de pixels de masques (50 millions) ; réduire la source ou séparer les lots')
            base=masque_base.detach().float().cpu().numpy()
        fingerprint=edit_fingerprint(rgb,base)
        strokes=decode(retouches_json,width=w,height=h,count=len(base),fingerprint=fingerprint)
        corrected=apply_strokes(base,strokes)
        dest=masque_base.device if masque_base is not None else image.device
        tensor=torch.from_numpy(corrected).to(device=dest)
        info={'version':'21.6','nombre_masques':len(base),'largeur_px':w,'hauteur_px':h,
              'traits_appliques':len(strokes),'source_sha256':fingerprint,
              'correction_enregistree':bool(strokes),'masque_vide':not bool(np.any(corrected > 0.001)), 'validation_cricut':False}
        result={'result':(tensor,image,json.dumps(info,ensure_ascii=False))}
        try:
            refs=publish(rgb,base,_output_directory())
            note='ATTENTION : aucun pixel retenu dans le masque. Dessiner la sélection avant export.' if info['masque_vide'] else 'Masques prêts pour inspection avant export.'
            result['ui']={'text':[f'Editeur V21.6 : {len(base)} masque(s), {len(strokes)} trait(s). {note}'],
                          'smartsvg_editor':[{'version':1,'width':w,'height':h,'count':len(base),'source':fingerprint,
                                              **(refs or {})}]}
        except Exception:
            # Display is optional, NEVER turn successful corrected masks into a failed job.
            result['ui']={'text':['Masques corrigés produits. Aperçu éditeur indisponible.'], 'smartsvg_editor':[]}
        return result


NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS=merge_registry(OLD,OLD_NAMES,{
    'SmartSVGMaskEditorV216':(SmartSVGMaskEditorV216,'01 · SmartSVG V21.6 — corriger masques / contours'),
})
