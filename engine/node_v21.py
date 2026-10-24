"""V21: one simple node; optional MASK batch, explicit local SAM2 toggle.

Legacy aliases and expert nodes are inherited unchanged from V20.6.
"""
import json
from pathlib import Path
import numpy as np
import torch
from .node_v206 import NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .multi_subject_v21 import run_v21,V21Error,SEGMENTATION
from .hd_multisticker_v206 import PRESETS,CUTS,DPI

class SmartSVGSimpleV21:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'image':('IMAGE',),
            'dossier_sortie':('STRING',{'default':r'C:\Users\Public\Documents\Cricut_SVG'}),
            'profil':(list(PRESETS),{'default':'auto'}),
            'operation':(list(CUTS),{'default':'sticker_contour'}),
            'largeur_mm':('FLOAT',{'default':40.,'min':15.,'max':180.,'step':1.}),
            'qualite_ppp':(list(map(str,DPI)),{'default':'300'}),
            'grille_multi':(['6x4','4x3','3x3','auto'],{'default':'6x4'}),
            'segmentation_ia':(list(SEGMENTATION),{'default':'desactiver'}),
        },'optional':{
            'masques_objets':('MASK',),
        }}
    RETURN_TYPES=('IMAGE','STRING')
    RETURN_NAMES=('apercu','rapport')
    FUNCTION='run';OUTPUT_NODE=True;CATEGORY='SmartSVG / Cricut / V21'

    def run(self,image,dossier_sortie,profil='auto',operation='sticker_contour',
            largeur_mm=40.,qualite_ppp='300',grille_multi='6x4',
            segmentation_ia='desactiver',masques_objets=None):
        if not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1 or image.shape[-1] not in (3,4):
            raise V21Error('IMAGE [1,H,W,3/4] requise')
        # Reject oversized images before their conversion to CPU/PIL.
        if image.shape[1]*image.shape[2]>20_000_000:raise V21Error('Source trop grande')
        raw=image[0].detach().cpu().numpy()
        if not np.isfinite(raw).all() or raw.min()<-.001 or raw.max()>1.001:
            raise V21Error('Valeurs image invalides')
        pixels=np.uint8(np.clip(raw,0,1)*255+.5)
        if not str(dossier_sortie).strip():
            import folder_paths
            dossier_sortie=str(Path(folder_paths.get_output_directory())/'SmartSVG')
        # For internal segmentation, RMBG runs only upon explicit selection.
        report,preview=run_v21(pixels,dossier_sortie,profil,float(largeur_mm),
                               int(qualite_ppp),operation,grille_multi,
                               segmentation=segmentation_ia,masks=masques_objets)
        arr=np.asarray(preview.convert('RGB'),np.float32)/255.
        tensor=torch.from_numpy(np.ascontiguousarray(arr))[None]
        msg=json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)
        return {'ui':{'text':[msg]},'result':(tensor,msg)}

NODE_CLASS_MAPPINGS={**OLD,'SmartSVGSimpleV21':SmartSVGSimpleV21}
NODE_DISPLAY_NAME_MAPPINGS={**OLD_NAMES,
    'SmartSVGSimpleV21':'SmartSVG V21 - Simple HD / sujets / planches (MASK optionnel)'}
