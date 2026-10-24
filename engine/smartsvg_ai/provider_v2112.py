"""V21.12: fail-closed ComfyUI-RMBG model adapter.

Supports the verified public RMBG 3.3.0 node signatures. No model is bundled.
The registered provider may download weights on first execution. Presence and
signature are not inference or real-world cut-quality certification.
"""
from __future__ import annotations
import gc
import numpy as np
import torch
from .auto_masks_v2111 import _accept

class ProviderUnavailable(RuntimeError):
    pass

# Only known, explicitly reviewed node IDs are ever invoked.
CANDIDATES = (
    ('BiRefNetRMBG', 'model', ('BiRefNet_lite', 'BiRefNet-general')),
    ('RMBG', 'model', ('RMBG-2.0',)),
    ('SAM2Segment', 'sam2_model', ('sam2.1_hiera_tiny',)),
)
DINO = 'GroundingDINO_SwinT_OGC (694MB)'
PROMPTS = ('person', 'cartoon character', 'toy')

def _choice(spec):
    if not isinstance(spec,(tuple,list)) or not spec:return ()
    items=spec[0]
    return tuple(items) if isinstance(items,(tuple,list)) else ()

def available(registry=None):
    """Read only contracts: NEVER load weights or download models."""
    if registry is None:
        try:
            import nodes
            registry=nodes.NODE_CLASS_MAPPINGS
        except (ImportError,AttributeError):
            registry={}
    found=[]
    for name,model_key,models in CANDIDATES:
        cls=registry.get(name)
        if cls is None:
            found.append({'noeud':name,'statut':'ABSENT'});continue
        try:
            spec=cls.INPUT_TYPES()
            required=spec['required']
            optional=spec.get('optional',{})
            all_inputs={**required,**optional}
            fn=getattr(cls,'FUNCTION',None)
            assert all(x in required for x in ('image',model_key))
            assert name!='SAM2Segment' or all(x in required for x in ('prompt','dino_model','device'))
            assert callable(getattr(cls,fn,None))
            assert len(getattr(cls,'RETURN_TYPES',()))>=2 and cls.RETURN_TYPES[1]=='MASK'
            chosen=next((model for model in models if model in _choice(required[model_key])),None)
            assert chosen is not None
            if name=='SAM2Segment':
                assert DINO in _choice(required['dino_model'])
                assert 'Auto' in _choice(required['device'])
            found.append({'noeud':name,'statut':'CONTRAT_COMPATIBLE_NON_EXECUTE',
                          'modele':chosen,'function':fn,
                          'parametres_optionnels':sorted(optional)})
        except (AssertionError,KeyError,TypeError,AttributeError,ValueError) as e:
            found.append({'noeud':name,'statut':'INCOMPATIBLE',
                          'details':f'{type(e).__name__}: {str(e)[:130]}'})
    return found

def _mask_from_output(out,hw):
    if isinstance(out,dict):out=out.get('result')
    if not isinstance(out,(tuple,list)) or len(out)<2:
        raise ProviderUnavailable('Sortie MASK manquante')
    value=out[1]
    if hasattr(value,'detach'):value=value.detach().float().cpu().numpy()
    arr=np.asarray(value)
    if arr.ndim==4 and arr.shape[0]==1 and arr.shape[-1]==1:arr=arr[0,:,:,0]
    if arr.ndim==3 and arr.shape[0]==1:arr=arr[0]
    if arr.ndim==2:arr=arr[None]
    if arr.ndim!=3 or arr.shape[1:]!=hw or not (1<=arr.shape[0]<=12):
        raise ProviderUnavailable('Masque hors dimensions ou lot ambigu')
    if arr.dtype.kind not in 'biuf' or not np.isfinite(arr).all() or arr.min()<-.001 or arr.max()>1.001:
        raise ProviderUnavailable('Masque invalide ou valeurs hors [0,1]')
    return np.ascontiguousarray(arr.astype('float32').clip(0,1))

