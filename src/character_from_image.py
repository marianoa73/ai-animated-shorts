"""Propose zone colors from an owned front reference. Human adjustment required."""
import argparse
from common import ROOT,local,read,save
from check_inputs import check_image

def propose(image,base):
    from PIL import Image,ImageStat
    check_image(image)
    with Image.open(image) as raw:
        im=raw.convert('RGB'); w,h=im.size
        # Assumes centered full-body reference; no face recognition or identity inference.
        zones={'skin':(.43,.12,.57,.22),'hair':(.4,.04,.6,.09),'top':(.4,.32,.6,.5),'bottom':(.42,.66,.58,.8),'shoes':(.4,.91,.6,.96)}
        for name,(x0,y0,x1,y1) in zones.items():
            crop=im.crop((int(x0*w),int(y0*h),int(x1*w),int(y1*h)))
            values=ImageStat.Stat(crop).median
            base['palette'][name]='#'+''.join(f'{int(v):02x}' for v in values)
    return base
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('image'); p.add_argument('output'); p.add_argument('--base',default='characters/example-a.json'); a=p.parse_args()
    out=local(a.output)
    if out.exists(): p.error('output exists; choose a new proposal file')
    base=read(local(a.base)); base['references']['front']=str(local(a.image).relative_to(ROOT))
    save(out,propose(local(a.image),base)); print('Proposal only: inspect palette, proportions, features and reference paths before adopting.')
