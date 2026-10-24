"""SmartSVG V20.2 line art + optional real SAM2/Flo2; all older aliases retained."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import torch
from .node_v2012 import NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .cricut_choice_v2012 import OPTIONS
from .lineart_ai_v202 import process_lineart_ai

class SmartSVGLineArtV202:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'image':('IMAGE',),
            'dossier_sortie':('STRING',{'default':r'C:\Users\Public\Documents\Cricut_SVG'}),
            'source':(['auto','scan','photo','capture_ecran','photo_ecran'],{'default':'auto'}),
            'cible_decoupe':(['carte','personnage','sticker'],{'default':'sticker'}),
            'operation_cricut':(list(OPTIONS),{'default':'imprimer_decouper_contour'}),
            'nettoyage':(['doux','fort'],{'default':'doux'}),
            'corriger_perspective':('BOOLEAN',{'default':True}),
            'marge_blanche_px':('INT',{'default':10,'min':0,'max':60,'step':1}),
            'largeur_finale_mm':('INT',{'default':90,'min':20,'max':280,'step':1}),
            'segmentation_ia':(['auto','forcer','desactiver'],{'default':'auto'}),
            'analyse_florence':(['auto','forcer','desactiver'],{'default':'auto'}),
            'profil_segmentation':(['personne','auto','cadeaux','chopes','personne_cadeaux','animaux'],{'default':'personne'}),
            'prompt_personnalise':('STRING',{'default':'','multiline':False}),
            'repere_masque':(['source','carte_redressee'],{'default':'source'}),
        },'optional':{'masques_objets':('MASK',)}}
    RETURN_TYPES=('IMAGE','STRING')
    RETURN_NAMES=('apercu_qa','rapport_export')
    FUNCTION='run'
    OUTPUT_NODE=True
    CATEGORY='SmartSVG / Cricut / Dessin'
    def run(self,image,dossier_sortie,source='auto',cible_decoupe='sticker',
            operation_cricut='imprimer_decouper_contour',nettoyage='doux',
            corriger_perspective=True,marge_blanche_px=10,largeur_finale_mm=90,
            segmentation_ia='auto',
            analyse_florence='auto',profil_segmentation='personne',prompt_personnalise='',
            repere_masque='source',masques_objets=None):
        if not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1 or image.shape[-1] not in (3,4):
            raise ValueError('IMAGE ComfyUI [1,H,W,3/4] unique requise')
        x=image[0].detach().cpu().numpy()
        if not np.isfinite(x).all():raise ValueError('IMAGE contient NaN/Inf')
        raw=np.uint8(np.clip(x,0,1)*255+.5)
        if not dossier_sortie.strip():
            import folder_paths
            dossier_sortie=str(Path(folder_paths.get_output_directory())/'SmartSVG')
        # Prefer ComfyUI native MASK batch [N,H,W], unchanged for alignment.
        result=process_lineart_ai(raw,dossier_sortie,source=source,target=cible_decoupe,
                mode=nettoyage,rectify=corriger_perspective,white_margin_px=marge_blanche_px,
                ia=segmentation_ia,profile=profil_segmentation,analyse_florence=analyse_florence,
                prompt=prompt_personnalise,masks=masques_objets,mask_space=repere_masque,
                operation=operation_cricut,width_mm=largeur_finale_mm)
        preview=result['base']['preview']
        tensor=torch.from_numpy(np.ascontiguousarray(preview.astype(np.float32)/255.)).unsqueeze(0)
        msg=json.dumps({'dossier':result['root'],'dossier_qa_ia':result['qa'],
            'candidat_sticker':result['image_candidat'],
            'fichier_mode_choisi':result['fichier_mode_choisi'],
            'statut_fichier':result['mode_choisi_provenance'],
            'choix_cricut':result['choix'], 'analyse':result['report'],
            'rapport_lineart':result['base']['report']},ensure_ascii=False,indent=2,allow_nan=False)
        return {'ui':{'text':[msg]},'result':(tensor,msg)}

NODE_CLASS_MAPPINGS={**OLD,'SmartSVGLineArtV202':SmartSVGLineArtV202}
NODE_DISPLAY_NAME_MAPPINGS={**OLD_NAMES,'SmartSVGLineArtV202':
        'SmartSVG V20.2 - Dessin Photo + Florence2 / SAM2 (candidat Cricut)'}