def _kwargs(info, image, name, cls):
    inp=cls.INPUT_TYPES()
    required=inp['required']; optional=inp.get('optional',{})
    chosen=info['modele']
    args={'image':image}
    if name=='SAM2Segment':
        args.update(sam2_model=chosen,dino_model=DINO,device='Auto')
    else:args['model']=chosen
    # Limit numerical work on 8GB cards without making unsupported API assumptions.
    defaults={'unload_model':True, 'background':'Alpha','mask_blur':0,
              'mask_offset':0,'invert_output':False,'refine_foreground':False,
              'sensitivity':1.0,'process_res':768,'threshold':0.38,
              'background_color':'#FFFFFF'}
    for key,value in defaults.items():
        if key in optional:args[key]=value
    return args

def segment_adaptive(rgb, *,registry=None,max_results=12):
    """Attempt supported local AI backends; return only pre-screened candidate masks.

    A mask is a PROPOSAL, not evidence that the right object was understood.
    Fail closed on absent plugins, incompatible signatures, bad shapes and OOM.
    """
    a=np.asarray(rgb)
    if a.ndim!=3 or a.shape[2]!=3 or a.dtype!=np.uint8:raise ValueError('RGB uint8 attendu')
    h,w=a.shape[:2]
    if not h or not w or h*w>5_000_000:raise ValueError('Taille source > 5 MP')
    if registry is None:
        try:
            import nodes
            registry=nodes.NODE_CLASS_MAPPINGS
        except (ImportError,AttributeError):
            registry={}
    supported=available(registry)
    issues=[];attempted=0
    if not any(x['statut']=='CONTRAT_COMPATIBLE_NON_EXECUTE' for x in supported):
        raise ProviderUnavailable('RMBG: aucun fournisseur reconnu compatible; installer/mettre à jour ComfyUI-RMBG')
    image=torch.from_numpy(np.ascontiguousarray(a).astype('float32')/255.0).unsqueeze(0)
    try:
        for info in supported:
            if info['statut']!='CONTRAT_COMPATIBLE_NON_EXECUTE':continue
            name=info['noeud'];cls=registry[name]
            prompts=PROMPTS if name=='SAM2Segment' else (None,)
            backend=None
            try:
                backend=cls()
                fn=getattr(backend,info['function'])
                for prompt in prompts:
                    kw=_kwargs(info,image,name,cls)
                    if prompt is not None:kw['prompt']=prompt
                    attempted+=1
                    try:
                        result=fn(**kw)
                        array=_mask_from_output(result,(h,w))
                        # The 21.11 safety checks are mandatory even for real model results.
                        checked,flags=_accept(array,pixel_count=h*w,expected_hw=(h,w),source='IA')
                        if checked is None:
                            issues.append({'provider':name,'prompt':prompt,'erreur':','.join(flags)[:170]})
                            continue
                        if checked.shape[0]>max_results:checked=checked[:max_results]
                        return {'masks':checked,'audit':{
                            'provider':name,'model':info['modele'],'prompt':prompt,
                            'inference_effectuee':True,'tentatives':attempted,
                            'certification_semantique':False,'decoupe_cricut_testee':False,
                            'avertissements':flags,'autres_tentatives':issues[-8:]}}
                    except (KeyboardInterrupt,SystemExit):raise
                    except Exception as exc:
                        if isinstance(exc,(torch.cuda.OutOfMemoryError,MemoryError)) or 'out of memory' in str(exc).lower():
                            raise ProviderUnavailable('VRAM insuffisante pour cette inférence : réduire image ou libérer GPU') from exc
                        issues.append({'provider':name,'prompt':prompt,
                                       'erreur':f'{type(exc).__name__}: {str(exc)[:120]}'})
            except (KeyboardInterrupt,SystemExit):raise
            except ProviderUnavailable:raise
            except Exception as exc:
                issues.append({'provider':name,'erreur':f'{type(exc).__name__}: {str(exc)[:120]}'})
            finally:
                backend=None
                gc.collect()
                if torch.cuda.is_available():torch.cuda.empty_cache()
    finally:
        del image
    raise ProviderUnavailable('Aucun masque acceptable. Essais : '+str(issues[-6:])[:550])
