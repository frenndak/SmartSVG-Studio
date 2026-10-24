"""SmartSVG V20.0: sequential SAM2 -> ROI BiRefNet matting -> cautious QA.

Legacy photo/Cricut pipelines remain untouched; the standalone node can be
wired ahead of any historic export. Full Express orchestration is opt-in only.
"""
from __future__ import annotations
import json
from pathlib import Path
import os
import tempfile
from uuid import uuid4
import numpy as np
from PIL import Image
import torch

from .adaptive_refiner_v20 import adaptive_refine, validate_masks, RefinementError
from .node_v196 import _image_u8, _mask_numpy
from .node_v19 import _detect_scene, _arr_image
from .scene_florence_v193 import inspect_scene
from .auto_segment_v192 import segment_scene
from .node_v198 import SmartSVGStudioV198Expert, SmartSVGStudioV198Express
from .node_v199 import NODE_CLASS_MAPPINGS as LEGACY, NODE_DISPLAY_NAME_MAPPINGS as LEGACY_NAMES


def _save_qa(root, reference, variants, uncertain, report):
    """Stage the entire QA report in one directory, then publish atomically.

    Failed saves leave no partial diagnostic directory. Cricut print outputs
    are never written by this function.  Reference is pre-refinement masks.
    """
    import shutil
    root=Path(root)
    root.mkdir(parents=True,exist_ok=True)
    qa=root/'QA_MATTING_V20'
    if qa.is_symlink():
        raise ValueError('QA directory must not be a symbolic link')
    qa.mkdir(parents=True,exist_ok=True)
    key=uuid4().hex
    final=qa/key
    stage=Path(tempfile.mkdtemp(prefix='.pending_',dir=str(qa)))
    try:
        files=[]
        if reference.shape!=variants.shape or uncertain.shape!=reference.shape[1:]:
            raise ValueError('Diagnostic masks not aligned')
        changed=[]
        for i,mask in enumerate(variants):
            if np.array_equal(mask,reference[i]):continue
            changed.append(i)
        for i in changed:
            for typ,arr in [('SOURCE',reference[i]),('PROPOSITION',variants[i])]:
                fname=f'OBJET_{i+1:02d}_{typ}.png'
                Image.fromarray(np.uint8(np.clip(arr,0,1)*255+.5),'L').save(stage/fname,format='PNG')
                files.append(fname)
        fname='INCERTITUDES.png'
        Image.fromarray(np.uint8(np.clip(uncertain,0,1)*255+.5),'L').save(stage/fname,format='PNG')
        files.append(fname)
        payload=dict(report)
        payload['fichiers_qa']=[str(final/name) for name in files]
        payload['masques_alternatifs_exportes']=len(changed)
        payload['export_qa_atomique']=True
        with (stage/'rapport.json').open('w',encoding='utf8') as f:
            json.dump(payload,f,ensure_ascii=False,indent=2,allow_nan=False)
            f.flush();os.fsync(f.fileno())
        os.replace(stage,final)
        return final/'rapport.json'
    except BaseException:
        shutil.rmtree(stage,ignore_errors=True)
        raise


def _primary(rgb, profile, analyse_florence, segmentation_objets='auto'):
    audit={'status':'NON_LANCE','florence':'NON_LANCE'}
    if segmentation_objets=='desactiver':return None,audit
    custom=''
    if analyse_florence!='desactiver':
        try:
            f=inspect_scene(rgb,profile=profile)
            audit['florence']=f['audit']
            if f['prompts']:custom=';'.join(f['prompts'])
            elif analyse_florence=='forcer':raise RefinementError('Aucun objet Florence2 detecte')
        except Exception as exc:
            audit['florence']={'statut':'ECHEC','detail':f'{type(exc).__name__}: {str(exc)[:175]}'}
            if analyse_florence=='forcer':raise
    res=segment_scene(rgb,profile=profile,custom_prompts=custom)
    audit['sam2']=res['audit']
    audit['status']='MASQUES_SAM2' if res['masks'] is not None else 'AUCUN_MASQUE'
    return res['masks'],audit


