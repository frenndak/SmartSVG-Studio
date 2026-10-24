"""ComfyUI V18: production V17 plus optional object-mask-based editable SVG."""
from pathlib import Path
import gc
import numpy as np
import torch
from .node_v17 import SmartSVGStudioV17Expert, SmartSVGStudioV17Express
from .engine_v18 import process_v18

class SmartSVGStudioV18Expert(SmartSVGStudioV17Expert):
    @classmethod
    def INPUT_TYPES(cls):
        old=super().INPUT_TYPES()
        return {'required':{**old['required'],
                  'mode_objets':(['auto','masques_requis'],{'default':'auto'}),
                  'noms_objets':('STRING',{'default':'','multiline':True})},
                'optional':{**old['optional'],'masques_objets':('MASK',)}}

    def execute(self,image,dossier_sortie,type_entree='auto',type_creation='auto',ia_locale='auto',
                largeur_planche_mm=180,marge_sticker_mm=1.5,couleurs_svg_simplifie=10,
                mode_objets='auto',noms_objets='',masque_png=None,masques_objets=None):
        if image.ndim!=4 or image.shape[0]!=1:raise ValueError('V18 attend une seule image ou planche [1,H,W,C]')
        rgb=np.uint8(np.clip(image[0].detach().cpu().numpy()[...,:3],0,1)*255+.5)
        out=str(dossier_sortie).strip()
        if not out:
            import folder_paths
            out=str(Path(folder_paths.get_output_directory())/'SmartSVG')
        alpha=None
        if masque_png is not None:
            if masque_png.ndim!=3 or masque_png.shape[0]!=1:raise ValueError('Masque PNG: [1,H,W] attendu')
            alpha=np.uint8((1-np.clip(masque_png[0].detach().cpu().numpy(),0,1))*255+.5)
            if alpha.shape!=rgb.shape[:2]:raise ValueError('Taille du masque PNG incorrecte')
        masks=None
        if masques_objets is not None:
            if masques_objets.ndim!=3:raise ValueError('Masques objets: batch [N,H,W] attendu')
            masks=masques_objets.detach().cpu().numpy()
        self._rmbg_stats=[]
        try:
            report,preview=process_v18(rgb,out,layout=type_entree,intent=type_creation,
                ia_mode=ia_locale,ai_masker=self._rmbg_mask if ia_locale!='desactiver' else None,
                alpha=alpha,sheet_width_mm=largeur_planche_mm,margin_mm=marge_sticker_mm,
                editable_colors=couleurs_svg_simplifie,runtime_rmbg_stats=self._rmbg_stats,
                object_masks=masks,object_labels=noms_objets,object_mode=mode_objets)
        finally:
            self._rmbg_backend=None;self._rmbg_backend_class=None
            gc.collect()
            if torch.cuda.is_available():torch.cuda.empty_cache()
        obj=report['audit_v18']['objets']
        message=(f'SmartSVG V18: {obj["nombre_stickers"]} sticker(s), {obj["objets_proposes"]} objets candidats.\n'
                 f'Masque IA objets utilise: {obj["masques_externes_utilises"]}.\n'
                 f'KIT CRICUT: {report["output"]}/KIT_IMPORT_CRICUT\n'
                 'Pour imprimer: 01 PNG. Pour modifier les objets candidats: 04 SVG.\n'
                 'Ces propositions ne sont pas des identifications semantiques garanties; aucun test machine realise.')
        return (torch.from_numpy(np.asarray(preview.convert('RGB'),dtype=np.float32).copy()/255).unsqueeze(0),message)

class SmartSVGStudioV18Express(SmartSVGStudioV18Expert):
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
        return self.execute(image,dossier_sortie,type_entree='auto',type_creation='auto',
                ia_locale=ia_locale,largeur_planche_mm=largeur_planche_mm,
                marge_sticker_mm=1.5,couleurs_svg_simplifie=10,
                mode_objets='auto',noms_objets='',masque_png=masque_png,masques_objets=masques_objets)

NODE_CLASS_MAPPINGS={
    'SmartSVGStudioV18Express':SmartSVGStudioV18Express,
    'SmartSVGStudioV18Expert':SmartSVGStudioV18Expert,
    'SmartSVGStudioV17Express':SmartSVGStudioV17Express,
    'SmartSVGStudioV17Expert':SmartSVGStudioV17Expert,
    'SmartSVGStudioV16Express':SmartSVGStudioV17Express,
    'SmartSVGStudioV16Expert':SmartSVGStudioV17Expert}
NODE_DISPLAY_NAME_MAPPINGS={
    'SmartSVGStudioV18Express':'SmartSVG V18 Express - Cricut + objets proposes',
    'SmartSVGStudioV18Expert':'SmartSVG V18 Expert - masques IA objets + Cricut',
    'SmartSVGStudioV17Express':'SmartSVG V17 Express (compatibilite)',
    'SmartSVGStudioV17Expert':'SmartSVG V17 Expert (compatibilite)',
    'SmartSVGStudioV16Express':'SmartSVG V16 (compatibilite V17)',
    'SmartSVGStudioV16Expert':'SmartSVG V16 Expert (compatibilite V17)'}
