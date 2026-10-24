"""V19.7.1 trustworthy optional telemetry for SmartSVG's internal stages.

This profiler does not modify model CUDA peak counters or any production files.
Sync failures, partial GPU sensor failures, and external-node limits are explicit.
"""
from __future__ import annotations
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time
from uuid import uuid4

_CURRENT = ContextVar('smartsvg_v197_profile', default=None)
_FRAMES = ContextVar('smartsvg_v197_stage_frames', default=())


def _cpu_rss():
    """Best-effort resident memory for whole ComfyUI process, not one model."""
    try:
        import psutil
        return int(psutil.Process(os.getpid()).memory_info().rss)
    except (ImportError, OSError, AttributeError):
        return None


def _cuda_state(torch_module=None):
    """Collect independent CUDA fields, retaining those usable if one API fails."""
    try:
        if torch_module is None:
            import torch as torch_module
        if not bool(torch_module.cuda.is_available()):
            return {'available':False,'reason':'CUDA non disponible'}
        device=int(torch_module.cuda.current_device())
    except Exception as exc:
        return {'available':False,'reason':f'{type(exc).__name__}: {str(exc)[:110]}'}
    result={'available':True,'device_index':device}
    failures={}
    getters={
        'device_name':lambda:str(torch_module.cuda.get_device_name(device)),
        'allocated_bytes':lambda:int(torch_module.cuda.memory_allocated(device)),
        'reserved_bytes':lambda:int(torch_module.cuda.memory_reserved(device)),
        'global_peak_allocated_bytes':lambda:int(torch_module.cuda.max_memory_allocated(device)),
        'device_memory_info':lambda:torch_module.cuda.mem_get_info(device),
    }
    for key,func in getters.items():
        try:
            val=func()
            if key=='device_memory_info':
                free,total=val
                if not (0<=int(free)<=int(total)):
                    raise ValueError('valeurs incoherentes pour mem_get_info')
                result['free_device_bytes']=int(free)
                result['total_device_bytes']=int(total)
            else:
                result[key]=val
        except Exception as exc:
            failures[key]=f'{type(exc).__name__}: {str(exc)[:100]}'
    if failures:
        result['mesures_indisponibles']=failures
        result['capture_partielle']=True
    else:
        result['capture_partielle']=False
    return result


def _sync(torch_module=None):
    """Return proof of CUDA synchronization, not an unobservable best effort."""
    try:
        if torch_module is None:
            import torch as torch_module
        if not bool(torch_module.cuda.is_available()):
            return {'tentative':False,'reussie':False,'motif':'CUDA non disponible'}
        torch_module.cuda.synchronize()
        return {'tentative':True,'reussie':True}
    except Exception as exc:
        # Observability must never make a successful production run fail.
        return {'tentative':True,'reussie':False,
                'motif':f'{type(exc).__name__}: {str(exc)[:130]}'}


