"""V21.15 G1.1 compatibility repair: restore two legacy V19.2 IDs.

V19.2 Express workflow contains an ``ia_locale`` widget that its original node
forgot to declare. The adapter accepts the saved widget without changing legacy
sources, replacing no pre-existing registered class, and forwards the setting.
"""
from __future__ import annotations
from .node_v21141 import NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .node_v192 import SmartSVGStudioV192Expert, SmartSVGStudioV192Express
from .smartsvg_compat.registry import merge_registry


class SmartSVGStudioV192ExpressCompat(SmartSVGStudioV192Express):
    @classmethod
    def INPUT_TYPES(cls):
        ports=super().INPUT_TYPES()
        req=dict(ports['required'])
        # Restore serialized V19.2 order so saved widget values are not shifted.
        ordered={}
        for key,value in req.items():
            ordered[key]=value
            if key=='type_fichier':
                ordered['ia_locale']=(['auto','forcer','desactiver'],{'default':'auto'})
        return {'required':ordered,'optional':dict(ports['optional'])}

    def execute_express(self,image,dossier_sortie,largeur_planche_mm=180,type_fichier='auto',
                        ia_locale='auto',segmentation_objets='auto',profil_segmentation='auto',
                        masque_png=None,masques_objets=None):
        return self.execute(image,dossier_sortie,largeur_planche_mm=largeur_planche_mm,
            type_fichier=type_fichier,segmentation_objets=segmentation_objets,
            profil_segmentation=profil_segmentation,ia_locale=ia_locale,
            masque_png=masque_png,masques_objets=masques_objets)


NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS=merge_registry(OLD,OLD_NAMES,{
 'SmartSVGStudioV192Expert':(SmartSVGStudioV192Expert,'Legacy V19.2 Expert — SAM2 Auto + Cricut'),
 'SmartSVGStudioV192Express':(SmartSVGStudioV192ExpressCompat,'Legacy V19.2 Express — SAM2 Auto + Cricut'),
})
