"""V20.1.2: choose the Cricut operation; old node IDs stay supported."""
from __future__ import annotations
import json
from pathlib import Path

import numpy as np
import torch
from .node_v201 import NODE_CLASS_MAPPINGS as BASE, NODE_DISPLAY_NAME_MAPPINGS as BASE_NAMES
from .cricut_choice_v2012 import OPTIONS, process_choice

class SmartSVGLineArtV2012:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'image':('IMAGE',),
            'dossier_sortie':('STRING',{'default':r'C:\Users\Public\Documents\Cricut_SVG'}),
            'source':(['auto','scan','photo','capture_ecran','photo_ecran'],{'default':'auto'}),
            'cible_decoupe':(['carte','personnage','sticker'],{'default':'sticker'}),
            'operation_cricut':(list(OPTIONS),{'default':'imprimer_decouper_contour'}),
            'nettoyage':(['doux','fort'],{'default':'doux'}),
            'corriger_perspective':('BOOLEAN',{'default':True}),
            'marge_blanche_px':('INT',{'default':10,'min':0,'max':60,'step':1}),
            'largeur_finale_mm':('INT',{'default':90,'min':20,'max':280,'step':1}),
        }}
    RETURN_TYPES=('IMAGE','STRING')
    RETURN_NAMES=('apercu_qa','rapport_export')
    FUNCTION='run'
    OUTPUT_NODE=True
    CATEGORY='SmartSVG / Cricut / Dessin'

    def run(self,image,dossier_sortie,source='auto',cible_decoupe='sticker',
            operation_cricut='imprimer_decouper_contour',nettoyage='doux',
            corriger_perspective=True,marge_blanche_px=10,largeur_finale_mm=90):
        if (not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1 or
                image.shape[-1] not in (3,4)):
            raise ValueError('IMAGE ComfyUI [1,H,W,3/4] unique requise')
        pixels=image[0].detach().cpu().numpy()
        if not np.isfinite(pixels).all():raise ValueError('IMAGE: pixels non finis')
        a=np.uint8(np.clip(pixels,0,1)*255+.5)
        if not dossier_sortie.strip():
            import folder_paths
            dossier_sortie=str(Path(folder_paths.get_output_directory())/'SmartSVG')
        result=process_choice(a,dossier_sortie,source=source,target=cible_decoupe,
                              operation=operation_cricut,mode=nettoyage,
                              rectify=corriger_perspective,white_margin_px=marge_blanche_px,
                              width_mm=largeur_finale_mm)
        preview=torch.from_numpy(np.ascontiguousarray(result['preview'],dtype=np.float32)/255).unsqueeze(0)
        info={**result['choice_report'], 'dossier':result['root'],
              'dossier_choix':result['cricut_root'],
              'fichier_recommande':result['recommended_file'],
              'rapport_lineart':result['report']}
        msg=json.dumps(info,ensure_ascii=False,indent=2)
        return {'ui':{'text':[msg]},'result':(preview,msg)}

NODE_CLASS_MAPPINGS={**BASE,'SmartSVGLineArtV2012':SmartSVGLineArtV2012}
NODE_DISPLAY_NAME_MAPPINGS={**BASE_NAMES,
    'SmartSVGLineArtV2012':'SmartSVG V20.1.2 - Choix de decoupe Cricut / Stylo'}