class RunProfile:
    def __init__(self, enabled=True, torch_module=None):
        self.enabled=bool(enabled)
        self.torch_module=torch_module
        self.events=[]
        self.output_path=None
        self.started_at=datetime.now(timezone.utc).isoformat()
        self.run_start=time.perf_counter()
        self.status='EN_COURS'

    @contextmanager
    def activate(self):
        if not self.enabled:
            yield self
            return
        token=_CURRENT.set(self)
        try:
            yield self
        finally:
            _CURRENT.reset(token)

    @contextmanager
    def stage(self,label):
        if not self.enabled:
            yield
            return
        label=str(label)[:120]
        stack=_FRAMES.get()
        frame={'child_elapsed':0.0}
        stack_token=_FRAMES.set((*stack,frame))
        sync_before=_sync(self.torch_module)
        before=_cuda_state(self.torch_module)
        rss_before=_cpu_rss()
        start=time.perf_counter()
        error=None
        try:
            yield
        except BaseException as exc:
            error=f'{type(exc).__name__}: {str(exc)[:160]}'
            raise
        finally:
            sync_after=_sync(self.torch_module)
            elapsed=max(0.0,time.perf_counter()-start)
            after=_cuda_state(self.torch_module)
            rss_after=_cpu_rss()
            _FRAMES.reset(stack_token)
            if stack:
                stack[-1]['child_elapsed']+=elapsed
            reliable=(sync_before['reussie'] and sync_after['reussie'] and
                      before.get('available') and after.get('available') and
                      before.get('device_index')==after.get('device_index'))
            event={'etape':label,'secondes_ecoulees':round(elapsed,4),
                   'secondes_exclusives_approximatives':round(max(0.0,elapsed-frame['child_elapsed']),4),
                   'statut':'ERREUR' if error else 'OK',
                   'cuda_avant':before,'cuda_apres':after,
                   'synchronisation_cuda_avant':sync_before,
                   'synchronisation_cuda_apres':sync_after,
                   'chronometrage_gpu_synchronise':bool(reliable),
                   'rss_processus_avant_bytes':rss_before,
                   'rss_processus_apres_bytes':rss_after}
            if error:event['erreur']=error
            if before.get('available') and after.get('available') and all(
                'allocated_bytes' in x for x in (before,after)):
                event['variation_allocation_cuda_bytes']=after['allocated_bytes']-before['allocated_bytes']
            if rss_before is not None and rss_after is not None:
                event['variation_rss_processus_bytes']=rss_after-rss_before
            self.events.append(event)

    def report(self):
        elapsed=round(max(0.0,time.perf_counter()-self.run_start),4)
        stage_times={};exclusive_times={}
        for event in self.events:
            key=event['etape']
            if key!='SmartSVG / traitement complet':
                stage_times[key]=round(stage_times.get(key,0.0)+event['secondes_ecoulees'],4)
                exclusive_times[key]=round(exclusive_times.get(key,0.0)+event['secondes_exclusives_approximatives'],4)
        failures=[{'etape':e['etape'],'erreur':e.get('erreur')} for e in self.events if e['statut']=='ERREUR']
        sync_failures=[e['etape'] for e in self.events if any(
            x['tentative'] and not x['reussie'] for x in
            (e['synchronisation_cuda_avant'],e['synchronisation_cuda_apres']))]
        partial_sensors=[e['etape'] for e in self.events if any(
            x.get('capture_partielle',False) for x in (e['cuda_avant'],e['cuda_apres']))]
        return {'version':'19.7.1-beta','statut':self.status,'echec':getattr(self,'failure',None),
                'erreurs_partielles':failures,'nombre_erreurs_partielles':len(failures),
                'date_debut_utc':self.started_at,'secondes_totales':elapsed,
                'durees_etapes_s':stage_times,
                'durees_exclusives_approximatives_s':exclusive_times,
                'etapes':self.events,'sortie_production':self.output_path,
                'mesure_gpu_reelle_observee':any(x['cuda_apres'].get('available') for x in self.events),
                'synchronisation_cuda_echouee_etapes':sync_failures,
                'captures_gpu_partielles_etapes':partial_sensors,
                'preuve_inference_GPU_modele_specifique':False,
                'etapes_modele_interne_appelees':[x['etape'] for x in self.events
                    if x['etape'].startswith(('SAM2 /','Florence-2 /','RMBG /'))],
                'limites':[
                    'Les secondes_ecoulees sont murales; synchronisation CUDA parfois indisponible: verifier chronometrage_gpu_synchronise.',
                    'Les durees exclusives sont APPROXIMATIVES et excluent les horloges enfant, pas tous les couts de mesure.',
                    'CUDA PyTorch et RSS concernent tout le processus ComfyUI, possiblement partage avec d autres noeuds.',
                    'global_peak_allocated_bytes : PAS le pic isolé de l etape ; pic historique de l allocateur PyTorch.',
                    'Variation de memoire allouee != pic de VRAM reel ; les allocations externes peuvent etre absentes.',
                    'Des donnees GPU partielles ne prouvent pas une inference du modele sur CUDA.',
                    'Les etapes imbriquees se chevauchent et ne doivent pas etre additionnees au total.',
                    'Les noeuds externes deja executes ne sont pas profiles retroactivement.',
                    'Les synchronisations peuvent ralentir l execution profilee.',
                ]}

    def annotate_stage(self,label,*,mask_count=None,notes=None):
        if not self.enabled:return
        for ev in reversed(self.events):
            if ev['etape']==label:
                if mask_count is not None:
                    n=int(mask_count)
                    if n>=0:
                        ev['masques_acceptes']=n
                        if n>0:
                            ev['secondes_amorties_par_masque']=round(ev['secondes_ecoulees']/n,4)
                            ev['note_cout']='Moyenne amortie par masque, non cout par objet.'
                if notes:ev['notes']=str(notes)[:170]
                break


def active_profiler():
    return _CURRENT.get()


@contextmanager
def track_stage(label):
    p=active_profiler()
    if p is None:
        yield
    else:
        with p.stage(label):
            yield


def record_output_path(path):
    p=active_profiler()
    if p is not None:p.output_path=str(path)


def save_profile(profile:RunProfile, output_root):
    """Atomic sidecar diagnostic: a failed save never edits the production output."""
    root=Path(output_root).expanduser()
    root.mkdir(parents=True,exist_ok=True)
    if not root.is_dir():raise ValueError('Destination diagnostic non accessible')
    # Retain historic naming pattern for existing consumers/workflows.
    path=root/('PERFORMANCES_V19_7_'+uuid4().hex+'.json')
    temp=root/('.'+path.stem+'.'+uuid4().hex+'.tmp')
    try:
        temp.write_text(json.dumps(profile.report(),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
        os.replace(temp,path)
    finally:
        temp.unlink(missing_ok=True)
    return path


def annotate_stage(label,**kwargs):
    p=active_profiler()
    if p is not None:p.annotate_stage(label,**kwargs)
