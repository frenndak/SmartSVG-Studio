"""V21.14: shape-coverage repair and micro-cut warnings for editable SVG.

Does not change PNG Print Then Cut generation or older node registrations.
"""
from __future__ import annotations
import copy,json
import numpy as np
import torch
from .node_v21132 import NODE_CLASS_MAPPINGS as OLD,NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .node_v21132 import SmartSVGEditableColorsV21132
from .smartsvg_vector.layers_v2113 import save_svg,VectorizationRefused
from .smartsvg_vector.recovery_v2114 import vectorize_recovered
from .smartsvg_compat.registry import merge_registry

class SmartSVGEditableColorsV2114(SmartSVGEditableColorsV21132):
    """One extra editable silhouette-color layer; retains four output ports."""
    CATEGORY='SmartSVG / 03 VECTORISER'
    @classmethod
    def INPUT_TYPES(cls):return copy.deepcopy(super().INPUT_TYPES())
    def run(self,image,couleurs=8,largeur_mm=40.,dossier_sortie='',masque_sujet=None):
        if not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1 or image.shape[-1] not in (3,4):
            raise VectorizationRefused('Image ComfyUI [1,H,W,3/4] requise')
        data=image[0].detach().float().cpu().numpy()
        if not np.isfinite(data).all() or data.min()<-.001 or data.max()>1.001:
            raise VectorizationRefused('Image hors plage [0,1] ou non finie')
        pixels=np.uint8(np.rint(np.clip(data,0,1)*255))
        if masque_sujet is None:
            if pixels.shape[-1]!=4:raise VectorizationRefused('Masque du sujet obligatoire pour une image opaque')
            mask=np.asarray(pixels[:,:,3],dtype=np.float32)/255.
        else:
            if not isinstance(masque_sujet,torch.Tensor) or masque_sujet.ndim not in (2,3):
                raise VectorizationRefused('MASK ComfyUI invalide')
            if masque_sujet.ndim==3 and masque_sujet.shape[0]!=1:
                raise VectorizationRefused('Choisir un sujet avant de vectoriser')
            mask=masque_sujet[0].detach().float().cpu().numpy() if masque_sujet.ndim==3 else masque_sujet.detach().float().cpu().numpy()
        svg,preview,audit,comparison,qa=vectorize_recovered(pixels,mask,colors=int(couleurs),width_mm=largeur_mm)
        # Write only after all quality and geometry checks have succeeded.
        filename=save_svg(svg,dossier_sortie)
        report={**audit,'comparaison_v21131':qa,'fichier_svg_editable':filename,
                'compatibilite_print_then_cut':'NE_PAS_UTILISER_A_LA_PLACE_DU_PNG',
                'certification_decoupe':False,'certification_visuelle':False}
        risks=report['risques_decoupe']
        info=(f"SVG V21.14 EXPÉRIMENTAL : silhouette {audit['fidelite_silhouette_avant']*100:.1f}% "
              f"→ {audit['fidelite_silhouette_apres']*100:.1f}%, "
              f"{risks['anneaux_fins_a_verifier']} formes/anneaux fins à vérifier. "
              "NE PAS utiliser comme PNG Print Then Cut. Vérifier les calques dans Inkscape.")
        return {'result':(torch.from_numpy(np.ascontiguousarray(comparison,dtype=np.float32)/255.)[None],
                    torch.from_numpy(np.ascontiguousarray(preview,dtype=np.float32)/255.)[None],
                    filename,json.dumps(report,ensure_ascii=False,allow_nan=False)),
                'ui':{'text':[info]}}

NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS=merge_registry(OLD,OLD_NAMES,{
    'SmartSVGEditableColorsV2114':(SmartSVGEditableColorsV2114,
        '03 · SVG multicouche V21.14 — Récupération silhouette et alerte micro-découpes')
})
