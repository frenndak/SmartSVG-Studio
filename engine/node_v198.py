"""ComfyUI V19.8: independent one-to-one object mask alignment and QA.

Optional diagnostics can be integrated into V19.7.1 production without
changing existing Cricut exports in default diagnostic mode.
"""
from __future__ import annotations
import json
from pathlib import Path
from uuid import uuid4
import os
import tempfile
import time

import torch

from .mask_alignment_v198 import compare_aligned_masks, MaskComparisonError
from .node_v196 import _image_u8, _mask_numpy
from .node_v1971 import (SmartSVGStudioV1971Expert, SmartSVGStudioV1971Express,
                         NODE_CLASS_MAPPINGS as EXISTING_CLASSES,
                         NODE_DISPLAY_NAME_MAPPINGS as EXISTING_NAMES)


class SmartSVGAlignMasksV198:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'image': ('IMAGE',),
            'masque_reference': ('MASK',),
            'mode': (['diagnostic','selection_prudente','selection_avec_annotation'],{'default':'diagnostic'}),
        },'optional': {
            'masque_alternative_B':('MASK',),
            'masque_alternative_C':('MASK',),
            'masque_annote':('MASK',),
        }}
    RETURN_TYPES=('MASK','MASK','STRING')
    RETURN_NAMES=('masques_retenus','zones_incertitude','rapport_appariement')
    FUNCTION='run'
    CATEGORY='SmartSVG / Cricut'

    def run(self,image,masque_reference,mode='diagnostic',masque_alternative_B=None,
            masque_alternative_C=None,masque_annote=None):
        selected,uncertain,report=compare_aligned_masks(
            _image_u8(image),_mask_numpy(masque_reference),
            _mask_numpy(masque_alternative_B),_mask_numpy(masque_alternative_C),
            mode=mode,annotation=_mask_numpy(masque_annote))
        return (torch.from_numpy(selected.copy()),
                torch.from_numpy(uncertain[None].copy()),
                json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False))


def _write_report(base:Path, report:dict) -> Path:
    """Write diagnostic outside artifact folder, never mutate Print Then Cut."""
    base.mkdir(parents=True,exist_ok=True)
    fd, temp_path=tempfile.mkstemp(prefix='.SmartSVG198_',suffix='.tmp',dir=base)
    path=base/f'ALIGNEMENT_MASQUES_V19_8_{uuid4().hex[:10]}.json'
    try:
        with os.fdopen(fd,'w',encoding='utf8') as f:
            json.dump(report,f,indent=2,ensure_ascii=False,allow_nan=False)
            f.flush();os.fsync(f.fileno())
        os.replace(temp_path,path)
    finally:
        if os.path.exists(temp_path):os.unlink(temp_path)
    return path


