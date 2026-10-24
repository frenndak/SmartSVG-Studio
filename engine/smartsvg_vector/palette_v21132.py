"""Deterministic local palette extraction: does not reset NumPy/OpenCV global RNG."""
from __future__ import annotations
import numpy as np


def _dist2(samples, centers):
    # Float32 ranges bounded by 255; rounding tiny negative distances to zero.
    a=(samples*samples).sum(axis=1,keepdims=True)
    b=(centers*centers).sum(axis=1)
    return np.maximum(a+b-2*(samples@centers.T),0.)


def local_kmeans_palette(sample, k, seed=2113, max_iterations=32):
    data=np.asarray(sample,dtype=np.float32)
    if data.ndim!=2 or data.shape[1]!=3 or not 2<=k<=min(16,len(data)):
        raise ValueError('Palette input invalid')
    if not np.isfinite(data).all() or data.min()<0 or data.max()>255:
        raise ValueError('Palette values invalid')
    rng=np.random.default_rng(seed)
    # Deterministic k-means++ with local generator and a stable fallback.
    centers=np.empty((k,3),dtype=np.float32)
    centers[0]=data[int(rng.integers(len(data)))]
    closest=_dist2(data,centers[:1])[:,0]
    for j in range(1,k):
        total=float(closest.sum(dtype=np.float64))
        if total<=0:
            centers[j]=data[int(rng.integers(len(data)))]
        else:
            target=float(rng.random())*total
            idx=int(np.searchsorted(np.cumsum(closest,dtype=np.float64),target,side='left'))
            centers[j]=data[min(idx,len(data)-1)]
        closest=np.minimum(closest,_dist2(data,centers[j:j+1])[:,0])
    for _ in range(max_iterations):
        dist=_dist2(data,centers)
        labels=np.argmin(dist,axis=1)
        updated=centers.copy()
        counts=np.bincount(labels,minlength=k)
        for channel in range(3):
            total=np.bincount(labels,weights=data[:,channel],minlength=k)
            np.divide(total,counts,out=updated[:,channel],where=counts>0)
        for j in np.flatnonzero(counts==0):
            far=int(np.argmax(np.min(dist,axis=1)))
            updated[j]=data[far]
        if float(np.max(np.abs(updated-centers)))<0.2:
            centers=updated
            break
        centers=updated
    return np.uint8(np.rint(np.clip(centers,0,255)))
