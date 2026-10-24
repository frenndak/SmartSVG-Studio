"""V21.15.2 — guarded white-sheet Express; legacy node IDs untouched."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import torch
from .node_v2115 import NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .node_v2151 import SmartSVGExpressV2151, _comfy_output_directory
from .node_v211 import PROJETS, IA_MODES
from .smartsvg_quality.release_gate_v21152 import run_v21152
from .smartsvg_ui.presentation import build_presentation
from .smartsvg_ui.preview_bridge_v2151 import publish_previews
from .smartsvg_compat.registry import merge_registry
from .production_v211 import preflight_masks, StudioError


class SmartSVGExpressV21152(SmartSVGExpressV2151):
    CATEGORY='SmartSVG / 01 CRÉER'
    @classmethod
    def INPUT_TYPES(cls):
        # Preserve the same six required and one optional inputs, including
        # serialized widget order. No migration required for existing workflows.
        return super().INPUT_TYPES()

    def run(self,image,dossier_sortie='',projet=PROJETS[0],largeur_mm=40.,
            qualite_ppp='300',ia_locale=IA_MODES[0],masques_objets=None):
        if projet not in PROJETS or ia_locale not in IA_MODES or qualite_ppp not in ('300','450'):
            raise StudioError('Option Express inconnue')
        if not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1 or image.shape[-1] not in (3,4):
            raise StudioError('Image ComfyUI [1,H,W,RGB/RGBA] attendue')
        if image.shape[1]*image.shape[2]>20_000_000:raise StudioError('Image trop grande')
        preflight_masks(masques_objets,image.shape[1:3])
        raw=image[0].detach().cpu().numpy()
        if not np.isfinite(raw).all() or raw.min()<-.001 or raw.max()>1.001:
            raise StudioError('Pixels non finis ou hors plage [0,1]')
        pixels=np.uint8(np.clip(np.rint(raw*255),0,255))
        if not str(dossier_sortie).strip():
            try:
                import folder_paths
                dossier_sortie=str(Path(folder_paths.get_output_directory())/'SmartSVG')
            except ImportError:dossier_sortie=str(Path.cwd()/'SmartSVG_Output')
        profile='auto';operation='sticker_contour';grid='6x4'
        if projet==PROJETS[2]:profile='planche_multi';grid='6x4'
        elif projet==PROJETS[3]:profile='planche_multi';grid='4x3'
        elif projet==PROJETS[4]:operation='carte_rectangle'
        seg=dict(zip(IA_MODES,('desactiver','si_disponible','forcer')))[ia_locale]
        report,preview=run_v21152(pixels,dossier_sortie,profile,float(largeur_mm),
                         int(qualite_ppp),operation,grid,seg,masques_objets)
        gate=report['controle_v21152'];blocked=gate['status']=='BLOCKED'
        message=(f"SmartSVG V21.15.2 · {report.get('nombre_objets_exportes',0)} objet(s)\n"
                 f"Précontrôle de découpe : {'⛔ BLOQUÉ' if blocked else '⚠️ REVUE HUMAINE OBLIGATOIRE'}\n"
                 f"Détourage : {report['white_sheet_v21152']['mode']}\n"
                 f"{gate['action_requise']}\n"
                 f"Dossier : {report['dossier']}")
        # Contain only UI failures. A successful export must not fail because
        # ComfyUI lacks the optional dashboard in a particular frontend.
        try:
            view=build_presentation(report,mask_external=masques_objets is not None,ai_mode=ia_locale)
            view['etat_prevol']=gate['status']
            view['action_requise']=gate['action_requise']
            view['provenance']=('Détourage géométrique automatique, sans IA ; contrôle humain requis'
                if report['white_sheet_v21152']['mode']=='AUTO_MASQUES_HEURISTIQUES'
                else 'Pas de détourage automatique fiable établi')
        except Exception:
            view=None
        try:previews=publish_previews(report,_comfy_output_directory())
        except Exception:previews=[]
        arr=np.asarray(preview.convert('RGB'),np.float32)/255.
        tensor=torch.from_numpy(np.ascontiguousarray(arr))[None]
        payload=json.dumps(report,ensure_ascii=False,allow_nan=False)
        return {'ui':{'text':[message], 'smartsvg':[view] if view else [],
                      'smartsvg_previews':previews},'result':(tensor,message,payload)}

NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS=merge_registry(OLD,OLD_NAMES,{
 'SmartSVGExpressV21152':(SmartSVGExpressV21152,
                            '01 · SmartSVG EXPRESS V21.15.2 — détourage contrôlé'),
})