def run_adaptive(rgb, *, reference=None, annotation=None, mode='diagnostic', profil='auto',
                 analyse_florence='auto', segmentation_objets='auto', modele='Lucida', max_passes=2,
                 registry=None, model_runner=None):
    audit={'source':'MASK_ComfyUI' if reference is not None else 'AUTO_SAM2_DINO'}
    masks=validate_masks(rgb,reference) if reference is not None else None
    if masks is None:
        masks,inference=_primary(rgb,profil,analyse_florence,segmentation_objets)
        audit['premiere_passe']=inference
        if masks is None:
            raise RefinementError('Aucun masque SAM2 utilisable : aucun detourage exporte ou invente')
    selected,alternatives,uncertainty,qa=adaptive_refine(
        rgb,masks,registry=registry,model=modele,max_passes=max_passes,
        mode=mode,annotation=annotation,model_runner=model_runner)
    qa['provenance']=audit
    return selected,alternatives,uncertainty,qa,masks.copy()


class SmartSVGAdaptiveV20:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'image':('IMAGE',),
            'mode':(['diagnostic','proposition','adopter_annotation'],{'default':'diagnostic'}),
            'modele_matting':(['Lucida','BiRefNet-portrait','BiRefNet-matting'],{'default':'Lucida'}),
            'max_passes':('INT',{'default':2,'min':0,'max':4,'step':1}),
            'profil_segmentation':(['auto','personne','cadeaux','chopes','personne_cadeaux','animaux'],{'default':'auto'}),
            'analyse_florence':(['auto','desactiver','forcer'],{'default':'auto'}),
        },'optional':{'masques_objets':('MASK',),'masque_annote':('MASK',)}}
    RETURN_TYPES=('MASK','MASK','MASK','STRING')
    RETURN_NAMES=('masques_retenus','variantes_matting','zones_incertitude','rapport_ia')
    FUNCTION='run'
    CATEGORY='SmartSVG / Cricut'
    def run(self,image,mode='diagnostic',modele_matting='Lucida',max_passes=2,
            profil_segmentation='auto',analyse_florence='auto',masques_objets=None,masque_annote=None):
        selected,alternatives,uncertain,report,original=run_adaptive(_image_u8(image),
            reference=_mask_numpy(masques_objets),annotation=_mask_numpy(masque_annote),mode=mode,
            profil=profil_segmentation,analyse_florence=analyse_florence,
            modele=modele_matting,max_passes=max_passes)
        return torch.from_numpy(selected.copy()),torch.from_numpy(alternatives.copy()),\
               torch.from_numpy(uncertain[None].copy()),json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)


