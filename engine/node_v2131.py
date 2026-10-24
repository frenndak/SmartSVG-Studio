"""SmartSVG V21.3.1 - audited instance extraction and backwards-compatible Express."""
from __future__ import annotations
import json
import numpy as np
import torch
from .node_v213 import SmartSVGExpressV213, NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .instances_v2131 import segment_instances, render_preview, PROFILE_PROMPTS, InstanceError
from .gpu_budget_v203 import gpu_snapshot, policy_decision

class SmartSVGExpressV2131(SmartSVGExpressV213):
    CATEGORY='SmartSVG / Cricut / V21.3.1'

class SmartSVGInstancesV2131:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'image':('IMAGE',),
            'profil':(list(PROFILE_PROMPTS),{'default':'Trois renards'}),
            'source_boites':(['Florence-2','Boîtes manuelles'],{'default':'Florence-2'}),
            'boites_json':('STRING',{'default':'[]','multiline':True}),
            'max_objets':('INT',{'default':6,'min':1,'max':12}),
        }}
    RETURN_TYPES=('MASK','IMAGE','STRING')
    RETURN_NAMES=('masques_individuels','apercu_guidage','diagnostic_instances')
    FUNCTION='run';CATEGORY='SmartSVG / Cricut / V21.3.1'
    def run(self,image,profil='Trois renards',source_boites='Florence-2',
            boites_json='[]',max_objets=6):
        if not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1 or image.shape[-1] not in (3,4):
            raise InstanceError('IMAGE attendue : [1,H,W,RGB/RGBA]')
        if image.shape[1]*image.shape[2]>5_000_000:
            raise InstanceError('Image >5 Mp : réduire avant IA')
        data=image[0,:,:,:3].detach().float().cpu().numpy()
        if not np.isfinite(data).all() or data.min()<-.001 or data.max()>1.001:
            raise InstanceError('Valeurs image invalides')
        rgb=np.uint8(np.clip(np.round(data*255),0,255))
        snapshot=gpu_snapshot()
        decision=policy_decision(snapshot,policy='strict',ia='forcer')
        if decision['action']!='PROCEDER':
            raise InstanceError('Segmentation locale impossible: '+decision['raison']+' (contrôle GPU préventif, pas garantie de mémoire)')
        batch,report=segment_instances(rgb,profile=profil,source=source_boites,
                                       boxes_json=boites_json,max_objects=max_objets)
        report['controle_gpu_avant_inference']=decision
        preview=render_preview(rgb,batch,report)
        pv=torch.from_numpy(np.ascontiguousarray(np.asarray(preview,np.float32)/255))[None]
        return (torch.from_numpy(np.ascontiguousarray(batch)),pv,
                json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False))

NODE_CLASS_MAPPINGS={**OLD,'SmartSVGExpressV2131':SmartSVGExpressV2131,
                     'SmartSVGInstancesV2131':SmartSVGInstancesV2131}
NODE_DISPLAY_NAME_MAPPINGS={**OLD_NAMES,
    'SmartSVGExpressV2131':'SmartSVG V21.3.1 - EXPRESS (5 choix)',
    'SmartSVGInstancesV2131':'SmartSVG V21.3.1 - Sujets distincts (contrôles renforcés)'}
