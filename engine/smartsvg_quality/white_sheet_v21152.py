"""Conservative CPU-only foreground candidates for *regular white sticker sheets*.

Deliberately not a general-purpose person / photograph segmenter. Each tile must
independently satisfy foreground/background and geometry checks; otherwise abstain
instead of exporting a misleading rectangular silhouette. Does not run IA.
"""
from __future__ import annotations
from dataclasses import dataclass
import cv2
import numpy as np

MAX_SOURCE_PIXELS = 20_000_000

class SheetUncertain(ValueError):
    """The sheet cannot safely be auto-isolated into per-subject silhouettes."""

@dataclass(frozen=True)
class WhiteSheetResult:
    masks: np.ndarray
    diagnostics: tuple[dict, ...]
    algorithm: str = 'white-grid-cc-1'


def segment_white_grid(pixels:np.ndarray, *, cols:int=4, rows:int=3,
                       white_threshold:int=227) -> WhiteSheetResult:
    """Find *one dominant contiguous candidate* in each regular grid cell.

    Requires whitespace around objects and rejects a full-cell/rectangular
    foreground. All masks are binary foreground=1 and equal source H×W.
    Only supported on grids of 12/24 with maximum 20M pixels.
    """
    if not isinstance(pixels,np.ndarray) or pixels.dtype!=np.uint8 or pixels.ndim!=3 or pixels.shape[2] not in (3,4):
        raise SheetUncertain('Image RGB/RGBA uint8 attendue')
    if (cols, rows) not in ((4,3),(6,4)):
        raise SheetUncertain('Grille non prise en charge par le detourage fond blanc')
    h,w=pixels.shape[:2]
    if h*w>MAX_SOURCE_PIXELS or min(w//cols,h//rows)<55:
        raise SheetUncertain('Dimensions insuffisantes ou image trop grande')
    if pixels.shape[2]==4 and np.min(pixels[:,:,3])<250:
        raise SheetUncertain('Image deja transparente : conserver le pipeline alpha existant')
    masks=np.zeros((cols*rows,h,w),dtype=np.uint8)
    diagnostics=[]
    for r in range(rows):
        for c in range(cols):
            x0=round(w*c/cols);x1=round(w*(c+1)/cols)
            y0=round(h*r/rows);y1=round(h*(r+1)/rows)
            tile=pixels[y0:y1,x0:x1,:3]
            th,tw=tile.shape[:2]
            nearwhite=np.all(tile>235,axis=2)
            white_share=float(nearwhite.mean())
            # Corner regions must be mostly light. This explicitly excludes
            # dark-backed sheets and photographic/patterned tile backgrounds.
            hh=max(5,round(th*.10));ww=max(5,round(tw*.10))
            corners=[tile[:hh,:ww],tile[:hh,-ww:],tile[-hh:,:ww],tile[-hh:,-ww:]]
            corner_white=min(float(np.mean(np.all(region>232,axis=2))) for region in corners)
            if not (.17<=white_share<=.85) or corner_white<.61:
                raise SheetUncertain(f'Case {r+1}/{c+1} : fond blanc non fiable')
            # Dark ink and coloured print are nonwhite. A flat-white cell with
            # black dashed borders has no sufficiently large subject component.
            foreground=np.uint8(np.min(tile,axis=2)<white_threshold)
            n,labels,stats,_=cv2.connectedComponentsWithStats(foreground,8)
            components=sorted(range(1,n),key=lambda i:int(stats[i,cv2.CC_STAT_AREA]),reverse=True)
            if not components:
                raise SheetUncertain(f'Case {r+1}/{c+1} : sujet absent')
            main=components[0];area=int(stats[main,cv2.CC_STAT_AREA]);total=int(foreground.sum())
            x,y,bw,bh=map(int,stats[main,:4])
            dominance=area/max(total,1)
            if not (.035<=area/(tw*th)<=.76 and dominance>=.78):
                raise SheetUncertain(f'Case {r+1}/{c+1} : sujet ambigu ou parasite')
            if x<max(2,round(tw*.014)) or y<max(2,round(th*.014)) or x+bw>tw-max(2,round(tw*.014)) or y+bh>th-max(2,round(th*.014)):
                raise SheetUncertain(f'Case {r+1}/{c+1} : sujet touche le bord')
            body=np.uint8(labels==main)*255
            # The area inside the exterior silhouette must be filled for a
            # single cut outline. Keep full RGB source untouched elsewhere.
            contours,_=cv2.findContours(body,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            if len(contours)!=1:
                raise SheetUncertain(f'Case {r+1}/{c+1} : contour multiple')
            main_contour=contours[0]
            perimeter=cv2.arcLength(main_contour,True)
            rect_ratio=float(cv2.contourArea(main_contour)/max(1,bw*bh))
            vertices=len(cv2.approxPolyDP(main_contour,max(1,perimeter*.025),True))
            if rect_ratio>=.94 and vertices<=5:
                raise SheetUncertain(f'Case {r+1}/{c+1} : contour rectangulaire, pas un sujet')
            cv2.drawContours(body,contours,-1,255,cv2.FILLED)
            idx=r*cols+c
            masks[idx,y0:y1,x0:x1]=(body>0).astype(np.uint8)
            diagnostics.append({'cellule':[r+1,c+1], 'bbox_source':[x0+x,y0+y,x0+x+bw,y0+y+bh],
                'fraction_blanche':round(white_share,4),'blanc_aux_coins_min':round(corner_white,4),
                'dominance_composante':round(dominance,4),
                'fraction_sujet':round(float(np.mean(body>0)),4),
                'contour_rectangle_ratio':round(rect_ratio,4),
                'nombre_sujets_acceptes':1,
                'verification_humaine_requise':True})
    return WhiteSheetResult(masks=masks,diagnostics=tuple(diagnostics))