class SmartSVGStudioV20Expert(SmartSVGStudioV198Expert):
    @classmethod
    def INPUT_TYPES(cls):
        old=super().INPUT_TYPES(); required=dict(old['required']);optional=dict(old.get('optional',{}))
        required['raffinement_ia']=(['desactiver','diagnostic','proposition','adopter_annotation'],{'default':'desactiver'})
        required['modele_matting']=(['Lucida','BiRefNet-portrait','BiRefNet-matting'],{'default':'Lucida'})
        required['max_passes_ia']=('INT',{'default':2,'min':0,'max':4,'step':1})
        return {'required':required,'optional':optional}
    def execute(self,image,raffinement_ia='desactiver',modele_matting='Lucida',max_passes_ia=2,**kwargs):
        if raffinement_ia=='desactiver':return super().execute(image=image,**kwargs)
        scene=str(kwargs.get('type_fichier','auto'))
        if scene=='stickers':
            x,t=super().execute(image=image,**kwargs)
            return x,t+'\nV20.0: raffinement IA ignore sur planche stickers (moteur vectoriel conserve).'
        rgb,alpha=_arr_image(image,kwargs.get('masque_png'))
        if scene=='auto' and _detect_scene(rgb,alpha)!='photo':
            x,t=super().execute(image=image,**kwargs)
            return x,t+'\nV20.0: scene classifiee stickers; matting non applique.'
        source=kwargs.get('masques_objets')
        masks=_mask_numpy(source) if source is not None else None
        annotation=_mask_numpy(kwargs.get('masque_annote')) if kwargs.get('masque_annote') is not None else None
        try:
            selected,alternatives,uncertain,report,original=run_adaptive(
                rgb,reference=masks,annotation=annotation,mode=raffinement_ia,
                profil=kwargs.get('profil_segmentation','auto'),
                analyse_florence=kwargs.get('analyse_florence','auto'),
                segmentation_objets=kwargs.get('segmentation_objets','auto'),
                modele=modele_matting,max_passes=max_passes_ia)
        except Exception as exc:
            if kwargs.get('segmentation_objets')=='forcer' or raffinement_ia=='adopter_annotation':raise
            # SAM2 already failed once; avoid repeating costly inference.
            if masks is None:
                kwargs['segmentation_objets']='desactiver'
                kwargs['analyse_florence']='desactiver'
                kwargs['ia_locale']='desactiver'
                kwargs['strategie_photo']='analyse_seule'
            x,t=super().execute(image=image,**kwargs)
            return x,t+f'\nV20.0: second passage non realise ({type(exc).__name__}: {str(exc)[:120]}). Repli historique.'
        # Diagnostic/proposition always transmit the ORIGINAL mask to production.
        # Only adoption with explicit annotation may change production.
        kwargs['masques_objets']=torch.from_numpy(selected.copy())
        kwargs['alignement_masques']='diagnostic'
        x,t=super().execute(image=image,**kwargs)
        try:
            root=str(kwargs.get('dossier_sortie','')).strip()
            if not root:
                import folder_paths
                root=str(Path(folder_paths.get_output_directory())/'SmartSVG')
            fn=_save_qa(Path(root),original,alternatives,uncertain,report)
            t+=f'\nV20.0: second passage {report["appels_modele_reussis"]} objet(s), '+\
               f'{report["masques_proposes"]} proposition(s). QA: {fn}'
        except Exception as exc:
            t+='\nATTENTION V20.0: rapport matting non sauvegarde ('+type(exc).__name__+').'
        return x,t


class SmartSVGStudioV20Express(SmartSVGStudioV20Expert):
    @classmethod
    def INPUT_TYPES(cls):
        old=SmartSVGStudioV198Express.INPUT_TYPES()
        required=dict(old['required']);optional=dict(old.get('optional',{}))
        required['raffinement_ia']=(['desactiver','diagnostic','proposition','adopter_annotation'],{'default':'desactiver'})
        required['modele_matting']=(['Lucida','BiRefNet-portrait','BiRefNet-matting'],{'default':'Lucida'})
        required['max_passes_ia']=('INT',{'default':2,'min':0,'max':4,'step':1})
        return {'required':required,'optional':optional}
    FUNCTION='execute_express'
    CATEGORY='SmartSVG / Cricut'
    OUTPUT_NODE=True
    def execute_express(self,image,dossier_sortie,largeur_planche_mm=180,type_fichier='auto',
                        segmentation_objets='auto',profil_segmentation='auto',analyse_florence='auto',
                        raffinement_contours='conservateur',contacts_objets='conservateur',
                        comparaison_masques='diagnostic',profil_performances='activer',
                        alignement_masques='diagnostic',raffinement_ia='desactiver',
                        modele_matting='Lucida',max_passes_ia=2,masque_png=None,masques_objets=None,
                        masque_alternative_B=None,masque_alternative_C=None,masque_annote=None):
        return self.execute(image=image,dossier_sortie=dossier_sortie,
            largeur_planche_mm=largeur_planche_mm,type_fichier=type_fichier,
            segmentation_objets=segmentation_objets,profil_segmentation=profil_segmentation,
            analyse_florence=analyse_florence,raffinement_contours=raffinement_contours,
            contacts_objets=contacts_objets,comparaison_masques=comparaison_masques,
            profil_performances=profil_performances,alignement_masques=alignement_masques,
            raffinement_ia=raffinement_ia,modele_matting=modele_matting,max_passes_ia=max_passes_ia,
            masque_png=masque_png,masques_objets=masques_objets,
            masque_alternative_B=masque_alternative_B,masque_alternative_C=masque_alternative_C,
            masque_annote=masque_annote,ia_locale='auto')


