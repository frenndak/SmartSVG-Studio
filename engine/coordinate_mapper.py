"""Explicit image-space contract for object segmentation masks.

Coordinates are pixel-corner coordinates; transforms map source -> destination.
No automatic guessing of resize, crop, composition, or sticker order.
"""
from __future__ import annotations
from dataclasses import dataclass
import json
import cv2
import numpy as np

@dataclass(frozen=True)
class CoordinateMapper:
    matrix: np.ndarray
    source_shape: tuple[int,int]
    target_shape: tuple[int,int]

    def __post_init__(self):
        m=np.asarray(self.matrix,dtype=np.float64)
        if m.shape!=(3,3) or not np.isfinite(m).all() or abs(np.linalg.det(m))<1e-9:
            raise ValueError('Matrice 3x3 non inversible/finie')
        if not np.allclose(m[2,:],(0,0,1),atol=1e-9):
            raise ValueError('Les perspectives ne sont pas prises en charge (affine uniquement)')
        if len(self.source_shape)!=2 or len(self.target_shape)!=2 or min(*self.source_shape,*self.target_shape)<1:
            raise ValueError('Dimensions source ou sortie invalides')
        object.__setattr__(self,'matrix',m)

    @classmethod
    def from_json(cls,text,source_shape,target_shape):
        try:
            obj=json.loads(text)
            matrix=obj.get('source_vers_planche') if isinstance(obj,dict) else obj
            return cls(np.asarray(matrix,dtype=np.float64),tuple(source_shape),tuple(target_shape))
        except (TypeError,KeyError,ValueError) as exc:
            raise ValueError('Transformation attendue: JSON matrice 3x3 source_vers_planche') from exc

    def inverse(self):
        return CoordinateMapper(np.linalg.inv(self.matrix),self.target_shape,self.source_shape)

    def map_points(self,points):
        a=np.asarray(points,dtype=np.float64)
        if a.shape[-1]!=2:raise ValueError('Points attendus Nx2')
        homo=np.concatenate([a.reshape(-1,2),np.ones((a.size//2,1))],axis=1)
        out=(self.matrix@homo.T).T[:,:2]
        return out.reshape(a.shape)

    def map_bbox(self,bbox):
        x,y,w,h=map(float,bbox)
        if min(w,h)<0:raise ValueError('bbox negative')
        pts=self.map_points(np.array([[x,y],[x+w,y],[x+w,y+h],[x,y+h]]))
        l,t=pts.min(axis=0);r,b=pts.max(axis=0)
        return [float(l),float(t),float(r-l),float(b-t)]

    def warp_masks(self,masks):
        batch=np.asarray(masks)
        if batch.ndim==2:batch=batch[None]
        if batch.ndim!=3 or batch.shape[1:]!=self.source_shape:
            raise ValueError(f'Masques: attendus [N,{self.source_shape[0]},{self.source_shape[1]}], reçu {batch.shape}')
        if not 1<=batch.shape[0]<=16 or batch.size>25_000_000 or not np.issubdtype(batch.dtype,np.number) or not np.isfinite(batch).all():
            raise ValueError('Masques invalides ou trop grands')
        if batch.min() < -0.001 or batch.max() > 1.001:raise ValueError('Masques hors de [0,1]')
        h,w=self.target_shape
        return np.stack([cv2.warpAffine(mask.astype(np.float32),self.matrix[:2],(w,h),flags=cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=0) for mask in batch])


def resolve_masks(masks,source_shape,target_shape,space='planche',transform_json=''):
    """Returns (array, diagnostics). Rejects any unregistered source->sheet mapping."""
    if masks is None:return None,{'statut':'non_fournis','repere':space}
    if space not in ('planche','source'):
        raise ValueError('Repere de masques non reconnu')
    arr=np.asarray(masks)
    if arr.ndim==2:arr=arr[None]
    if space=='planche':
        if transform_json.strip():raise ValueError('Ne pas fournir de matrice en mode planche')
        if arr.ndim!=3 or tuple(arr.shape[1:])!=tuple(target_shape):
            raise ValueError('Masques planche non alignés, fournir repère source et transformation explicite')
        return arr,{'statut':'alignement_explicite_planche','repere':space}
    if transform_json.strip():
        mapper=CoordinateMapper.from_json(transform_json,source_shape,target_shape)
    else:
        raise ValueError('Masques source : matrice source_vers_planche explicite obligatoire, meme si les dimensions coincident (recomposition potentielle)')
    out=mapper.warp_masks(arr)
    return out,{'statut':'reprojection_source_vers_planche','repere':space,
                'matrice':mapper.matrix.tolist(),'source_shape':list(source_shape),'planche_shape':list(target_shape)}
