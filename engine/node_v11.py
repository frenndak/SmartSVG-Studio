"""SmartSVG Studio V11. V9 is kept separately; V11 is a new ComfyUI node."""
from pathlib import Path
import numpy as np
import torch
from .engine_v11 import process_v11


class SmartSVGStudioV11:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'image': ('IMAGE',),
            'dossier_sortie': ('STRING', {'default':r'C:\Users\Public\Documents\Cricut_SVG', 'multiline':False}),
            'type_entree': (['auto','unique','planche'],{'default':'auto'}),
            'type_creation': (['auto','logo','cartoon','illustration_complexe','photo','silhouette'],{'default':'auto'}),
            'ia_locale': (['auto','forcer','desactiver'],{'default':'auto'}),
            'largeur_planche_mm': ('INT',{'default':180,'min':30,'max':290,'step':5}),
            'marge_sticker_mm': ('FLOAT',{'default':1.5,'min':0,'max':5.,'step':.25}),
            'couleurs_svg_simplifie': ('INT',{'default':10,'min':3,'max':32,'step':1}),
        }, 'optional':{'masque_png':('MASK',)}}
    RETURN_TYPES=('IMAGE','STRING')
    RETURN_NAMES=('APERÇU','RAPPORT')
    FUNCTION='execute'
    CATEGORY='SmartSVG / Cricut'
    OUTPUT_NODE=True

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float('nan')

    def _rmbg_mask(self,img_np):
        """Use registered RMBG node, with compatible model from its own INPUT_TYPES.
        The node runtime, not this plugin, manages weights and GPU resources.
        """
        import nodes
        available=nodes.NODE_CLASS_MAPPINGS
        clazz=available.get('RMBG') or available.get('AILab_RMBG')
        if clazz is None:
            matches=[value for key,value in available.items() if key.upper().endswith('RMBG')
                     and getattr(value,'__name__','')=='RMBG']
            clazz=matches[0] if matches else None
        if clazz is None:
            raise RuntimeError('ComfyUI-RMBG non detecte. Ajouter/activer 1038lab/ComfyUI-RMBG.')
        inputs=clazz.INPUT_TYPES().get('required',{})
        model_choices=inputs.get('model',([],))[0]
        if 'INSPYRENET' not in model_choices:
            raise RuntimeError('La version de RMBG ne propose pas INSPYRENET.')
        params={
            'sensitivity':0.5,'process_res':768, 'mask_blur':0,'mask_offset':0,
            'background':'Alpha','invert_output':False,'refine_foreground':False,
            'unload_model':False,'optimize':True,'background_color':'#FFFFFF'
        }
        chosen={}
        for name,typ in inputs.items():
            if name in ('image','model'):continue
            if name in params:
                chosen[name]=params[name]
            elif isinstance(typ,tuple) and len(typ)>1 and isinstance(typ[1],dict) and 'default' in typ[1]:
                chosen[name]=typ[1]['default']
            elif isinstance(typ,tuple) and isinstance(typ[0],(list,tuple)) and typ[0]:
                chosen[name]=typ[0][0]
            else:
                raise RuntimeError(f'Parametre RMBG obligatoire inconnu: {name}. API probablement modifiee.')
        tensor=torch.from_numpy(np.ascontiguousarray(img_np,dtype=np.float32)/255).unsqueeze(0)
        # Reuse one model for all crops within ONE workflow execution.
        # Otherwise each of twelve stickers can cause a costly model reload.
        if getattr(self,'_rmbg_backend_class',None) is not clazz:
            self._rmbg_backend=clazz()
            self._rmbg_backend_class=clazz
        result=self._rmbg_backend.process_image(tensor,'INSPYRENET',**chosen)
        if not isinstance(result,(tuple,list)) or len(result)<2:
            raise RuntimeError('RMBG ne renvoie pas de MASK compatible (sortie 2 requise).')
        mask=result[1]
        if hasattr(mask,'detach'):mask=mask.detach().cpu().numpy()
        mask=np.asarray(mask)
        while mask.ndim>2:mask=mask[0]
        if mask.ndim!=2:raise RuntimeError('Masque IA non bidimensionnel')
        return mask

    def execute(self,image,dossier_sortie,type_entree='auto',type_creation='auto',ia_locale='auto',
                largeur_planche_mm=180,marge_sticker_mm=1.5,couleurs_svg_simplifie=10,
                masque_png=None):
        if image.shape[0]!=1:
            raise ValueError('Une image a la fois, ou une planche contenant plusieurs dessins')
        rgb=np.uint8(np.clip(image[0].detach().cpu().numpy()[...,:3],0,1)*255+0.5)
        folder=dossier_sortie.strip()
        if not folder:
            import folder_paths
            folder=str(Path(folder_paths.get_output_directory())/'SmartSVG')
        alpha=None
        if masque_png is not None:
            if masque_png.shape[0]!=1:
                raise ValueError('Masque PNG: un seul calque par image')
            alpha=np.uint8((1-np.clip(masque_png[0].detach().cpu().numpy(),0,1))*255+0.5)
        try:
            report,preview=process_v11(rgb,folder,layout=type_entree,intent=type_creation,
                ia_mode=ia_locale,ai_masker=self._rmbg_mask if ia_locale!='desactiver' else None,
                alpha=alpha,sheet_width_mm=largeur_planche_mm,
                margin_mm=marge_sticker_mm,editable_colors=couleurs_svg_simplifie)
        finally:
            # Model instance is kept across the 12 crops, but not indefinitely.
            # Let ComfyUI/PyTorch reclaim GPU memory for the next workflow.
            if hasattr(self,'_rmbg_backend'):
                self._rmbg_backend=None
                self._rmbg_backend_class=None
                import gc
                gc.collect()
        arr=np.asarray(preview.convert('RGB'),dtype=np.float32)/255
        tensor=torch.from_numpy(arr.copy()).unsqueeze(0)
        qa=report['qa_v11']
        lines=[f'SmartSVG V11 : {qa["statut"]}',f'Dossier : {report["output"]}',
               f'{qa["contours_total"]} contours pour {qa["dessins"]} dessins',
               f'Impression : {report["fichier_a_importer"]}',
               f'Ecart minimal : {qa["espacement_minimum_mm"]} mm',
               'SVG de couleurs = formes non semantiques',
               'Verifie la previsualisation Design Space avant de fabriquer']
        lines += ['ATTENTION : '+e for e in qa['alertes']]
        return tensor,'\n'.join(lines)

NODE_CLASS_MAPPINGS={'SmartSVGStudioV11':SmartSVGStudioV11}
NODE_DISPLAY_NAME_MAPPINGS={'SmartSVGStudioV11':'SmartSVG Studio V11 — Cricut QA / IA locale / SVG couleurs'}
