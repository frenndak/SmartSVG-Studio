"""SmartSVG V20.4: non-destructive line-art/AI mask quality checkpoint.

The V20.3 engine and previously shipped Cricut outputs remain untouched.
"""
from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path
from uuid import uuid4
from PIL import Image
from .node_v203 import (NODE_CLASS_MAPPINGS as OLD,
                        NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES,
                        SmartSVGLineArtV203)
from .mask_quality_v204 import audit_output_root, atomic_json, draw_overlay, analyze_batch

class SmartSVGLineArtV204(SmartSVGLineArtV203):
    """Add strict QA report to output of V20.3, never silently alter cut candidates."""
    @classmethod
    def INPUT_TYPES(cls):
        old=SmartSVGLineArtV203.INPUT_TYPES()
        required=dict(old['required']);optional=dict(old.get('optional',{}))
        required['controle_contours']=(['activer','desactiver'],{'default':'activer'})
        return {'required':required,'optional':optional}
    FUNCTION='run'
    CATEGORY='SmartSVG / Cricut / Qualite'

    def run(self,image,dossier_sortie,source='auto',cible_decoupe='sticker',
            operation_cricut='imprimer_decouper_contour',nettoyage='doux',
            corriger_perspective=True,marge_blanche_px=10,largeur_finale_mm=90,
            segmentation_ia='auto',analyse_florence='auto',profil_segmentation='personne',
            prompt_personnalise='',repere_masque='source',masques_objets=None,
            politique_gpu='protege',vram_libre_min_gio=2.5,marge_securite_gio=.5,
            controle_contours='activer'):
        if controle_contours not in ('activer','desactiver'):
            raise ValueError('Controle contours invalide')
        result=super().run(image=image,dossier_sortie=dossier_sortie,source=source,
            cible_decoupe=cible_decoupe,operation_cricut=operation_cricut,
            nettoyage=nettoyage,corriger_perspective=corriger_perspective,
            marge_blanche_px=marge_blanche_px,largeur_finale_mm=largeur_finale_mm,
            segmentation_ia=segmentation_ia,analyse_florence=analyse_florence,
            profil_segmentation=profil_segmentation,prompt_personnalise=prompt_personnalise,
            repere_masque=repere_masque,masques_objets=masques_objets,
            politique_gpu=politique_gpu,vram_libre_min_gio=vram_libre_min_gio,
            marge_securite_gio=marge_securite_gio)
        data=json.loads(result['result'][1])
        if controle_contours=='desactiver':
            data['qualite_masque_v20_4']={'statut':'DESACTIVE','validation_humaine_obligatoire':True}
        else:
            root=Path(data['dossier'])
            try:
                values,report=audit_output_root(root)
                if values is not None:
                    mask,ink=values
                    # Every QA run is isolated; no user file is overwritten.
                    folder=root/'QA_QUALITE_V20_4'
                    if folder.is_symlink():raise ValueError('Dossier QA symlink interdit')
                    folder.mkdir(parents=True,exist_ok=True)
                    suffix=uuid4().hex
                    preview=folder/('apercu_'+suffix+'.png')
                    temp=None
                    try:
                        with tempfile.NamedTemporaryFile(dir=folder,prefix='.pending_preview_',suffix='.png',delete=False) as fp:
                            temp=Path(fp.name)
                        Image.fromarray(draw_overlay(mask,ink),'RGB').save(temp)
                        os.replace(temp,preview)
                    finally:
                        if temp is not None:temp.unlink(missing_ok=True)
                    report['fichier_apercu']=str(preview)
                    report['legende']='rouge=contour du masque, violet=traits exclus du masque'
                    report['fichier_contour_ia_precedent_inchange']=True
                if values is not None:
                    saved=atomic_json(folder/('diagnostic_'+suffix+'.json'),report)
                    report['fichier_rapport']=saved
                data['qualite_masque_v20_4']=report
            except Exception as exc:
                data['qualite_masque_v20_4']={
                    'statut':'ECHEC_DIAGNOSTIC','erreur':type(exc).__name__,
                    'verdict':'NON_EVALUE','validation_humaine_obligatoire':True,
                    'note':'Les fichiers Cricut restent ceux produits par V20.3; ne pas interpreter cet echec comme une validation.'}
        data['version_controle']='20.4-beta'
        data['regle_cricut']='Un statut sans anomalies geometriques NE constitue PAS une validation de la decoupe.'
        payload=json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)
        return {'ui':{'text':[payload]},'result':(result['result'][0],payload)}

class SmartSVGMaskQualityV204:
    """Independent QA for SAM2, BiRefNet, Florence or user-provided mask batches."""
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'masques_objets':('MASK',)}}
    RETURN_TYPES=('MASK','STRING')
    RETURN_NAMES=('masques_inchanges','rapport_qualite')
    FUNCTION='run'
    CATEGORY='SmartSVG / Cricut / Qualite'
    def run(self,masques_objets):
        # Validate without mutating the incoming tensor. Preserve exact bits,
        # device and shape at the output, including any soft edges.
        report=analyze_batch(masques_objets)
        payload=json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)
        return {'ui':{'text':[payload]},'result':(masques_objets,payload)}

NODE_CLASS_MAPPINGS={**OLD,'SmartSVGLineArtV204':SmartSVGLineArtV204,
    'SmartSVGMaskQualityV204':SmartSVGMaskQualityV204}
NODE_DISPLAY_NAME_MAPPINGS={**OLD_NAMES,
    'SmartSVGLineArtV204':'SmartSVG V20.4 - Dessin + Cricut + QA masque/contours',
    'SmartSVGMaskQualityV204':'SmartSVG V20.4 - Verification de masques IA (sans modification)'}
