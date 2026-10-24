"""Two ComfyUI entry points: Express and Expert. Both use V16 validated exports."""
from pathlib import Path
import gc
import numpy as np
import torch

from .node_v11 import SmartSVGStudioV11
from .rmbg_bridge import invoke_rmbg
from .engine_v16 import process_v16

class SmartSVGStudioV16Expert(SmartSVGStudioV11):
    """Keeps the exact V15 advanced input contract for easy migration."""
    @classmethod
    def INPUT_TYPES(cls):
        return super().INPUT_TYPES()

    def _rmbg_mask(self, image_np):
        mask, metadata=invoke_rmbg(self,image_np)
        self._rmbg_stats.append(metadata)
        return mask

    def execute(self,image,dossier_sortie,type_entree='auto',type_creation='auto',ia_locale='auto',
                largeur_planche_mm=180,marge_sticker_mm=1.5,couleurs_svg_simplifie=10,
                masque_png=None):
        if image.ndim!=4 or image.shape[0]!=1:
            raise ValueError('Une image ou planche par execution, forme attendue [1,H,W,C]')
        rgb=np.uint8(np.clip(image[0].detach().cpu().numpy()[...,:3],0,1)*255+.5)
        folder=str(dossier_sortie).strip()
        if not folder:
            import folder_paths
            folder=str(Path(folder_paths.get_output_directory())/'SmartSVG')
        alpha=None
        if masque_png is not None:
            if masque_png.ndim!=3 or masque_png.shape[0]!=1:
                raise ValueError('MASK doit etre [1,H,W]')
            alpha=np.uint8((1-np.clip(masque_png[0].detach().cpu().numpy(),0,1))*255+.5)
            if alpha.shape!=rgb.shape[:2]:raise ValueError('Image et masque de tailles differentes')
        self._rmbg_stats=[]
        try:
            report,preview=process_v16(rgb,folder,layout=type_entree,intent=type_creation,
                ia_mode=ia_locale,ai_masker=self._rmbg_mask if ia_locale!='desactiver' else None,
                alpha=alpha,sheet_width_mm=largeur_planche_mm,margin_mm=marge_sticker_mm,
                editable_colors=couleurs_svg_simplifie,runtime_rmbg_stats=self._rmbg_stats)
        finally:
            self._rmbg_backend=None
            self._rmbg_backend_class=None
            gc.collect()
            if torch.cuda.is_available():torch.cuda.empty_cache()
        qa=report['audit_v16']
        message=(f'SmartSVG V16 : {qa["nombre_stickers"]} sticker(s); 1 planche + PNG/SVG individuels.\n'
                 f'KIT A IMPORTER : {report["output"]}/{"KIT_IMPORT_CRICUT"}\n'
                 f'Dimensions : {qa["largeur_planche_mm"]:.1f} x {qa["hauteur_planche_mm"]:.1f} mm; '
                 f'densite source {qa["densite_pixels_effective_dpi"]:.0f} DPI.\n'
                 f'IA: {report["audit_v141"]["ia"]["etat"]}.\n'
                 'PNG = impression fidele ; SVG = couleur/regions ; APLATIR les calques avant Print Then Cut.\n'
                 'Cricut et inférence GPU réelles non testées sur ce PC.')
        return (torch.from_numpy(np.asarray(preview.convert('RGB'),dtype=np.float32).copy()/255).unsqueeze(0), message)

class SmartSVGStudioV16Express(SmartSVGStudioV16Expert):
    """One input, one global output directory, size, optional local AI; all other values automatic."""
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'image': ('IMAGE',),
            'dossier_sortie': ('STRING',{'default':r'C:\Users\Public\Documents\Cricut_SVG','multiline':False}),
            'largeur_planche_mm': ('INT',{'default':180,'min':30,'max':290,'step':5}),
            'ia_locale': (['auto','forcer','desactiver'],{'default':'auto'}),
        },'optional':{'masque_png':('MASK',)}}
    FUNCTION='execute_express'
    CATEGORY='SmartSVG / Cricut'
    OUTPUT_NODE=True

    def execute_express(self,image,dossier_sortie,largeur_planche_mm=180,ia_locale='auto',masque_png=None):
        return self.execute(image,dossier_sortie,type_entree='auto',type_creation='auto',
                            ia_locale=ia_locale,largeur_planche_mm=largeur_planche_mm,
                            marge_sticker_mm=1.5,couleurs_svg_simplifie=10,masque_png=masque_png)

NODE_CLASS_MAPPINGS={'SmartSVGStudioV16Express':SmartSVGStudioV16Express,
                     'SmartSVGStudioV16Expert':SmartSVGStudioV16Expert}
NODE_DISPLAY_NAME_MAPPINGS={'SmartSVGStudioV16Express':'SmartSVG V16 Express — Cricut en 1 clic',
                            'SmartSVGStudioV16Expert':'SmartSVG V16 Expert — Cricut + IA locale'}
