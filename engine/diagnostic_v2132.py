"""Non-invasive environment and model-interface diagnostic for SmartSVG.

No weights are loaded, no models downloaded and no inference is performed.
Registry presence is deliberately *not* treated as proof weights are installed.
"""
from __future__ import annotations
import json


def _status(registry, torch_module):
    result = {
        'version':'21.3.2',
        'comfyui_registry_disponible':registry is not None,
        'florence_noeud': 'ABSENT',
        'sam2_noeud':'ABSENT',
        'cuda':'NON_VERIFIE',
        'gpu_nom':None,
        'vram_libre_gio':None,
        'modeles_poids_charges_et_testes':False,
        'detourage_ia_execute':False,
        'validation_cricut_reelle':False,
        'avertissements':[],
    }
    if registry is not None:
        florence=registry.get('AILab_Florence2')
        if florence is not None:
            try:
                spec=florence.INPUT_TYPES()
                required=spec.get('required',{})
                result['florence_noeud']='INTERFACE_PRESENTE' if all(k in required for k in ('model_name','task','image')) else 'INTERFACE_INCOMPATIBLE'
            except Exception:
                result['florence_noeud']='INTERFACE_INCOMPATIBLE'
        try:
            from .auto_segment_v192 import _registry_class
            _registry_class(registry)
            result['sam2_noeud']='INTERFACE_COMPATIBLE'
        except Exception:
            result['sam2_noeud']='ABSENT_OU_INCOMPATIBLE'
    if torch_module is not None:
        try:
            if torch_module.cuda.is_available():
                result['cuda']='DISPONIBLE'
                try:
                    result['gpu_nom']=str(torch_module.cuda.get_device_name())
                except Exception:
                    result['avertissements'].append('NOM_GPU_INDISPONIBLE')
                try:
                    free,total=torch_module.cuda.mem_get_info()
                    if 0<=free<=total and total>0:
                        result['vram_libre_gio']=round(free/1073741824,2)
                        result['vram_totale_gio']=round(total/1073741824,2)
                    else:
                        result['avertissements'].append('MESURE_VRAM_INVALIDE')
                except Exception:
                    result['avertissements'].append('MESURE_VRAM_INDISPONIBLE')
            else:result['cuda']='INDISPONIBLE'
        except Exception:
            result['cuda']='CONTROLE_ECHOUE'
    if result['florence_noeud']!='INTERFACE_PRESENTE':
        result['avertissements'].append('VERIFIER_COMFYUI_RMBG_FLORENCE')
    if result['sam2_noeud']!='INTERFACE_COMPATIBLE':
        result['avertissements'].append('VERIFIER_COMFYUI_RMBG_SAM2')
    if result['cuda']!='DISPONIBLE':
        result['avertissements'].append('IA_GPU_NON_VERIFIEE')
    return result


def diagnostics(registry=None,torch_module=None):
    return _status(registry,torch_module)


def render_diagnostic(report):
    return (f"SmartSVG V21.3.2 — diagnostic local\n"
        f"GPU : {report['cuda']} | {report.get('gpu_nom') or 'non identifie'}\n"
        f"VRAM libre : {report['vram_libre_gio'] if report['vram_libre_gio'] is not None else 'non mesuree'} Gio\n"
        f"Florence-2 : {report['florence_noeud']} | SAM2 : {report['sam2_noeud']}\n"
        "Ce controle ne charge pas les poids IA et ne valide aucune decoupe Cricut.\n"
        "En cas d'absence de modeles, utiliser le workflow Express sans IA.")