NODE_CLASS_MAPPINGS={**LEGACY,
                     'SmartSVGAdaptiveV20':SmartSVGAdaptiveV20,
                     'SmartSVGStudioV20Expert':SmartSVGStudioV20Expert,
                     'SmartSVGStudioV20Express':SmartSVGStudioV20Express}
NODE_DISPLAY_NAME_MAPPINGS={**LEGACY_NAMES,
                     'SmartSVGAdaptiveV20':'SmartSVG V20.0 - Segmentation + Matting ROI / diagnostic',
                     'SmartSVGStudioV20Expert':'SmartSVG V20.0 Expert - orchestration locale',
                     'SmartSVGStudioV20Express':'SmartSVG V20.0 Express - Cricut + matting prudent'}


class SmartSVGEnvironmentV20:
    """Read-only local ComfyUI/RMBG preflight, with no inference or downloads."""
    @classmethod
    def INPUT_TYPES(cls):return {'required':{}}
    RETURN_TYPES=('STRING',)
    RETURN_NAMES=('rapport_installation',)
    OUTPUT_NODE=True
    FUNCTION='run'
    CATEGORY='SmartSVG / Cricut'
    def run(self):
        info={'version':'20.0','execution_modele_ia':False,'installation_rmbg':'inconnue',
              'modules_disponibles':{},'cuda':{'disponible':False},'conseils':[]}
        try:
            import nodes
            reg=getattr(nodes,'NODE_CLASS_MAPPINGS',{})
            for name in ('BiRefNetRMBG','SAM2Segment','AILab_Florence2'):
                info['modules_disponibles'][name]=name in reg
            info['installation_rmbg']='partielle_ou_complete' if any(info['modules_disponibles'].values()) else 'absente_ou_non_chargee'
            if 'BiRefNetRMBG' in reg:
                try:
                    spec=reg['BiRefNetRMBG'].INPUT_TYPES()['required']['model'][0]
                    info['modeles_matting_annonces']=[str(x) for x in spec]
                except Exception as exc:
                    info['conseils'].append('Interface BiRefNetRMBG a verifier: '+type(exc).__name__)
        except Exception as exc:
            info['installation_rmbg']='comfyui_indisponible'
            info['conseils'].append('Contexte ComfyUI inaccessible: '+type(exc).__name__)
        try:
            cuda=bool(torch.cuda.is_available())
            info['cuda']['disponible']=cuda
            if cuda:
                info['cuda']['peripherique']=str(torch.cuda.get_device_name(torch.cuda.current_device()))
                props=torch.cuda.get_device_properties(torch.cuda.current_device())
                info['cuda']['vram_physique_gio']=round(props.total_memory/1024**3,2)
        except Exception as exc:
            info['cuda']['erreur']=type(exc).__name__
        if not info['modules_disponibles'].get('SAM2Segment'):
            info['conseils'].append('Installer ou actualiser RMBG avant la segmentation principale')
        info['conseils'].append('Aucun poids de modele IA n est execute ni telecharge par ce diagnostic')
        payload=json.dumps(info,ensure_ascii=False,indent=2)
        return {'ui':{'text':[payload]},'result':(payload,)}

NODE_CLASS_MAPPINGS['SmartSVGEnvironmentV20']=SmartSVGEnvironmentV20
NODE_DISPLAY_NAME_MAPPINGS['SmartSVGEnvironmentV20']='SmartSVG V20.0 - Diagnostic installation RMBG / CUDA'
