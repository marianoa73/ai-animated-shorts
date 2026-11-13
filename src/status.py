"""Manual review-state changes; never publishes a video."""
import argparse
import re
from common import ROOT,read,save,file_hash

def set_status(name,state,visual_reviewed=False,root=ROOT):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*',name): raise ValueError('invalid identifier')
    if state not in ['revision','pruebas','aprobados','produccion']:raise ValueError('invalid state')
    video=root/'output'/f'{name}.mp4'
    if not video.exists():raise ValueError('video does not exist')
    h=file_hash(video)
    if state in ['aprobados','produccion']:
        qa=read(root/'output'/f'{name}-qa.json')
        if not qa.get('ok') or qa.get('video_hash')!=h or not visual_reviewed:
            raise ValueError('current video must pass QA and have explicit visual review')
    f=root/'output/status.json';states=read(f) if f.exists() else {}
    states[name]={'state':state,'video_hash':h};save(f,states)
    return states

def main():
    p=argparse.ArgumentParser();p.add_argument('episode');p.add_argument('state',choices=['revision','pruebas','aprobados','produccion']);p.add_argument('--visual-reviewed',action='store_true');a=p.parse_args()
    try:set_status(a.episode,a.state,a.visual_reviewed)
    except (ValueError,OSError,KeyError) as e:p.exit(1,f'STATUS ERROR: {e}\n')
    print('Local state updated; nothing published.')
if __name__=='__main__':main()
