"""SmartSVG V20.3: GPU resource preflight + guarded LineArt execution.

New aliases only. Inherited V20.2 Cricut engine untouched. CUDA gate is
advisory/protective, never a claim of proven RTX 3070 inference.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import tempfile
import time
from uuid import uuid4
from .node_v202 import (NODE_CLASS_MAPPINGS as OLD,
                         NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES,
                         SmartSVGLineArtV202)
from .gpu_budget_v203 import gpu_snapshot,policy_decision,compare_snapshots


class SmartSVGGPUPreflightV203:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'politique_gpu':(['protege','diagnostic','strict'],{'default':'protege'}),
            'vram_libre_min_gio':('FLOAT',{'default':2.5,'min':0.,'max':10.,'step':.25}),
            'marge_securite_gio':('FLOAT',{'default':.5,'min':0.,'max':4.,'step':.25}),
        }}
    RETURN_TYPES=('STRING',)
    RETURN_NAMES=('rapport_prevol_gpu',)
    FUNCTION='run'
    OUTPUT_NODE=True
    CATEGORY='SmartSVG / Cricut / GPU'
    def run(self,politique_gpu='protege',vram_libre_min_gio=2.5,marge_securite_gio=.5):
        status=gpu_snapshot()
        decision=policy_decision(status,policy=politique_gpu,
             free_min_gib=vram_libre_min_gio,margin_gib=marge_securite_gio)
        payload=json.dumps({'version':'20.3-beta','snapshot':status,'garde_fou':decision,
            'modeles_execution':False},ensure_ascii=False,indent=2,allow_nan=False)
        return {'ui':{'text':[payload]},'result':(payload,)}


class SmartSVGLineArtV203(SmartSVGLineArtV202):
    @classmethod
    def INPUT_TYPES(cls):
        old=SmartSVGLineArtV202.INPUT_TYPES()
        required=dict(old['required']);optional=dict(old.get('optional',{}))
        required['politique_gpu']=(['protege','diagnostic','strict'],{'default':'protege'})
        required['vram_libre_min_gio']=('FLOAT',{'default':2.5,'min':0.,'max':10.,'step':.25})
        required['marge_securite_gio']=('FLOAT',{'default':.5,'min':0.,'max':4.,'step':.25})
        return {'required':required,'optional':optional}
    FUNCTION='run'
    CATEGORY='SmartSVG / Cricut / Dessin'
    def run(self,image,dossier_sortie,source='auto',cible_decoupe='sticker',
            operation_cricut='imprimer_decouper_contour',nettoyage='doux',
            corriger_perspective=True,marge_blanche_px=10,largeur_finale_mm=90,
            segmentation_ia='auto',analyse_florence='auto',profil_segmentation='personne',
            prompt_personnalise='',repere_masque='source',masques_objets=None,
            politique_gpu='protege',vram_libre_min_gio=2.5,marge_securite_gio=.5):
        before=gpu_snapshot()
        policy=policy_decision(before,policy=politique_gpu,
                 free_min_gib=vram_libre_min_gio,margin_gib=marge_securite_gio,
                 ia=segmentation_ia,external_masks=masques_objets is not None)
        if policy['action']=='ABANDON_EXPLICITE':
            raise RuntimeError('SmartSVG V20.3: IA demandee mais prevol GPU insuffisant ('+
                policy['raison']+'). Desactiver IA ou adapter le seuil; aucune sortie generee.')
        effective_ia=segmentation_ia
        effective_florence=analyse_florence
        if policy['action']=='SAUTER_IA_GARDER_EXPORTS':
            effective_ia='desactiver'
            effective_florence='desactiver'
        start=time.perf_counter()
        result=super().run(image=image,dossier_sortie=dossier_sortie,
            source=source,cible_decoupe=cible_decoupe,operation_cricut=operation_cricut,
            nettoyage=nettoyage,corriger_perspective=corriger_perspective,
            marge_blanche_px=marge_blanche_px,largeur_finale_mm=largeur_finale_mm,
            segmentation_ia=effective_ia,analyse_florence=effective_florence,
            profil_segmentation=profil_segmentation,prompt_personnalise=prompt_personnalise,
            repere_masque=repere_masque,masques_objets=masques_objets)
        after=gpu_snapshot()
        original=json.loads(result['result'][1])
        ai_report=original.get('analyse',{})
        metrics=compare_snapshots(before,after,start,
                       model_was_called=bool(ai_report.get('segmentation_ia_appelee',False)))
        metrics['version']='20.3-beta'
        metrics['decision_prevol']=policy
        metrics['ia_effective_demandee']=effective_ia
        metrics['inference_rapportee']=ai_report.get('inference',{})
        metrics['fichiers_cricut_historiques_inchanges']=True
        metrics['note_exports']='Les exports de production sont generes exclusivement par le moteur V20.2 intact.'
        root=Path(original['dossier'])
        saved=None
        try:
            qa=root/'QA_GPU_V20_3'
            if qa.is_symlink():raise ValueError('Destination QA GPU symlink interdite')
            qa.mkdir(parents=True,exist_ok=True)
            final=qa/('rapport_gpu_'+uuid4().hex+'.json')
            with tempfile.NamedTemporaryFile('w',encoding='utf8',dir=qa,prefix='.pending_gpu_',
                                             suffix='.tmp',delete=False) as f:
                temp=Path(f.name)
                json.dump(metrics,f,ensure_ascii=False,indent=2,allow_nan=False)
                f.flush();os.fsync(f.fileno())
            try:
                os.replace(temp,final)
            finally:
                temp.unlink(missing_ok=True)
            saved=str(final)
        except Exception as exc:
            saved='ECHEC_ECRITURE_QA_GPU: '+type(exc).__name__
        original['profil_gpu_v20_3']=metrics
        original['rapport_gpu_enregistre']=saved
        original['avertissement']='Un candidat IA reste A VERIFIER; le prevol GPU ne valide ni son masque ni sa decoupe.'
        payload=json.dumps(original,ensure_ascii=False,indent=2,allow_nan=False)
        return {'ui':{'text':[payload]},'result':(result['result'][0],payload)}


NODE_CLASS_MAPPINGS={**OLD,
    'SmartSVGGPUPreflightV203':SmartSVGGPUPreflightV203,
    'SmartSVGLineArtV203':SmartSVGLineArtV203}
NODE_DISPLAY_NAME_MAPPINGS={**OLD_NAMES,
    'SmartSVGGPUPreflightV203':'SmartSVG V20.3 - Etat GPU / VRAM sans inference',
    'SmartSVGLineArtV203':'SmartSVG V20.3 - Dessin + Cricut + protection VRAM'}
