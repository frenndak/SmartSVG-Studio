"""SmartSVG V20.1.1 ComfyUI line-art specialization, preserving V20 aliases."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import torch
from .node_v20 import NODE_CLASS_MAPPINGS as BASE, NODE_DISPLAY_NAME_MAPPINGS as BASE_NAMES
from .lineart_v201 import process_lineart

class SmartSVGLineArtV201:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'image':('IMAGE',),
            'dossier_sortie':('STRING',{'default':r'C:\Users\Public\Documents\Cricut_SVG'}),
            'source':(['auto','scan','photo','capture_ecran','photo_ecran'],{'default':'auto'}),
            'cible_decoupe':(['carte','personnage','sticker'],{'default':'carte'}),
            'nettoyage':(['doux','fort'],{'default':'doux'}),
            'corriger_perspective':('BOOLEAN',{'default':True}),
            'marge_blanche_px':('INT',{'default':10,'min':0,'max':60,'step':1}),
        }}
    RETURN_TYPES=('IMAGE','STRING')
    RETURN_NAMES=('apercu_qa','rapport_export')
    FUNCTION='run'
    OUTPUT_NODE=True
    CATEGORY='SmartSVG / Cricut / Dessin'
    def run(self,image,dossier_sortie,source='auto',cible_decoupe='carte',nettoyage='doux',
            corriger_perspective=True,marge_blanche_px=10):
        if (not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1
                or image.shape[-1] not in (3,4)):
            raise ValueError('IMAGE ComfyUI [1,H,W,3/4] unique requise')
        pixels=image[0].detach().cpu().numpy()
        if not np.isfinite(pixels).all():
            raise ValueError('IMAGE: composantes non finies interdites')
        rgb=np.uint8(np.clip(pixels,0,1)*255+.5)
        if not dossier_sortie.strip():
            import folder_paths
            dossier_sortie=str(Path(folder_paths.get_output_directory())/'SmartSVG')
        result=process_lineart(rgb,dossier_sortie,source=source,target=cible_decoupe,
            mode=nettoyage,rectify=corriger_perspective,white_margin_px=marge_blanche_px)
        preview=torch.from_numpy(np.ascontiguousarray(result['preview'],dtype=np.float32)/255).unsqueeze(0)
        msg=json.dumps({'dossier':result['root'],'fichier_brouillon':result['image'],**result['report']},
                       ensure_ascii=False,indent=2)
        return {'ui':{'text':[msg]},'result':(preview,msg)}

class SmartSVGLineArtV2011(SmartSVGLineArtV201):
    """Alias de version corrective, widgets inchangés pour workflows précédents."""
    pass

NODE_CLASS_MAPPINGS={**BASE,'SmartSVGLineArtV201':SmartSVGLineArtV201,
                    'SmartSVGLineArtV2011':SmartSVGLineArtV2011}
NODE_DISPLAY_NAME_MAPPINGS={**BASE_NAMES,
    'SmartSVGLineArtV201':'SmartSVG V20.1 - Photo / Scan de dessin (line-art)',
    'SmartSVGLineArtV2011':'SmartSVG V20.1.1 - Photo / Scan de dessin (line-art corrigé)'}

