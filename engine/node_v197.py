"""V19.7 optional wall-clock and process CUDA instrumentation.

No inference is run just for benchmarking: wrap the real V19.6 execution.
Only internal Florence-2/SAM2 calls are measured; external RMBG nodes are NOT.
"""
from pathlib import Path
import json
from .telemetry_v197 import RunProfile, save_profile
from .node_v196 import (SmartSVGStudioV196Expert, SmartSVGStudioV196Express,
                        NODE_CLASS_MAPPINGS as OLD_CLASSES,
                        NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES)


class SmartSVGStudioV197Expert(SmartSVGStudioV196Expert):
    @classmethod
    def INPUT_TYPES(cls):
        orig=super().INPUT_TYPES()
        req=dict(orig['required']);opt=dict(orig['optional'])
        req['profil_performances']=(['activer','desactiver'],{'default':'activer'})
        return {'required':req,'optional':opt}

    def execute(self,image,profil_performances='activer',**kwargs):
        if profil_performances=='desactiver':
            return super().execute(image=image,**kwargs)
        if profil_performances!='activer':
            raise ValueError('profil_performances : mode inconnu')
        profile=RunProfile(enabled=True)
        root=str(kwargs.get('dossier_sortie','')).strip()
        if not root:
            import folder_paths
            root=str(Path(folder_paths.get_output_directory())/'SmartSVG')
        try:
            with profile.activate():
                with profile.stage('SmartSVG / traitement complet'):
                    result=super().execute(image=image,**kwargs)
            profile.status='REUSSI'
        except Exception as exc:
            profile.status='ECHEC'
            profile.failure=f'{type(exc).__name__}: {str(exc)[:220]}'
            try:
                save_profile(profile,root)
            except Exception:
                pass
            raise
        try:
            path=save_profile(profile,root)
            image_result,text_result=result
            anomalies=sum(e['statut']=='ERREUR' for e in profile.events)
            return (image_result,text_result+f'\nV19.7 profil reel: {path}\n'
                    + (f'ATTENTION: {anomalies} etape(s) ont echoue; voir le JSON.\n' if anomalies else '')
                    + 'Les modeles externes deja executes ne sont pas chronometres.')
        except Exception as exc:
            # The exported PNG/SVG stays valid; warn instead of silently losing
            # the only performance report that the user expected.
            try:
                image_result,text_result=result
                return (image_result, text_result + '\nATTENTION: mesure terminee mais rapport performances non enregistre ('
                        +type(exc).__name__+'). Les fichiers Cricut sont conserves.')
            except Exception:
                return result



class SmartSVGStudioV197Express(SmartSVGStudioV197Expert):
    @classmethod
    def INPUT_TYPES(cls):
        old=SmartSVGStudioV196Express.INPUT_TYPES()
        req=dict(old['required']);opt=dict(old['optional'])
        req['profil_performances']=(['activer','desactiver'],{'default':'activer'})
        return {'required':req,'optional':opt}
    FUNCTION='execute_express'
    CATEGORY='SmartSVG / Cricut'
    OUTPUT_NODE=True
    def execute_express(self,image,dossier_sortie,largeur_planche_mm=180,type_fichier='auto',
                        segmentation_objets='auto',profil_segmentation='auto',analyse_florence='auto',
                        raffinement_contours='conservateur',contacts_objets='conservateur',
                        comparaison_masques='diagnostic',profil_performances='activer',
                        masque_png=None,masques_objets=None,masque_alternative_B=None,
                        masque_alternative_C=None,masque_annote=None):
        return self.execute(image,dossier_sortie=dossier_sortie,largeur_planche_mm=largeur_planche_mm,
            type_fichier=type_fichier,segmentation_objets=segmentation_objets,
            analyse_florence=analyse_florence,profil_segmentation=profil_segmentation,
            raffinement_contours=raffinement_contours,contacts_objets=contacts_objets,
            comparaison_masques=comparaison_masques,profil_performances=profil_performances,
            masque_png=masque_png,masques_objets=masques_objets,
            masque_alternative_B=masque_alternative_B,masque_alternative_C=masque_alternative_C,
            masque_annote=masque_annote,ia_locale='auto')


NODE_CLASS_MAPPINGS={**OLD_CLASSES,
                     'SmartSVGStudioV197Express':SmartSVGStudioV197Express,
                     'SmartSVGStudioV197Expert':SmartSVGStudioV197Expert}
NODE_DISPLAY_NAME_MAPPINGS={**OLD_NAMES,
                     'SmartSVGStudioV197Express':'SmartSVG V19.7 Express (profil performances)',
                     'SmartSVGStudioV197Expert':'SmartSVG V19.7 Expert (profil IA locale)'}
