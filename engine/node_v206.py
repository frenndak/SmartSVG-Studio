"""Simple, independent V20.6 HD / multi-sticker node, retaining V20.5 nodes."""
import json
from pathlib import Path
import numpy as np
import torch
from .node_v205 import NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .hd_multisticker_v206 import run_v206,PRESETS,CUTS,DPI,ExportError

class SmartSVGSimpleV206:
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
        }}
    RETURN_TYPES=('IMAGE','STRING')
    RETURN_NAMES=('apercu','rapport')
    FUNCTION='run';OUTPUT_NODE=True;CATEGORY='SmartSVG / Cricut / Simple V20.6'
    def run(self,image,dossier_sortie,profil='auto',operation='sticker_contour',largeur_mm=40.,qualite_ppp='300',grille_multi='6x4'):
        if not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1 or image.shape[-1] not in (3,4):
            raise ExportError('Une seule IMAGE ComfyUI [1,H,W,3/4] est requise')
        raw=image[0].detach().cpu().numpy()
        if not np.isfinite(raw).all() or raw.min()<-0.001 or raw.max()>1.001:
            raise ExportError('Valeurs IMAGE invalides (NaN, infini ou hors 0..1)')
        data=np.uint8(np.clip(raw,0,1)*255+.5)
        if not str(dossier_sortie).strip():
            import folder_paths
            dossier_sortie=str(Path(folder_paths.get_output_directory())/'SmartSVG')
        report,preview=run_v206(data,dossier_sortie,profil,float(largeur_mm),int(qualite_ppp),operation,grille_multi)
        arr=np.asarray(preview.convert('RGB'),dtype=np.float32)/255.
        tensor=torch.from_numpy(np.ascontiguousarray(arr))[None]
        msg=json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)
        return {'ui':{'text':[msg]},'result':(tensor,msg)}

NODE_CLASS_MAPPINGS={**OLD,'SmartSVGSimpleV206':SmartSVGSimpleV206}
NODE_DISPLAY_NAME_MAPPINGS={**OLD_NAMES,'SmartSVGSimpleV206':'SmartSVG V20.6 - Simple HD et multi-stickers'}
