"""V19.6 conservative mask comparison & read-only RTX/ComfyUI diagnostics.

The legacy V19.5.2 production pipeline is unmodified. Additional masks from
RMBG FeyNoBg/Finegrain (or SAM2) must be connected explicitly and registered
in source-image coordinates. No fake masks, no hidden GPU model downloads.
"""
import json
import numpy as np
import torch
from .mask_compare_v196 import compare_mask_sets, MaskComparisonError
from .telemetry_v197 import track_stage
from .node_v195 import (SmartSVGStudioV195Expert, SmartSVGStudioV195Express,
                         NODE_CLASS_MAPPINGS as BASE_CLASSES,
                         NODE_DISPLAY_NAME_MAPPINGS as BASE_DISPLAY)


def _image_u8(tensor):
    if not isinstance(tensor,torch.Tensor) or tensor.ndim!=4 or tensor.shape[0]!=1 or tensor.shape[3]<3:
        raise ValueError('IMAGE: lot d une seule image RGB attendu [1,H,W,3]')
    return np.uint8(np.clip(tensor[0,:,:,:3].detach().cpu().numpy(),0,1)*255+.5)


def _mask_numpy(tensor):
    if tensor is None:return None
    if not isinstance(tensor,torch.Tensor) or tensor.ndim!=3:
        raise ValueError('MASK: tenseur [N,H,W] requis')
    return tensor.detach().cpu().numpy()


class SmartSVGCompareMasksV196:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'image':('IMAGE',),
            'masque_reference':('MASK',),
            'mode_comparaison':(['conservateur','diagnostic','selection_prudente'],{'default':'diagnostic'}),
        },'optional':{'masque_alternative_B':('MASK',),'masque_alternative_C':('MASK',),
                      'masque_annote':('MASK',)}}
    RETURN_TYPES=('MASK','STRING')
    RETURN_NAMES=('masque_selectionne','rapport_comparaison')
    FUNCTION='run'
    CATEGORY='SmartSVG / Cricut'
    def run(self,image,masque_reference,mode_comparaison='diagnostic',
            masque_alternative_B=None,masque_alternative_C=None,masque_annote=None):
        with track_stage("Comparaison des masques"):
            chosen,report=compare_mask_sets(_image_u8(image),_mask_numpy(masque_reference),
                _mask_numpy(masque_alternative_B),_mask_numpy(masque_alternative_C),
                mode=mode_comparaison,annotated=_mask_numpy(masque_annote))
        return (torch.from_numpy(chosen.copy()),json.dumps(report,ensure_ascii=False,indent=2))


class SmartSVGStudioV196Expert(SmartSVGStudioV195Expert):
    @classmethod
    def INPUT_TYPES(cls):
        original=super().INPUT_TYPES()
        required=dict(original['required']); optional=dict(original['optional'])
        required['comparaison_masques']=(['desactiver','diagnostic','selection_prudente'],{'default':'diagnostic'})
        optional.update({'masque_alternative_B':('MASK',),'masque_alternative_C':('MASK',),
                         'masque_annote':('MASK',)})
        return {'required':required,'optional':optional}

    def execute(self,image,comparaison_masques='diagnostic',masque_alternative_B=None,
                masque_alternative_C=None,masque_annote=None,**kwargs):
        reference=kwargs.get('masques_objets')
        report=None
        if comparaison_masques!='desactiver' and reference is not None:
            with track_stage("Comparaison des masques"):
                chosen,report=compare_mask_sets(_image_u8(image),_mask_numpy(reference),
                    _mask_numpy(masque_alternative_B),_mask_numpy(masque_alternative_C),
                    mode=comparaison_masques,annotated=_mask_numpy(masque_annote))
            kwargs['masques_objets']=torch.from_numpy(chosen.copy())
        elif masque_alternative_B is not None or masque_alternative_C is not None:
            # Never silently let a second mask stand in for a missing reference.
            raise MaskComparisonError('Une alternative est connectee sans masque reference. Connecter masques_objets ou utiliser le comparateur autonome.')
        image_out,txt=super().execute(image=image,**kwargs)
        if report is None:
            suffix='V19.6 comparateur: non lance (aucun masque de reference ou mode desactive).'
        else:
            n=sum(v!='reference' for v in report['selection'])
            suffix=(f'V19.6 comparateur: {n}/{report["nombre_objets"]} masques alternatifs retenus; '
                    'classement heuristique non certifie; masques sources preserves.')
        return image_out,txt+'\n'+suffix


