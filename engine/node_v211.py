"""V21.1: five-control, French-language Express GUI + legacy expert nodes."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import torch
from .node_v21 import NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .production_v211 import run_v211,StudioError,preflight_masks

PROJETS=(
    'Auto - conserver le visuel',
    'Sticker - contour du sujet',
    'Planche - 24 images (6x4)',
    'Planche - 12 images (4x3)',
    'Carte - visuel rectangulaire',
)
IA_MODES=('Desactivee','Si disponible','Obligatoire')

class SmartSVGExpressV211:
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
    FUNCTION='run';OUTPUT_NODE=True;CATEGORY='SmartSVG / Cricut / V21.1'

    def run(self,image,dossier_sortie='',projet=PROJETS[0],largeur_mm=40.,
            qualite_ppp='300',ia_locale=IA_MODES[0],masques_objets=None):
        if projet not in PROJETS or ia_locale not in IA_MODES or qualite_ppp not in ('300','450'):
            raise StudioError('Option Express inconnue')
        if not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1 or image.shape[-1] not in (3,4):
            raise StudioError('IMAGE attendue : [1,H,W,RGB/RGBA]')
        if image.shape[1]*image.shape[2]>20_000_000:raise StudioError('IMAGE trop grande')
        preflight_masks(masques_objets,image.shape[1:3])
        raw=image[0].detach().cpu().numpy()
        if not np.isfinite(raw).all() or raw.min()<-.001 or raw.max()>1.001:
            raise StudioError('Pixels source invalides')
        pixels=np.uint8(np.clip(np.round(raw*255),0,255))
        if not str(dossier_sortie).strip():
            try:
                import folder_paths
                dossier_sortie=str(Path(folder_paths.get_output_directory())/'SmartSVG')
            except ImportError:
                dossier_sortie=str(Path.cwd()/'SmartSVG_Output')
        profile='auto';mode='sticker_contour';grid='6x4'
        if projet==PROJETS[2]:profile='planche_multi';grid='6x4'
        elif projet==PROJETS[3]:profile='planche_multi';grid='4x3'
        elif projet==PROJETS[4]:mode='carte_rectangle'
        # No mandatory GPU load for rectangular cuts.
        ia={'Desactivee':'desactiver','Si disponible':'si_disponible',
            'Obligatoire':'forcer'}[ia_locale]
        report,preview=run_v211(pixels,dossier_sortie,profile,float(largeur_mm),
                                int(qualite_ppp),mode,grid,ia,masques_objets)
        n=report.get('nombre_objets_exportes',0)
        pages=report.get('planches',report.get('planches_cricut',[]))
        warnings=[]
        for obj in report.get('objets',[]):warnings+=obj.get('avertissements',[])
        if (report.get('v21',{}).get('mode')=='REPLI_V20_6_SANS_MASQUE'
                and mode=='sticker_contour' and report.get('nombre_objets_exportes',0)<=1):
            warnings.append('Image complexe : sans masque, contour du sujet non garanti')
        if any(isinstance(p,dict) and p.get('statut')!='CREATION_OK' for p in pages):
            warnings.append('Au moins une planche nécessite une vérification')
        status='A VERIFIER DANS CRICUT'
        summary=(f'SmartSVG V21.1 | {n} visuel(s) | {len(pages)} planche(s)\n'
                 f'Opération : {mode} | {largeur_mm:g} mm | {qualite_ppp} ppp\n'
                 f'Statut : {status}\n'
                 f'Dossier : {report["dossier"]}')
        if warnings:summary+='\nPoints de vigilance : '+', '.join(dict.fromkeys(warnings[:5]))
        preview_array=np.asarray(preview.convert('RGB'),np.float32)/255.
        tensor=torch.from_numpy(np.ascontiguousarray(preview_array))[None]
        payload=json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)
        return {'ui':{'text':[summary]},'result':(tensor,summary,payload)}

NODE_CLASS_MAPPINGS={**OLD,'SmartSVGExpressV211':SmartSVGExpressV211}
NODE_DISPLAY_NAME_MAPPINGS={**OLD_NAMES,
    'SmartSVGExpressV211':'SmartSVG V21.1 - EXPRESS (5 choix) / impression et découpe'}
