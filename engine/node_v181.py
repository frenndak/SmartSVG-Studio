"""V18.1 ComfyUI contract: explicit coordinate space, no silently resized masks."""
import gc
from pathlib import Path
import numpy as np
import torch
from .node_v18 import SmartSVGStudioV18Expert, SmartSVGStudioV18Express, NODE_CLASS_MAPPINGS as OLD_NODES, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .engine_v18 import process_v18
from .telemetry_v197 import record_output_path, track_stage

class SmartSVGStudioV181Expert(SmartSVGStudioV18Expert):
    @classmethod
    def INPUT_TYPES(cls):
        original=super().INPUT_TYPES()
        d=dict(original['required'])
        d['repere_masques']=(['planche','source'],{'default':'planche'})
        d['transformation_masques_json']=('STRING',{'default':'','multiline':True})
        return {'required':d,'optional':dict(original['optional'])}

    def execute(self,image,dossier_sortie,type_entree='auto',type_creation='auto',ia_locale='auto',
                largeur_planche_mm=180,marge_sticker_mm=1.5,couleurs_svg_simplifie=10,
                mode_objets='auto',noms_objets='',repere_masques='planche',transformation_masques_json='',
                masque_png=None,masques_objets=None):
        if image.ndim!=4 or image.shape[0]!=1:
            raise ValueError('Attendu image [1,H,W,C]')
        rgb=np.uint8(np.clip(image[0].detach().cpu().numpy()[...,:3],0,1)*255+.5)
        folder=str(dossier_sortie).strip()
        if not folder:
            import folder_paths
            folder=str(Path(folder_paths.get_output_directory())/'SmartSVG')
        alpha=None
        if masque_png is not None:
            if masque_png.ndim!=3 or masque_png.shape[0]!=1:raise ValueError('Masque PNG: [1,H,W]')
            alpha=np.uint8((1-np.clip(masque_png[0].detach().cpu().numpy(),0,1))*255+.5)
            if alpha.shape!=rgb.shape[:2]:raise ValueError('Masque PNG dimensions incorrectes')
        external=masques_objets.detach().cpu().numpy() if masques_objets is not None else None
        self._rmbg_stats=[]
        try:
            with track_stage("Sticker / vectorisation et preparation Cricut"):
                r,preview=process_v18(rgb,folder,layout=type_entree,intent=type_creation,
               ia_mode=ia_locale,ai_masker=self._rmbg_mask if ia_locale!='desactiver' else None,
               alpha=alpha,sheet_width_mm=largeur_planche_mm,margin_mm=marge_sticker_mm,
               editable_colors=couleurs_svg_simplifie,runtime_rmbg_stats=self._rmbg_stats,
               object_masks=external,object_labels=noms_objets,object_mode=mode_objets,
               mask_space=repere_masques,mask_transform_json=transformation_masques_json)
        finally:
            self._rmbg_backend=None;self._rmbg_backend_class=None
            gc.collect()
            if torch.cuda.is_available():torch.cuda.empty_cache()
        record_output_path(r["output"])
        q=r['audit_v18']['objets'];group=q['version_fidele_groupes']
        method=q['mode'];used=q['masques_externes_utilises']
        warning=(' ATTENTION masque externe rejete: '+str(q['erreur_masques'])) if q.get('erreur_masques') else ''
        result=(f'SmartSVG V18.1 : {q["nombre_stickers"]} stickers, {q["objets_proposes"]} propositions.\n'
                f'Methode reels: {method}; masques externes retenus: {used}.\n'
                f'Courbes: {group["chemins_reclasses"]} chemins affectes / '
                f'{group["chemins_residuels"]} conserves comme residus.\n'
                f'State QA: {r["output"]}\n'
                'Import Cricut: 01 PNG fidelite / 04 SVG courbes apres verification Aplatir.\n'+warning)
        return (torch.from_numpy(np.asarray(preview.convert('RGB'),np.float32).copy()/255).unsqueeze(0),result)

class SmartSVGStudioV181Express(SmartSVGStudioV181Expert):
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'image':('IMAGE',),
            'dossier_sortie':('STRING',{'default':r'C:\Users\Public\Documents\Cricut_SVG','multiline':False}),
            'largeur_planche_mm':('INT',{'default':180,'min':30,'max':290,'step':5}),
            'ia_locale':(['auto','forcer','desactiver'],{'default':'auto'})},
            'optional':{'masque_png':('MASK',),'masques_objets':('MASK',)}}
    FUNCTION='execute_express'
    CATEGORY='SmartSVG / Cricut'
    OUTPUT_NODE=True
    def execute_express(self,image,dossier_sortie,largeur_planche_mm=180,ia_locale='auto',masque_png=None,masques_objets=None):
        return self.execute(image,dossier_sortie,ia_locale=ia_locale,largeur_planche_mm=largeur_planche_mm,
                            masque_png=masque_png,masques_objets=masques_objets)

NODE_CLASS_MAPPINGS={
 'SmartSVGStudioV181Expert':SmartSVGStudioV181Expert,
 'SmartSVGStudioV181Express':SmartSVGStudioV181Express,
 'SmartSVGStudioV18Expert':SmartSVGStudioV18Expert,
 'SmartSVGStudioV18Express':SmartSVGStudioV18Express}
NODE_DISPLAY_NAME_MAPPINGS={
 'SmartSVGStudioV181Expert':'SmartSVG V18.1 Expert (masques alignes + recouvrement)',
 'SmartSVGStudioV181Express':'SmartSVG V18.1 Express (Cricut + audit)',
 'SmartSVGStudioV18Expert':'SmartSVG V18 Expert (ancien workflow)',
 'SmartSVGStudioV18Express':'SmartSVG V18 Express (ancien workflow)'}

# Preserve V16/V17 historical node IDs for existing saved ComfyUI workflows.
NODE_CLASS_MAPPINGS.update({k:v for k,v in OLD_NODES.items() if k not in NODE_CLASS_MAPPINGS})
NODE_DISPLAY_NAME_MAPPINGS.update({k:v for k,v in OLD_NAMES.items() if k not in NODE_DISPLAY_NAME_MAPPINGS})
