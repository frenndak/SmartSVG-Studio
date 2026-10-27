"""G2.4 opt-in ComfyUI mask vault node, using original IMAGE/MASK tensors.

No masks are reconstructed from downsampled previews. Write requires an
explicit project revision to prevent accidental overwrites of edited data.
"""
from __future__ import annotations

from io import BytesIO
import json
import os

import numpy as np
import torch
from PIL import Image

from .smartsvg_core.project_workspace_g22 import ManagedWorkspace, WorkspaceError
from .smartsvg_editor.strokes import (
    edit_fingerprint, source_fingerprint, MAX_INSTANCES,
    MAX_PIXELS, MAX_TOTAL_MASK_PIXELS, StrokeError,
)


class MaskVaultError(ValueError):
    pass


def _workspace():
    if os.environ.get('SMARTSVG_ENABLE_PROJECT_API')!='1':
        raise MaskVaultError('Masques G2.4 : activer explicitement le mode projets sur ComfyUI local')
    try:
        import folder_paths
        return ManagedWorkspace(folder_paths.get_output_directory())
    except (ImportError,AttributeError,OSError,WorkspaceError) as exc:
        raise MaskVaultError('Masques G2.4 : espace de projets indisponible') from exc


def _image(image):
    if (not isinstance(image,torch.Tensor) or image.ndim!=4 or
        image.shape[0]!=1 or image.shape[-1] not in (3,4)):
        raise MaskVaultError('Masques G2.4 : IMAGE [1,H,W,RGB/RGBA] requise')
    h,w=int(image.shape[1]),int(image.shape[2])
    if h<1 or w<1 or h*w>MAX_PIXELS:
        raise MaskVaultError('Masques G2.4 : image source trop grande (5 Mp)')
    rgb=np.ascontiguousarray(image[0].detach().float().cpu().numpy())
    fingerprint=source_fingerprint(rgb)
    return rgb,fingerprint


def _mask_array(input_mask,rgb):
    h,w=rgb.shape[:2]
    if input_mask is None:
        base=np.zeros((1,h,w),dtype=np.float32)
    else:
        if not isinstance(input_mask,torch.Tensor) or input_mask.ndim!=3:
            raise MaskVaultError('Masques G2.4 : MASK [N,H,W] attendu')
        if (tuple(input_mask.shape[1:])!=(h,w) or
            not 1<=input_mask.shape[0]<=MAX_INSTANCES or
            input_mask.numel()>MAX_TOTAL_MASK_PIXELS):
            raise MaskVaultError('Masques G2.4 : dimensions ou nombre de masques non compatibles')
        base=np.ascontiguousarray(input_mask.detach().to(
            device='cpu',dtype=torch.float32).numpy(),dtype=np.float32)
    if base.size>8_000_000:
        raise MaskVaultError('Masques G2.4 : limite de 8 millions de pixels de masques')
    if not np.isfinite(base).all() or base.min()<-.001 or base.max()>1.001:
        raise MaskVaultError('Masques G2.4 : masque non fini ou hors plage')
    return base


def _same_png_source(workspace,project_name,rgb):
    """Compare exact quantized pixel channels with the chosen project's PNG."""
    try:
        raw=workspace.source_png(project_name)
        with Image.open(BytesIO(raw)) as im:
            mode='RGBA' if rgb.shape[-1]==4 else 'RGB'
            data=np.ascontiguousarray(np.asarray(im.convert(mode)))
    except (OSError,ValueError,WorkspaceError) as exc:
        raise MaskVaultError('Masques G2.4 : PNG original du projet illisible') from exc
    pixels=np.ascontiguousarray(np.rint(np.clip(rgb,0,1)*255).astype(np.uint8))
    if data.shape!=pixels.shape or not np.array_equal(data,pixels):
        raise MaskVaultError(
            'Masques G2.4 : IMAGE différente du PNG original enregistré ; refuser la capture')


class SmartSVGProjectMaskVaultG24:
    """Deliberately opt-in pass-through for deterministic mask capture/replay."""
    CATEGORY='SmartSVG / 02 PROJETS'
    RETURN_TYPES=('MASK','IMAGE','STRING')
    RETURN_NAMES=('masques_base','image_source','diagnostic_masques')
    FUNCTION='run'
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'image':('IMAGE',),
            'nom_projet':('STRING',{'default':'mon_projet'}),
            'operation':(['Capturer les masques','Restaurer les masques'],),
            'empreinte_revision':('STRING',{'default':'','tooltip':
                'Coller le SHA-256 du projet affiché par SmartSVG Express. Une révision modifiée est refusée.'}),
        },'optional':{
            'masques_base':('MASK',),
        }}

    def run(self,image,nom_projet,operation,empreinte_revision,masques_base=None):
        rgb,img_sha=_image(image)
        workspace=_workspace()
        if operation=='Capturer les masques':
            base=_mask_array(masques_base,rgb)
            _same_png_source(workspace,nom_projet,rgb)
            source_sha=edit_fingerprint(rgb,base)
            raw=base.astype('<f4',copy=False).tobytes(order='C')
            result=workspace.save_base_masks(
                nom_projet,raw_float32=raw,shape=base.shape,
                image_fingerprint=img_sha,editor_fingerprint=source_sha,
                expected_sha256=empreinte_revision)
            out=torch.from_numpy(base.copy()).to(device=image.device,dtype=torch.float32)
            msg='Masques de base conservés en float32 sans perte.'
        elif operation=='Restaurer les masques':
            raw,meta=workspace.base_masks(nom_projet,expected_sha256=empreinte_revision)
            if img_sha!=meta['image_fingerprint']:
                raise MaskVaultError(
                    'Masques G2.4 : empreinte IMAGE différente de celle du snapshot')
            shape=meta['shape']
            if (tuple(shape[1:])!=tuple(rgb.shape[:2])):
                raise MaskVaultError('Masques G2.4 : dimensions source incompatibles')
            base=np.frombuffer(raw,dtype='<f4').reshape(tuple(shape)).copy()
            if edit_fingerprint(rgb,base)!=meta['editor_fingerprint']:
                raise MaskVaultError('Masques G2.4 : empreinte image + masques incompatible')
            out=torch.from_numpy(base).to(device=image.device,dtype=torch.float32)
            result={'count':shape[0],'base_masks_exact':True,
                    'certified':False}
            msg='Masques float32 relus à l’identique. Relancer l’éditeur V21.6 pour les retouches.'
        else:
            raise MaskVaultError('Masques G2.4 : opération inconnue')
        report={'version':'g2.4','operation':operation,'masques':int(out.shape[0]),
                'certification_cricut':False,'details':msg}
        if isinstance(result,dict) and 'sha256' in result:
            report['nouvelle_empreinte_revision']=result['sha256']
        return out,image,json.dumps(report,ensure_ascii=False)


NODE_CLASS_MAPPINGS={
    'SmartSVGProjectMaskVaultG24':SmartSVGProjectMaskVaultG24
}
NODE_DISPLAY_NAME_MAPPINGS={
    'SmartSVGProjectMaskVaultG24':'02 · SmartSVG G2.4 — capturer / restaurer masques exacts'
}