class SmartSVGStudioV198Expert(SmartSVGStudioV1971Expert):
    @classmethod
    def INPUT_TYPES(cls):
        obj=super().INPUT_TYPES()
        req=dict(obj['required'])
        req['alignement_masques']=(['diagnostic','selection_prudente','selection_avec_annotation'],{'default':'diagnostic'})
        return {'required':req,'optional':dict(obj.get('optional',{}))}

    def execute(self,image,alignement_masques='diagnostic',**kwargs):
        source=kwargs.get('masques_objets')
        altb=kwargs.pop('masque_alternative_B',None)
        altc=kwargs.pop('masque_alternative_C',None)
        ann=kwargs.pop('masque_annote',None)
        report=None; elapsed=None
        legacy_mode=kwargs.get('comparaison_masques','diagnostic')
        if source is not None:
            start=time.perf_counter()
            selected,uncertain,report=compare_aligned_masks(
                _image_u8(image),_mask_numpy(source),_mask_numpy(altb),
                _mask_numpy(altc),mode=alignement_masques,
                annotation=_mask_numpy(ann))
            elapsed=time.perf_counter()-start
            kwargs['masques_objets']=torch.from_numpy(selected.copy())
        elif altb is not None or altc is not None or ann is not None:
            raise MaskComparisonError('Alternatives fournies sans masque reference; branchez masques_objets')
        elif alignement_masques=='selection_avec_annotation':
            raise MaskComparisonError('Annotation et masque reference requis en mode supervise')
        # Legacy comparator disabled: no double selection, nor legacy errors
        # when alternatives have a different number/order of objects.
        kwargs['comparaison_masques']='desactiver'
        preview,msg=super().execute(image=image,**kwargs)
        if legacy_mode not in ('diagnostic','desactiver'):
            msg+='\nNOTE: ancien mode V19.6 ignore; utiliser alignement_masques V19.8.'
        if report is None:
            return preview,msg+'\nV19.8: aucun masque externe, alignement non lance.'
        report['duree_comparaison_s']=round(elapsed,5)
        n=sum(o['selection']!='reference' for o in report['objets'])
        try:
            out_dir=str(kwargs.get('dossier_sortie','')).strip()
            if not out_dir:
                import folder_paths
                out_dir=str(Path(folder_paths.get_output_directory())/'SmartSVG')
            path=_write_report(Path(out_dir),report)
            note=f'\nV19.8: {n}/{len(report["objets"])} masque(s) alternatif(s) retenu(s). Rapport: {path}'
        except Exception as exc:
            note=f'\nATTENTION: rapport appariement non enregistre ({type(exc).__name__}); PNG Cricut conserve.'
        return preview,msg+note


class SmartSVGStudioV198Express(SmartSVGStudioV198Expert):
    @classmethod
    def INPUT_TYPES(cls):
        old=SmartSVGStudioV1971Express.INPUT_TYPES()
        req=dict(old['required'])
        req['alignement_masques']=(['diagnostic','selection_prudente','selection_avec_annotation'],{'default':'diagnostic'})
        return {'required':req,'optional':dict(old.get('optional',{}))}
    FUNCTION='execute_express'
    CATEGORY='SmartSVG / Cricut'
    OUTPUT_NODE=True

    def execute_express(self,image,dossier_sortie,largeur_planche_mm=180,type_fichier='auto',
                        segmentation_objets='auto',profil_segmentation='auto',analyse_florence='auto',
                        raffinement_contours='conservateur',contacts_objets='conservateur',
                        comparaison_masques='diagnostic',profil_performances='activer',
                        alignement_masques='diagnostic',masque_png=None,masques_objets=None,
                        masque_alternative_B=None,masque_alternative_C=None,masque_annote=None):
        return self.execute(image=image,dossier_sortie=dossier_sortie,
            largeur_planche_mm=largeur_planche_mm,type_fichier=type_fichier,
            segmentation_objets=segmentation_objets,profil_segmentation=profil_segmentation,
            analyse_florence=analyse_florence,raffinement_contours=raffinement_contours,
            contacts_objets=contacts_objets,comparaison_masques=comparaison_masques,
            profil_performances=profil_performances,alignement_masques=alignement_masques,
            masque_png=masque_png,masques_objets=masques_objets,
            masque_alternative_B=masque_alternative_B,
            masque_alternative_C=masque_alternative_C,masque_annote=masque_annote,
            ia_locale='auto')

NODE_CLASS_MAPPINGS={**EXISTING_CLASSES,
    'SmartSVGAlignMasksV198':SmartSVGAlignMasksV198,
    'SmartSVGStudioV198Expert':SmartSVGStudioV198Expert,
    'SmartSVGStudioV198Express':SmartSVGStudioV198Express}
NODE_DISPLAY_NAME_MAPPINGS={**EXISTING_NAMES,
    'SmartSVGAlignMasksV198':'SmartSVG V19.8 - Apparier objets + carte incertitudes',
    'SmartSVGStudioV198Expert':'SmartSVG V19.8 Expert - appariement IA',
    'SmartSVGStudioV198Express':'SmartSVG V19.8 Express - Cricut + appariement'}
