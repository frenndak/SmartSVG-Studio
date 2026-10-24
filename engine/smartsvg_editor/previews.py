"""Publish bounded preview images using ComfyUI's own authenticated /view.

Never expose source file paths or raw SVG/XML in frontend responses.
ComfyUI output files remain accessible to clients authorized on the server.
"""
from __future__ import annotations
from pathlib import Path
from uuid import uuid4
from time import time
import re
import numpy as np
from PIL import Image

FOLDER='SmartSVG_Studio_Editor'
MAX_OWNED=96
MAX_AGE=72*3600
FILENAME=re.compile(r'ed_[a-f0-9]{24}_(?:image|mask\d{2})\.png\Z')


def _cleanup(directory, retain):
    try:
        owned=sorted((p for p in directory.iterdir() if p.is_file() and not p.is_symlink() and FILENAME.fullmatch(p.name)),
                     key=lambda p:p.stat().st_mtime,reverse=True)
        now=time()
        for pos,p in enumerate(owned):
            if p.name not in retain and (pos >= MAX_OWNED or now-p.stat().st_mtime>MAX_AGE):
                p.unlink(missing_ok=True)
    except OSError:
        pass


def publish(rgb, masks, output_directory, *, max_side=760):
    if not output_directory or Path(output_directory).is_symlink():return None
    root=Path(output_directory).resolve()
    if not root.is_dir():return None  # ComfyUI creates its own output directory
    folder=root/FOLDER
    if folder.is_symlink():return None
    try:
        folder.mkdir(exist_ok=True)
        if not folder.resolve().is_relative_to(root):return None
        _cleanup(folder,set())
        h,w=rgb.shape[:2]
        scale=min(1.0,max_side/max(w,h))
        pw=max(1,round(w*scale));ph=max(1,round(h*scale))
        token=uuid4().hex[:24]
        names=[]
        arr=np.rint(np.clip(rgb[:,:,:3],0,1)*255).astype(np.uint8)
        source=Image.fromarray(arr,'RGB')
        if source.size!=(pw,ph):source=source.resize((pw,ph),Image.Resampling.LANCZOS)
        names.append((f'ed_{token}_image.png',source))
        for idx,mask in enumerate(masks):
            layer=Image.fromarray(np.uint8(np.rint(np.clip(mask,0,1)*255)),'L')
            if layer.size!=(pw,ph):layer=layer.resize((pw,ph),Image.Resampling.NEAREST)
            names.append((f'ed_{token}_mask{idx:02d}.png',layer))
        refs=[]
        for name,im in names:
            im.save(folder/name,format='PNG',optimize=True)
            refs.append({'filename':name,'subfolder':FOLDER,'type':'output'})
        _cleanup(folder,{r['filename'] for r in refs})
        return {'image':refs[0],'masks':refs[1:],'preview_width':pw,'preview_height':ph}
    except (OSError,ValueError,Image.DecompressionBombError):
        # UI-only failure cannot break the actual corrected MASK computation.
        return None
