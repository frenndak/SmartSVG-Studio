"""SmartSVG V20.3 — conservative live CUDA preflight and auditable policy.

Only CURRENT observations. Do not infer SAM2/BiRefNet VRAM requirements from a
GPU's marketed memory. No global peak reset, forced unload or cache clearing:
ComfyUI may have other nodes/models resident in the same CUDA process.
"""
from __future__ import annotations
from datetime import datetime, timezone
import math
import time

GIB = 1024 ** 3
POLICIES = ('diagnostic', 'protege', 'strict')


def _safe_read(func, errors, key):
    try:
        value=func()
        return value
    except Exception as exc:
        errors.append({'capteur':key,'erreur':type(exc).__name__})
        return None


def gpu_snapshot(torch_module=None):
    """Process-local allocation & global driver free memory; never a model benchmark.

    Return JSON-serializable dict; absent sensors are explicitly unknown. The
    `global_peak_allocated` field is lifetime-wide (never reset for diagnostics).
    """
    d={'date_utc':datetime.now(timezone.utc).isoformat(),
       'cuda_disponible':False,'capteurs_partiels':False,'erreurs_capteurs':[],
       'mesure_gpu_specifique_modele':False,
       'remarque':'mem_get_info: libre global CUDA; allocated/reserved: allocateur PyTorch du processus; pic historique.'}
    err=d['erreurs_capteurs']
    if torch_module is None:
        torch_module=_safe_read(lambda:__import__('torch'),err,'import_torch')
        if torch_module is None:
            d['raison']='torch_indisponible';d['capteurs_partiels']=True
            return d
    cuda=getattr(torch_module,'cuda',None)
    if cuda is None:
        d['raison']='cuda_api_absente';d['capteurs_partiels']=True
        return d
    available=_safe_read(cuda.is_available,err,'cuda_disponible')
    if not available:
        d['raison']='cuda_indisponible' if available is False else 'test_cuda_echoue'
        d['capteurs_partiels']=bool(err)
        return d
    d['cuda_disponible']=True
    index=_safe_read(cuda.current_device,err,'index_gpu')
    if index is not None:
        d['index_gpu']=int(index)
        props=_safe_read(lambda:cuda.get_device_properties(index),err,'proprietes_gpu')
        if props is not None:
            d['nom_gpu']=str(getattr(props,'name','inconnu'))
            total=getattr(props,'total_memory',None)
            if isinstance(total,(int,float)) and total>0:
                d['vram_physique_bytes']=int(total)
        mem=_safe_read(lambda:cuda.mem_get_info(index),err,'memoire_libre_globale')
        if mem is not None:
            if (isinstance(mem,(tuple,list)) and len(mem)==2
                    and all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in mem)
                    and 0<=mem[0]<=mem[1]):
                d['vram_libre_globale_bytes']=int(mem[0]);d['vram_totale_pilote_bytes']=int(mem[1])
            else:
                err.append({'capteur':'memoire_libre_globale','erreur':'valeurs_invalides'})
        for key, fn in [('pytorch_alloue_bytes',cuda.memory_allocated),
                        ('pytorch_reserve_bytes',cuda.memory_reserved),
                        ('pytorch_pic_historique_alloue_bytes',cuda.max_memory_allocated)]:
            value=_safe_read(lambda fn=fn:fn(index),err,key)
            if isinstance(value,(int,float)) and math.isfinite(value) and value>=0:
                d[key]=int(value)
    d['capteurs_partiels']=bool(err)
    return d


def policy_decision(snapshot, *, policy='protege', free_min_gib=2.5,
                    margin_gib=.5, ia='auto', external_masks=False):
    """Guard internal inference only, not externally obtained masks or exports.

    Threshold is a USER CONFIGURED safety gate; not a benchmark or measured
    requirement for any particular model. A forced IA request is never silently
    downgraded, even under protected policy.
    """
    if policy not in POLICIES:raise ValueError('Politique GPU inconnue')
    if ia not in ('auto','desactiver','forcer'):raise ValueError('Segmentation IA inconnue')
    for name,value in [('free_min_gib',free_min_gib),('margin_gib',margin_gib)]:
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0 or value>16:
            raise ValueError('Seuil GPU invalide: '+name)
    if free_min_gib+margin_gib>16:raise ValueError('Budget GPU superieur a 16 Gio')
    requirement=int((free_min_gib+margin_gib)*GIB)
    reason=''
    if ia=='desactiver':reason='IA_INTERNE_DESACTIVEE'
    elif external_masks:reason='MASQUES_EXTERNES_PRIORITAIRES'
    elif not snapshot.get('cuda_disponible'):reason='CUDA_INDISPONIBLE'
    elif 'vram_libre_globale_bytes' not in snapshot:reason='MEMOIRE_GPU_INCONNUE'
    elif snapshot['vram_libre_globale_bytes']<requirement:reason='MEMOIRE_GPU_INSUFFISANTE'
    else:reason='SEUIL_LIBRE_RESPECTE'
    unsafe=reason in ('CUDA_INDISPONIBLE','MEMOIRE_GPU_INCONNUE','MEMOIRE_GPU_INSUFFISANTE')
    if unsafe and ia!='desactiver' and not external_masks:
        if policy=='strict' or ia=='forcer':action='ABANDON_EXPLICITE'
        elif policy=='protege':action='SAUTER_IA_GARDER_EXPORTS'
        else:action='TENTER_IA_AVEC_ALERTE'
    else:action='PROCEDER'
    return {'politique':policy,'action':action,'raison':reason,
            'seuil_mem_libre_gio':float(free_min_gib),'marge_securite_gio':float(margin_gib),
            'seuil_total_bytes':requirement,'mem_libre_observee_bytes':snapshot.get('vram_libre_globale_bytes'),
            'ia_demandee':ia,'masques_externes':bool(external_masks),
            'seuil_non_garanti':True,
            'mise_en_garde':'Ce seuil est un filtre preventif, pas la preuve que SAM2/BiRefNet tiendra en VRAM.'}


def compare_snapshots(before,after,start_s,*,model_was_called=False):
    """Wall-clock duration and before/after CUDA memory; not an inference-only peak."""
    seconds=max(0.0,time.perf_counter()-start_s)
    same=(before.get('cuda_disponible') and after.get('cuda_disponible') and
          before.get('index_gpu')==after.get('index_gpu'))
    result={'secondes_totales_ecoulees':round(seconds,4),
            'gpu_avant':before,'gpu_apres':after,
            'gpu_identique_avant_apres':bool(same),
            'appel_modele_interne_signale':bool(model_was_called),
            'inference_gpu_prouvee':False,
            'pic_vram_de_l_inference_mesure':False,
            'limites':['Chronometre la totalite du noeud SmartSVG, pas chaque modele.',
                        'La VRAM libre CUDA provient du pilote pour tout le GPU et peut varier pendant le traitement.',
                        'Les statistiques PyTorch concernent le processus et le pic est historique.',
                        'Une invocation de modele ne prouve pas que ses calculs ont utilise CUDA.',
                        'Un garde-fou de memoire n empeche pas toutes les erreurs OOM.']}
    if same:
        for k in ('vram_libre_globale_bytes','pytorch_alloue_bytes','pytorch_reserve_bytes'):
            if k in before and k in after:
                result['delta_'+k]=after[k]-before[k]
    return result
