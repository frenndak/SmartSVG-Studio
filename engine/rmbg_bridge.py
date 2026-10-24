"""Version-aware bridge to registered ComfyUI-RMBG node.

RMBG is called locally; this module downloads no models and performs no network
requests. Any CUDA/model errors are propagated to the caller for explicit QA.
"""
import numpy as np
import torch

MODEL='INSPYRENET'
PREFERRED={'sensitivity':0.5,'process_res':768,'mask_blur':0,
           'mask_offset':0,'background':'Alpha','invert_output':False,
           'refine_foreground':False,'unload_model':False,
           'optimize':True,'background_color':'#FFFFFF'}

def _param_default(spec, name, required):
    if name in PREFERRED:
        return PREFERRED[name]
    if isinstance(spec, (tuple,list)) and len(spec)>1 and isinstance(spec[1],dict) and 'default' in spec[1]:
        return spec[1]['default']
    if isinstance(spec, (tuple,list)) and spec and isinstance(spec[0],(list,tuple)) and spec[0]:
        return spec[0][0]
    if required:
        raise RuntimeError('RMBG: parametre obligatoire sans valeur par defaut: '+name)
    return None

def invoke_rmbg(owner, img_np, registry=None):
    """Return 2D foreground mask (0..1) and debug metadata; keep backend cached.

    Runtime detection from INPUT_TYPES() supports optional advanced settings of
    ComfyUI-RMBG 3.x; a missing or malformed mask is never silently accepted.
    """
    if registry is None:
        import nodes
        registry=nodes.NODE_CLASS_MAPPINGS
    clazz=registry.get('RMBG') or registry.get('AILab_RMBG')
    if clazz is None:
        options=[v for k,v in registry.items() if k.upper().endswith('RMBG') and getattr(v,'__name__','')=='RMBG']
        clazz=options[0] if options else None
    if clazz is None:
        raise RuntimeError('ComfyUI-RMBG introuvable dans les noeuds enregistres')
    definitions=clazz.INPUT_TYPES()
    required=definitions.get('required',{})
    optional=definitions.get('optional',{})
    model_spec=required.get('model') or optional.get('model')
    choices=model_spec[0] if model_spec else []
    if MODEL not in choices:
        raise RuntimeError('RMBG: modele INSPYRENET absent de la version installee')
    params={}
    for name,spec in {**optional,**required}.items():
        if name in ('image','model'):continue
        value=_param_default(spec,name,name in required)
        if value is not None:params[name]=value
    if 'process_res' in required or 'process_res' in optional:
        assert 'process_res' in params
    arr=np.asarray(img_np)
    if arr.ndim!=3 or arr.shape[2]!=3 or arr.size==0:
        raise ValueError('RMBG attend HxWx3 RGB')
    if arr.dtype!=np.uint8:
        raise ValueError('RMBG attend des octets RGB uint8')
    image=torch.from_numpy(np.ascontiguousarray(arr,dtype=np.float32)/255.).unsqueeze(0)
    if getattr(owner,'_rmbg_backend_class',None) is not clazz:
        owner._rmbg_backend=clazz()
        owner._rmbg_backend_class=clazz
    # Result contract is (IMAGE, MASK). Do not assume the RGB output is a mask.
    result=owner._rmbg_backend.process_image(image,MODEL,**params)
    if not isinstance(result,(tuple,list)) or len(result)<2:
        raise RuntimeError('RMBG: sortie masque absente ou signature modifiee')
    mask=result[1]
    if hasattr(mask,'detach'):mask=mask.detach().cpu().numpy()
    mask=np.asarray(mask)
    while mask.ndim>2 and mask.shape[0]==1:
        mask=mask[0]
    if mask.ndim!=2 or mask.shape!=arr.shape[:2]:
        raise RuntimeError(f'RMBG: dimensions masque incorrectes {mask.shape}, attendu {arr.shape[:2]}')
    if not np.issubdtype(mask.dtype,np.number) or not np.all(np.isfinite(mask)):
        raise RuntimeError('RMBG: valeurs masque non numeriques ou non finies')
    if float(mask.min())<-.001 or float(mask.max())>1.001:
        raise RuntimeError('RMBG: masque hors intervalle 0..1')
    mask=np.clip(mask.astype(np.float32),0,1)
    return mask, {'modele':MODEL,'resolution':params.get('process_res'),
                  'parametres_fournis':sorted(params),'masque_min':round(float(mask.min()),3),
                  'masque_max':round(float(mask.max()),3)}
