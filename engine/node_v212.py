"""V21.2: same five Express controls with automatic visible export QA."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import torch
from .node_v211 import NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES,PROJETS,IA_MODES
from .production_v211 import preflight_masks, StudioError
from .controle_export_v212 import run_v212

class SmartSVGExpressV212:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'image':('IMAGE',),
            'dossier_sortie':('STRING',{'default':''}),
            'projet':(list(PROJETS),{'default':PROJETS[0]}),
            'largeur_mm':('FLOAT',{'default':40.,'min':15.,'max':180.,'step':1.}),
            'qualite_ppp':(['300','450'],{'default':'300'}),
            'ia_locale':(list(IA_MODES),{'default':IA_MODES[0]}),
        },'optional':{'masques_objets':('MASK',)}}
    RETURN_TYPES=('IMAGE','STRING','STRING')
    RETURN_NAMES=('apercu','resume_lisible','rapport_json')
    FUNCTION='run';OUTPUT_NODE=True;CATEGORY='SmartSVG / Cricut / V21.2'

    def run(self,image,dossier_sortie='',projet=PROJETS[0],largeur_mm=40.,
            qualite_ppp='300',ia_locale=IA_MODES[0],masques_objets=None):
        if projet not in PROJETS or ia_locale not in IA_MODES or qualite_ppp not in ('300','450'):
            raise StudioError('Option Express inconnue')
        if not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1 or image.shape[-1] not in (3,4):
            raise StudioError('IMAGE attendue : [1,H,W,RGB/RGBA]')
        if image.shape[1]*image.shape[2]>20_000_000:raise StudioError('Image trop grande')
        preflight_masks(masques_objets,image.shape[1:3])
        a=image[0].detach().cpu().numpy()
        if not np.isfinite(a).all() or a.min()<-.001 or a.max()>1.001:
            raise StudioError('Pixels source invalides')
        pixels=np.uint8(np.clip(np.round(a*255),0,255))
        if not str(dossier_sortie).strip():
            try:
                import folder_paths
                dossier_sortie=str(Path(folder_paths.get_output_directory())/'SmartSVG')
            except ImportError:dossier_sortie=str(Path.cwd()/'SmartSVG_Output')
        profile='auto';mode='sticker_contour';grid='6x4'
        if projet==PROJETS[2]:profile='planche_multi';grid='6x4'
        elif projet==PROJETS[3]:profile='planche_multi';grid='4x3'
        elif projet==PROJETS[4]:mode='carte_rectangle'
        ia={'Desactivee':'desactiver','Si disponible':'si_disponible','Obligatoire':'forcer'}[ia_locale]
        report,preview=run_v212(pixels,dossier_sortie,profile,float(largeur_mm),
                                int(qualite_ppp),mode,grid,ia,masques_objets)
        q=report['controle_v212'];n=report.get('nombre_objets_exportes',0)
        summary=(f'SmartSVG V21.2 | {n} objet(s) | {largeur_mm:g} mm | {qualite_ppp} ppp\n'
                 f'Statut : A VERIFIER AVANT CRICUT\n'
                 f'Apercu QA : {q["apercu_global"]}\n'
                 f'Dossier : {report["dossier"]}')
        if q['alertes']:summary+='\nAlertes : '+', '.join(q['alertes'])
        arr=np.asarray(preview.convert('RGB'),np.float32)/255.
        tensor=torch.from_numpy(np.ascontiguousarray(arr))[None]
        return {'ui':{'text':[summary]},
                'result':(tensor,summary,json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False))}

NODE_CLASS_MAPPINGS={**OLD,'SmartSVGExpressV212':SmartSVGExpressV212}
NODE_DISPLAY_NAME_MAPPINGS={**OLD_NAMES,
    'SmartSVGExpressV212':'SmartSVG V21.2 - EXPRESS + Apercu QA par objet (5 choix)'}
