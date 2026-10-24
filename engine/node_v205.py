"""SmartSVG 20.5: Cricut preflight additive nodes."""
import json
from .node_v204 import SmartSVGLineArtV204, NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .cricut_preflight_v205 import audit_project,atomic_qa,OPERATIONS,FORMATS

class SmartSVGLineArtV205(SmartSVGLineArtV204):
    @classmethod
    def INPUT_TYPES(cls):
        old=SmartSVGLineArtV204.INPUT_TYPES()
        req=dict(old['required']);opt=dict(old.get('optional',{}))
        req['controle_cricut']=(['activer','desactiver'],{'default':'activer'})
        req['format_papier']=(list(FORMATS),{'default':'A4'})
        return {'required':req,'optional':opt}
    FUNCTION='run';CATEGORY='SmartSVG / Cricut / Prevol'
    def run(self,image,dossier_sortie,source='auto',cible_decoupe='sticker',
            operation_cricut='imprimer_decouper_contour',nettoyage='doux',
            corriger_perspective=True,marge_blanche_px=10,largeur_finale_mm=90,
            segmentation_ia='auto',analyse_florence='auto',profil_segmentation='personne',
            prompt_personnalise='',repere_masque='source',masques_objets=None,
            politique_gpu='protege',vram_libre_min_gio=2.5,marge_securite_gio=.5,
            controle_contours='activer',controle_cricut='activer',format_papier='A4'):
        if controle_cricut not in ('activer','desactiver') or format_papier not in FORMATS:
            raise ValueError('Parametres de controle Cricut invalides')
        old=super().run(image=image,dossier_sortie=dossier_sortie,source=source,
            cible_decoupe=cible_decoupe,operation_cricut=operation_cricut,nettoyage=nettoyage,
            corriger_perspective=corriger_perspective,marge_blanche_px=marge_blanche_px,
            largeur_finale_mm=largeur_finale_mm,segmentation_ia=segmentation_ia,
            analyse_florence=analyse_florence,profil_segmentation=profil_segmentation,
            prompt_personnalise=prompt_personnalise,repere_masque=repere_masque,
            masques_objets=masques_objets,politique_gpu=politique_gpu,
            vram_libre_min_gio=vram_libre_min_gio,marge_securite_gio=marge_securite_gio,
            controle_contours=controle_contours)
        result=json.loads(old['result'][1])
        if controle_cricut=='desactiver':
            result['controle_cricut_v20_5']={'statut':'DESACTIVE','validation_humaine_obligatoire':True}
        else:
            try:
                r,preview=audit_project(result['dossier'],operation=operation_cricut,
                    width_mm=float(largeur_finale_mm),paper=format_papier,
                    chosen_file=result['fichier_mode_choisi'])
                result['controle_cricut_v20_5']=atomic_qa(result['dossier'],r,preview)
            except Exception as exc:
                result['controle_cricut_v20_5']={'statut':'ECHEC_PREFLIGHT','erreur':type(exc).__name__,
                    'validation_humaine_obligatoire':True,'exports_historiques_conserves':True}
        result['version_prevol']='20.5-beta'
        payload=json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)
        return {'ui':{'text':[payload]},'result':(old['result'][0],payload)}

class SmartSVGCricutPreflightV205:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'dossier_projet':('STRING',{'default':r'C:\Users\Public\Documents\Cricut_SVG\LineArt_V20_1_exemple'}),
            'operation_cricut':(list(OPERATIONS),{'default':'imprimer_decouper_contour'}),
            'largeur_dessin_mm':('FLOAT',{'default':90.,'min':20.,'max':280.,'step':1.}),
            'format_papier':(list(FORMATS),{'default':'A4'}),
            'source_contour':(['historique','ia_candidat'],{'default':'historique'})}}
    RETURN_TYPES=('STRING',);RETURN_NAMES=('rapport_prevol_cricut',)
    FUNCTION='run';OUTPUT_NODE=True;CATEGORY='SmartSVG / Cricut / Prevol'
    def run(self,dossier_projet,operation_cricut='imprimer_decouper_contour',
            largeur_dessin_mm=90.,format_papier='A4',source_contour='historique'):
        r,preview=audit_project(dossier_projet,operation_cricut,largeur_dessin_mm,format_papier,source_contour)
        r=atomic_qa(dossier_projet,r,preview)
        payload=json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False)
        return {'ui':{'text':[payload]},'result':(payload,)}
NODE_CLASS_MAPPINGS={**OLD,'SmartSVGLineArtV205':SmartSVGLineArtV205,'SmartSVGCricutPreflightV205':SmartSVGCricutPreflightV205}
NODE_DISPLAY_NAME_MAPPINGS={**OLD_NAMES,'SmartSVGLineArtV205':'SmartSVG V20.5 - Dessin + controle fabrication Cricut','SmartSVGCricutPreflightV205':'SmartSVG V20.5 - Controle fichier Cricut existant'}
