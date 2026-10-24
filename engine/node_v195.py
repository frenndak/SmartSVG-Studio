"""V19.5 Florence-grounded local SAM2 masks for ComfyUI-RMBG.

Legacy V19.1 still available under original node IDs. A photo gets independent
MASK extraction; sticker/V18.1 pipeline remains untouched.
"""
from pathlib import Path
import gc
import numpy as np
import torch

from .node_v19 import SmartSVGStudioV191Expert, SmartSVGStudioV191Express, _arr_image, _detect_scene
from .node_v194 import NODE_CLASS_MAPPINGS as OLD_CLASSES, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .auto_segment_v192 import segment_scene
from .scene_florence_v193 import inspect_scene, FlorenceUnavailable
from .photo_contacts_v195 import process_photo_v195 as process_photo
from .telemetry_v197 import track_stage, record_output_path, annotate_stage

class SmartSVGStudioV195Expert(SmartSVGStudioV191Expert):
    @classmethod
    def INPUT_TYPES(cls):
        old=super().INPUT_TYPES()
        req=dict(old['required']);opt=dict(old['optional'])
        req.update({
            'segmentation_objets':(['auto','forcer','desactiver'],{'default':'auto'}),
            'analyse_florence':(['auto','forcer','desactiver'],{'default':'auto'}),
            'profil_segmentation':(['auto','personne','cadeaux','chopes','personne_cadeaux','animaux'],{'default':'auto'}),
            'prompts_anglais':('STRING',{'default':'','multiline':True}),
            'raffinement_contours':(['conservateur','bords_doux'],{'default':'conservateur'}),
            'contacts_objets':(['conservateur','proposer_separation'],{'default':'conservateur'}),
        })
        return {'required':req,'optional':opt}

    def execute(self,image,dossier_sortie,type_entree='auto',type_creation='auto',ia_locale='auto',
                largeur_planche_mm=180,marge_sticker_mm=1.5,couleurs_svg_simplifie=10,
                mode_objets='auto',noms_objets='',repere_masques='planche',transformation_masques_json='',
                type_fichier='auto',strategie_photo='auto',boites_objets_json='',
                segmentation_objets='auto',profil_segmentation='auto',prompts_anglais='',analyse_florence='auto',
                raffinement_contours='conservateur',contacts_objets='conservateur',
                masque_png=None,masques_objets=None):
        rgb,alpha=_arr_image(image,masque_png)
        route=_detect_scene(rgb,alpha) if type_fichier=='auto' else type_fichier
        if route=='stickers':
            return super().execute(image,dossier_sortie,type_entree=type_entree,type_creation=type_creation,
                    ia_locale=ia_locale,largeur_planche_mm=largeur_planche_mm,
                    marge_sticker_mm=marge_sticker_mm,couleurs_svg_simplifie=couleurs_svg_simplifie,
                    mode_objets=mode_objets,noms_objets=noms_objets,repere_masques=repere_masques,
                    transformation_masques_json=transformation_masques_json,
                    type_fichier='stickers',strategie_photo=strategie_photo,
                    boites_objets_json=boites_objets_json,
                    masque_png=masque_png,masques_objets=masques_objets)
        dest=str(dossier_sortie).strip()
        if not dest:
            import folder_paths
            dest=str(Path(folder_paths.get_output_directory())/'SmartSVG')
        ext=masques_objets.detach().cpu().numpy() if masques_objets is not None else None
        self._rmbg_stats=[]
        auto_details={'statut':'NON_LANCEE','raison':'masques externes ou desactivation','masques_acceptes':0}
        florence_audit={'statut':'NON_LANCEE','raison':'analyse desactivee, masques externes ou prompts manuels'}
        # Do not run inference in analyse_seule or explicitly guided mode.
        run_auto=(ext is None and segmentation_objets!='desactiver' and
                  strategie_photo=='auto')
        selected_prompts=prompts_anglais
        if run_auto and not selected_prompts.strip() and analyse_florence!='desactiver':
            try:
                with track_stage("Florence-2 / detection"):
                    planned=inspect_scene(rgb,profile=profil_segmentation)
                annotate_stage('Florence-2 / detection',notes=f'{len(planned["detections"])} detections filtrees')
                florence_audit={**planned['audit'],'detections':planned['detections']}
                if planned['prompts']:
                    selected_prompts=';'.join(planned['prompts'])
                elif analyse_florence=='forcer':
                    raise FlorenceUnavailable('Florence2 n a detecte aucune categorie fiable')
            except Exception as exc:
                florence_audit={'statut':'ECHEC_ANALYSE','erreur':f'{type(exc).__name__}: {str(exc)[:220]}',
                               'repli':'prompts du profil courant' if analyse_florence=='auto' else 'aucun'}
                if analyse_florence=='forcer':
                    raise RuntimeError('Analyse Florence2 forcee indisponible: '+florence_audit['erreur']) from exc
        if run_auto:
            try:
                with track_stage("SAM2 / segmentation"):
                    segment=segment_scene(rgb,profile=profil_segmentation,
                                          custom_prompts=selected_prompts)
                annotate_stage('SAM2 / segmentation', mask_count=segment['audit'].get('masques_acceptes',0))
                if segment.get('masks') is not None:
                    annotate_stage('SAM2 / segmentation',mask_count=len(segment['masks']),
                                   notes='Cout moyen amorti pour les masques SAM2 renvoyes.')
                auto_details=segment['audit']
                auto_details['statut']='OK' if segment['masks'] is not None else 'AUCUN_MASQUE_UTILISABLE'
                if segment['masks'] is not None:
                    ext=segment['masks']
                    noms_objets=';'.join(segment['labels'])
            except Exception as exc:
                auto_details={'statut':'ECHEC_MODELE_LOCAL','erreur':f'{type(exc).__name__}: {str(exc)[:240]}',
                              'masques_acceptes':0}
                if segmentation_objets=='forcer':
                    raise RuntimeError('Segmentation locale forcee non disponible: '+auto_details['erreur']) from exc
        auto_details['analyse_florence_v193']=florence_audit
        if segmentation_objets=='forcer' and ext is None and strategie_photo=='auto':
            raise RuntimeError('Segmentation multi-objets forcee : aucun objet avec masque valide')
        # If auto segmentation failed, the legacy foreground RMBG may still be useful;
        # never pretend that a foreground mask represents separate objects.
        self._rmbg_backend=None;self._rmbg_backend_class=None
        provider=None
        if ext is None and strategie_photo=='auto' and ia_locale!='desactiver':
            def provider(arr):
                with track_stage("RMBG / masque de premier plan"):
                    return self._rmbg_mask(arr)
        try:
            with track_stage("Export photo / Cricut"):
                result,preview=process_photo(rgb,dest,masks=ext,labels=noms_objets,
                boxes_json=boites_objets_json,mode=strategie_photo,foreground_provider=provider,
                alpha=alpha,width_mm=largeur_planche_mm,white_offset_mm=marge_sticker_mm,
                mask_origin='AUTO_SAM2_DINO_SOURCE' if run_auto and ext is not None else 'MASK_ComfyUI_source',
                require_provider=(ia_locale=='forcer' and ext is None),
                segmentation_metadata=auto_details,refinement_mode=raffinement_contours,
                contact_mode=contacts_objets)
        finally:
            self._rmbg_backend=None;self._rmbg_backend_class=None
            gc.collect()
            if torch.cuda.is_available():torch.cuda.empty_cache()
        record_output_path(result["output"])
        qa=result['audit_v19']
        txt=(f'SmartSVG V19.5.2 PHOTO: {qa["nombre_objets_extraits"]} objet(s) detoures.\n'
             f'Florence2: {florence_audit.get("statut","NON_LANCEE")}.\n'
             f'SAM2 auto: {auto_details.get("statut", "INCONNU")} ; '
             f'{auto_details.get("masques_acceptes",0)} masque(s) retenu(s).\n'
             f'Dossier: {result["output"]}\n'
             'Verifier QUALITE_DETOURAGE_V19_4.json pour cheveux, mains et chopes.\n'
             'Rien ne garantit la reconnaissance des parties cachees ou du texte.\n')
        tensor=torch.from_numpy(np.asarray(preview,np.float32).copy()/255).unsqueeze(0)
        return tensor,txt

