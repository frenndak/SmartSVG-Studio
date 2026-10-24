"""Non-essential bounded preflight visual PNG; never edits manufacturing files."""
from __future__ import annotations
from pathlib import Path
from uuid import uuid4
from time import time
import re
import numpy as np
from PIL import Image, ImageDraw

FOLDER='SmartSVG_Studio_QA'
NAME=re.compile(r'qa217_[a-f0-9]{24}\.png\Z')
MAX_FILES=48
MAX_AGE=72*3600


def publish(image,masks,results,output_directory):
    if not output_directory or Path(output_directory).is_symlink():return None
    root=Path(output_directory).resolve()
    if not root.is_dir():return None
    dest=root/FOLDER
    if dest.is_symlink():return None
    try:
        dest.mkdir(exist_ok=True)
        if not dest.resolve().is_relative_to(root):return None
        old=sorted([p for p in dest.iterdir() if p.is_file() and not p.is_symlink() and NAME.fullmatch(p.name)],
            key=lambda p:p.stat().st_mtime,reverse=True)
        now=time()
        for index,p in enumerate(old):
            if index>=MAX_FILES-1 or now-p.stat().st_mtime>MAX_AGE:
                p.unlink(missing_ok=True)
        h,w=image.shape[:2];factor=min(1.,1024/max(h,w));pw=max(1,round(w*factor));ph=max(1,round(h*factor))
        base=Image.fromarray(np.uint8(np.rint(np.clip(image[...,:3],0,1)*255)),'RGB')
        if (w,h)!=(pw,ph):base=base.resize((pw,ph),Image.Resampling.LANCZOS)
        # Union alpha overlay: green mask pixel occupancy, leave source visible.
        union=np.any(masks>=.5,axis=0)
        alpha=Image.fromarray((union.astype(np.uint8)*65),'L')
        if (w,h)!=(pw,ph):alpha=alpha.resize((pw,ph),Image.Resampling.NEAREST)
        green=Image.new('RGB',(pw,ph),(27,225,115))
        base.paste(green,(0,0),alpha)
        painter=ImageDraw.Draw(base)
        for obj in results.get('objets',[]):
            b=obj.get('boite_px')
            if b:
                color=(255,165,30) if obj['etat']!='ok' else (55,255,135)
                x0,y0,x1,y1=b
                painter.rectangle((int(x0*factor),int(y0*factor),int((x1-1)*factor),int((y1-1)*factor)),outline=color,width=2)
        filename=f'qa217_{uuid4().hex[:24]}.png';base.save(dest/filename,'PNG',optimize=True)
        return {'filename':filename,'subfolder':FOLDER,'type':'output'}
    except (OSError,ValueError,Image.DecompressionBombError):
        return None
