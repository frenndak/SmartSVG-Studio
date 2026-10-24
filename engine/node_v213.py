"""V21.3 per-instance guide; 5-control Express V21.2 preserved unchanged."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import torch
from .node_v212 import (SmartSVGExpressV212, NODE_CLASS_MAPPINGS as OLD,
                        NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES)
from .instances_v213 import segment_instances, render_preview, PROFILE_PROMPTS, InstanceError

class SmartSVGExpressV213(SmartSVGExpressV212):
    CATEGORY='SmartSVG / Cricut / V21.3'

class SmartSVGInstancesV213:
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
    FUNCTION='run';CATEGORY='SmartSVG / Cricut / V21.3'
    def run(self,image,profil='Trois renards',source_boites='Florence-2',
            boites_json='[]',max_objets=6):
        if not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1 or image.shape[-1] not in (3,4):
            raise InstanceError('IMAGE attendue : [1,H,W,RGB/RGBA]')
        if image.shape[1]*image.shape[2]>5_000_000:raise InstanceError('Image >5 Mp')
        data=image[0,:,:,:3].detach().float().cpu().numpy()
        if not np.isfinite(data).all() or data.min()<-.001 or data.max()>1.001:
            raise InstanceError('Valeurs image invalides')
        rgb=np.uint8(np.clip(np.round(data*255),0,255))
        # Live GPU guard: only used in the actual ComfyUI inference node.
        from .gpu_budget_v203 import gpu_snapshot, policy_decision
        snapshot=gpu_snapshot()
        decision=policy_decision(snapshot,policy='strict',ia='forcer')
        if decision['action']!='PROCEDER':
            raise InstanceError('Segmentation locale impossible: '+decision['raison']+' (seuil configurable dans le module expert)')
        batch,report=segment_instances(rgb,profile=profil,source=source_boites,
                                       boxes_json=boites_json,max_objects=max_objets)
        report['controle_gpu_avant_inference']=decision
        preview=render_preview(rgb,batch,report)
        pv=torch.from_numpy(np.ascontiguousarray(np.asarray(preview,np.float32)/255))[None]
        return (torch.from_numpy(np.ascontiguousarray(batch)),pv,
                json.dumps(report,ensure_ascii=False,indent=2))

NODE_CLASS_MAPPINGS={**OLD,'SmartSVGExpressV213':SmartSVGExpressV213,
                     'SmartSVGInstancesV213':SmartSVGInstancesV213}
NODE_DISPLAY_NAME_MAPPINGS={**OLD_NAMES,
    'SmartSVGExpressV213':'SmartSVG V21.3 - EXPRESS (5 choix / masques externes)',
    'SmartSVGInstancesV213':'SmartSVG V21.3 - Segmenter sujets distincts (Florence-2 + SAM2)'}