class SmartSVGStudioV195Express(SmartSVGStudioV195Expert):
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'image':('IMAGE',),
            'dossier_sortie':('STRING',{'default':r'C:\Users\Public\Documents\Cricut_SVG','multiline':False}),
            'largeur_planche_mm':('INT',{'default':180,'min':30,'max':290,'step':5}),
            'type_fichier':(['auto','stickers','photo'],{'default':'auto'}),
            'segmentation_objets':(['auto','forcer','desactiver'],{'default':'auto'}),
            'analyse_florence':(['auto','forcer','desactiver'],{'default':'auto'}),
            'profil_segmentation':(['auto','personne','cadeaux','chopes','personne_cadeaux','animaux'],{'default':'auto'}),
            'raffinement_contours':(['conservateur','bords_doux'],{'default':'conservateur'}),
            'contacts_objets':(['conservateur','proposer_separation'],{'default':'conservateur'}),
        },'optional':{'masque_png':('MASK',),'masques_objets':('MASK',)}}
    FUNCTION='execute_express'
    CATEGORY='SmartSVG / Cricut'
    OUTPUT_NODE=True
    def execute_express(self,image,dossier_sortie,largeur_planche_mm=180,type_fichier='auto',
                        segmentation_objets='auto',profil_segmentation='auto',analyse_florence='auto',
                        raffinement_contours='conservateur',contacts_objets='conservateur',masque_png=None,masques_objets=None):
        return self.execute(image,dossier_sortie,largeur_planche_mm=largeur_planche_mm,
            type_fichier=type_fichier,segmentation_objets=segmentation_objets,analyse_florence=analyse_florence,
            profil_segmentation=profil_segmentation,raffinement_contours=raffinement_contours,
            contacts_objets=contacts_objets,ia_locale='auto',
            masque_png=masque_png,masques_objets=masques_objets)

NODE_CLASS_MAPPINGS={**OLD_CLASSES,
    'SmartSVGStudioV195Expert':SmartSVGStudioV195Expert,
    'SmartSVGStudioV195Express':SmartSVGStudioV195Express,
    'SmartSVGStudioV1951Expert':SmartSVGStudioV195Expert,
    'SmartSVGStudioV1951Express':SmartSVGStudioV195Express,
    'SmartSVGStudioV1952Expert':SmartSVGStudioV195Expert,
    'SmartSVGStudioV1952Express':SmartSVGStudioV195Express}
NODE_DISPLAY_NAME_MAPPINGS={**OLD_NAMES,
    'SmartSVGStudioV195Expert':'SmartSVG V19.5 Expert — Florence2 + SAM2 + contacts Cricut',
    'SmartSVGStudioV195Express':'SmartSVG V19.5 (compatibilite V19.5.1)',
    'SmartSVGStudioV1951Expert':'SmartSVG V19.5.1 Expert — contacts securises',
    'SmartSVGStudioV1951Express':'SmartSVG V19.5.1 Express — contacts securises',
    'SmartSVGStudioV1952Expert':'SmartSVG V19.5.2 Expert — QA masques et Cricut',
    'SmartSVGStudioV1952Express':'SmartSVG V19.5.2 Express — QA masques et Cricut'}