class SmartSVGStudioV196Express(SmartSVGStudioV196Expert):
    @classmethod
    def INPUT_TYPES(cls):
        old=SmartSVGStudioV195Express.INPUT_TYPES()
        required=dict(old['required']);opt=dict(old['optional'])
        required['comparaison_masques']=(['desactiver','diagnostic','selection_prudente'],{'default':'diagnostic'})
        opt.update({'masque_alternative_B':('MASK',),'masque_alternative_C':('MASK',),
                    'masque_annote':('MASK',)})
        return {'required':required,'optional':opt}
    FUNCTION='execute_express'
    CATEGORY='SmartSVG / Cricut'
    OUTPUT_NODE=True
    def execute_express(self,image,dossier_sortie,largeur_planche_mm=180,type_fichier='auto',
                        segmentation_objets='auto',profil_segmentation='auto',analyse_florence='auto',
                        raffinement_contours='conservateur',contacts_objets='conservateur',
                        comparaison_masques='diagnostic',masque_png=None,masques_objets=None,
                        masque_alternative_B=None,masque_alternative_C=None,masque_annote=None):
        return self.execute(image,dossier_sortie=dossier_sortie,largeur_planche_mm=largeur_planche_mm,
                            type_fichier=type_fichier,segmentation_objets=segmentation_objets,
                            analyse_florence=analyse_florence,profil_segmentation=profil_segmentation,
                            raffinement_contours=raffinement_contours,contacts_objets=contacts_objets,
                            comparaison_masques=comparaison_masques,masque_png=masque_png,
                            masques_objets=masques_objets,masque_alternative_B=masque_alternative_B,
                            masque_alternative_C=masque_alternative_C,masque_annote=masque_annote,ia_locale='auto')


class SmartSVGGpuDiagnosticV196:
    @classmethod
    def INPUT_TYPES(cls):return {'required':{'profil_gpu':(['rtx3070_8go','automatique'],{'default':'rtx3070_8go'})}}
    RETURN_TYPES=('STRING',)
    FUNCTION='inspect'
    CATEGORY='SmartSVG / Cricut'
    OUTPUT_NODE=True
    def inspect(self,profil_gpu='rtx3070_8go'):
        status={'profil':profil_gpu,'validation_gpu_reelle_effectuee':False,
                'torch_version':str(torch.__version__), 'cuda_disponible':bool(torch.cuda.is_available()),
                'noms_noeuds_RMBG':[],
                'conseil':'Comparer un modele a la fois. Ne pas charger FeyNoBg et SAM2 simultanement sur 8 Go.'}
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                p=torch.cuda.get_device_properties(i)
                status.setdefault('cartes',[]).append({'nom':p.name,'vram_gio':round(p.total_memory/1024**3,2),
                    'mem_allouee_mio':round(torch.cuda.memory_allocated(i)/1024**2,1)})
        try:
            import nodes
            registry=nodes.NODE_CLASS_MAPPINGS
            status['noms_noeuds_RMBG']=sorted(k for k in registry if any(s in k.lower() for s in
                ('sam2','fey','finegrain','florence','rmbg')))[:70]
        except Exception as exc:status['registre_noeuds']='indisponible: '+str(exc)[:120]
        return (json.dumps(status,ensure_ascii=False,indent=2),)


NODE_CLASS_MAPPINGS={**BASE_CLASSES,
                     'SmartSVGStudioV196Express':SmartSVGStudioV196Express,
                     'SmartSVGStudioV196Expert':SmartSVGStudioV196Expert,
                     'SmartSVGCompareMasksV196':SmartSVGCompareMasksV196,
                     'SmartSVGGpuDiagnosticV196':SmartSVGGpuDiagnosticV196}
NODE_DISPLAY_NAME_MAPPINGS={**BASE_DISPLAY,
                     'SmartSVGStudioV196Express':'SmartSVG V19.6 Express (comparer masques + Cricut)',
                     'SmartSVGStudioV196Expert':'SmartSVG V19.6 Expert (comparaison prudente)',
                     'SmartSVGCompareMasksV196':'SmartSVG V19.6 Comparer 3 masques (sans IA)',
                     'SmartSVGGpuDiagnosticV196':'SmartSVG V19.6 Diagnostic RTX / RMBG'}
