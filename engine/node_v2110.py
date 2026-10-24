"""V21.10: native-resolution inspection and reversible brush corrections in one ComfyUI node.

The optional GUI publication and QA hints never change the manufacturing tensor or
conceal a failed edit replay. Older node IDs/workflows remain registered unchanged.
"""
from __future__ import annotations
import json
import math
import numpy as np
import torch
from .node_v219 import NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .node_v216 import _output_directory
from .smartsvg_compat.registry import merge_registry
from .smartsvg_editor.strokes import (StrokeError,decode,edit_fingerprint,apply_strokes,
                                      MAX_PIXELS,MAX_INSTANCES,MAX_TOTAL_MASK_PIXELS)
from .smartsvg_native.inspector import analyse, publish_native


class SmartSVGUnifiedEditorV2110:
    """One input, one modal: base mask + saved strokes -> native edited mask + QA."""
    CATEGORY='SmartSVG / 01 CRÉER'
    RETURN_TYPES=('MASK','IMAGE','STRING')
    RETURN_NAMES=('masques_corriges','image_source','diagnostic_json')
    FUNCTION='run'
    OUTPUT_NODE=True

    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'image':('IMAGE',),
            'retouches_json':('STRING',{'default':'','multiline':True,
                                      'tooltip':'Enregistré par le panneau graphique V21.10 ; ne pas modifier manuellement.'}),
        },'optional':{'masque_base':('MASK',)}}

    def run(self,image,retouches_json='',masque_base=None,*,_qa_width_mm=40.,_qa_real=False):
        if isinstance(_qa_width_mm,bool) or not isinstance(_qa_width_mm,(int,float)) or not math.isfinite(_qa_width_mm) or not 5<=_qa_width_mm<=300:
            raise StrokeError('Largeur QA non valide : 5 à 300 mm')
        if not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1 or image.shape[-1] not in (3,4):
            raise StrokeError('V21.10 : source IMAGE [1,H,W,RGB(A)] requise')
        h,w=int(image.shape[1]),int(image.shape[2])
        if not (h>0 and w>0 and h*w<=MAX_PIXELS):
            raise StrokeError('V21.10 : source limitée à 5 Mp')
        if masque_base is None:
            base=np.zeros((1,h,w),dtype=np.float32)
        else:
            if not isinstance(masque_base,torch.Tensor) or masque_base.ndim!=3 or tuple(masque_base.shape[1:])!=(h,w) or not 1<=masque_base.shape[0]<=MAX_INSTANCES or masque_base.numel()>MAX_TOTAL_MASK_PIXELS:
                raise StrokeError('V21.10 : MASK [N,H,W] aligné, maximum 32 sujets / 50 Mp cumulés')
            base=masque_base.detach().float().cpu().numpy()
        source=image[0].detach().float().cpu().numpy()
        fingerprint=edit_fingerprint(source,base)
        strokes=decode(retouches_json,width=w,height=h,count=len(base),fingerprint=fingerprint)
        corrected=apply_strokes(base,strokes)
        device=masque_base.device if masque_base is not None else image.device
        tensor=torch.from_numpy(corrected).to(device=device)
        info={'version':'21.10','largeur_px':w,'hauteur_px':h,'nombre_masques':len(base),
              'traits_appliques':len(strokes),'empreinte_source':fingerprint,
              'masque_vide':not bool(np.any(corrected>=.5)),'largeur_qa_hypothese_mm':None if _qa_real else 40.0,'largeur_qa_mm':float(_qa_width_mm),'largeur_export_reelle_mm_connue':bool(_qa_real),
              'validation_cricut_physique':False,'inspection':'indisponible'}
        ui={'smartsvg_unified':[],'text':[]}
        # Drawing/quality status is advisory. GUI problems cannot invalidate masks.
        try:
            report=analyse(source,corrected,width_mm=_qa_width_mm)
            info['inspection']=report['statut']
            info['alertes_par_sujet']=[len(o['alertes']) for o in report['objets']]
        except Exception:
            report=None
            ui['text'].append('Diagnostic de contour indisponible ; masque corrigé conservé.')
        try:
            # Publish BASE masks, not corrected masks: browser replays all saved
            # strokes exactly once. Otherwise saving and rerunning doubles edits.
            refs=publish_native(source,base,_output_directory())
            if refs:
                objects=report['objets'] if report is not None else [
                    {'objet':i+1,'etat':'a_verifier','alertes':[],'points':[]}
                    for i in range(len(base))]
                ui['smartsvg_unified']=[{
                    'version':1,'width':w,'height':h,'count':len(base),'source':fingerprint,
                    'image':refs['image'],'masks':refs['masks'],'objects':objects,
                    'quality':info['inspection'],'qa_width_mm':float(_qa_width_mm),'real_size':bool(_qa_real)}]
            else:ui['text'].append('Aperçu natif indisponible ; retouches et fichiers de fabrication préservés.')
        except Exception:
            ui['text'].append('Affichage indisponible ; masques corrigés préservés.')
        qa_message=(f'seuils en mm basés sur la largeur réelle {_qa_width_mm:g} mm, à transmettre à Express.'
                    if _qa_real else 'seuils en mm basés sur 40 mm hypothétiques, non sur la largeur Express.')
        ui['text'].insert(0,f"V21.10 : {len(base)} sujet(s), {len(strokes)} retouche(s), diagnostic {info['inspection']} ; {qa_message}")
        return {'result':(tensor,image,json.dumps(info,ensure_ascii=False,allow_nan=False)),'ui':ui}


NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS=merge_registry(OLD,OLD_NAMES,{
    'SmartSVGUnifiedEditorV2110':(SmartSVGUnifiedEditorV2110,'01 · SmartSVG V21.10 — corriger + inspecter (natif)')
})
