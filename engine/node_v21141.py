"""SmartSVG 21.14.1 — bounded color recovery for editable SVGs.

Legacy Print Then Cut workflows and V21.14 vector node remain untouched.
"""
from __future__ import annotations
import copy,json
import numpy as np
import torch
from .node_v2114 import NODE_CLASS_MAPPINGS as OLD,NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .node_v2114 import SmartSVGEditableColorsV2114
from .smartsvg_vector.layers_v2113 import VectorizationRefused,save_svg
from .smartsvg_vector.color_repair_v21141 import vectorize_color_repaired
from .smartsvg_compat.registry import merge_registry

class SmartSVGEditableColorsV21141(SmartSVGEditableColorsV2114):
    CATEGORY='SmartSVG / 03 VECTORISER'
    @classmethod
    def INPUT_TYPES(cls):return copy.deepcopy(super().INPUT_TYPES())
    def run(self,image,couleurs=8,largeur_mm=40.,dossier_sortie='',masque_sujet=None):
        if not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1 or image.shape[-1] not in (3,4):
            raise VectorizationRefused('IMAGE ComfyUI [1,H,W,RGB(A)] attendue')
        raw=image[0].detach().float().cpu().numpy()
        if not np.isfinite(raw).all() or raw.min()<-.001 or raw.max()>1.001:
            raise VectorizationRefused('Valeurs IMAGE hors plage [0,1]')
        pixels=np.uint8(np.rint(np.clip(raw,0.,1.)*255.))
        if masque_sujet is None:
            if pixels.shape[-1]!=4:raise VectorizationRefused('MASK nécessaire pour une image opaque')
            mask=pixels[:,:,3].astype(np.float32)/255.
        else:
            if not isinstance(masque_sujet,torch.Tensor) or masque_sujet.ndim not in (2,3):
                raise VectorizationRefused('MASK ComfyUI invalide')
            if masque_sujet.ndim==3 and masque_sujet.shape[0]!=1:
                raise VectorizationRefused('Sélectionner un sujet avant la vectorisation')
            mask=masque_sujet[0].detach().float().cpu().numpy() if masque_sujet.ndim==3 else masque_sujet.detach().float().cpu().numpy()
        svg,preview,info,comparison,qa=vectorize_color_repaired(
            pixels,mask,colors=int(couleurs),width_mm=largeur_mm)
        # Persist only after completion of all shape/color/format validations.
        filename=save_svg(svg,dossier_sortie)
        report={**info,'comparaison_v21131':qa,'fichier_svg_editable':filename,
                'compatibilite_print_then_cut':'NE_PAS_UTILISER_A_LA_PLACE_DU_PNG',
                'certification_decoupe':False,'certification_visuelle':False}
        text=(f"V21.14.1 SVG EXPÉRIMENTAL : {qa['iou_silhouette_approx']*100:.1f}% silhouette ; "
              f"erreur couleur totale {info['mae_rvb_sur_toute_silhouette_avant']:.1f} → "
              f"{info['mae_rvb_sur_toute_silhouette_apres']:.1f} ; "
              f"{info['formes_ajoutees_pour_couleur']} formes couleur supplémentaires. "
              'NE PAS utiliser comme PNG Print Then Cut. Vérifier les tracés dans Inkscape.')
        return {'result':(torch.from_numpy(np.ascontiguousarray(comparison,dtype=np.float32)/255.)[None],
                          torch.from_numpy(np.ascontiguousarray(preview,dtype=np.float32)/255.)[None],
                          filename,json.dumps(report,ensure_ascii=False,allow_nan=False)),
                'ui':{'text':[text]}}

NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS=merge_registry(OLD,OLD_NAMES,{
 'SmartSVGEditableColorsV21141':(SmartSVGEditableColorsV21141,
   '03 · SVG multicouche V21.14.1 — Fidélité des couleurs et coupe')
})
