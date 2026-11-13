"""Validate private inputs before any generation; no network requests."""
import argparse
import math
import re
import struct
import wave
from common import ROOT, local, read, episode, number

def wav_info(path):
    with wave.open(str(path),'rb') as w:
        ch, width, sr = w.getnchannels(),w.getsampwidth(),w.getframerate()
        frames = w.getnframes(); data=w.readframes(frames)
    if width != 2: raise ValueError('WAV must be PCM 16 bit')
    if len(data) != frames*ch*width: raise ValueError('truncated WAV')
    vals=struct.unpack('<'+'h'*(len(data)//2),data)
    peak=max((abs(x)/32768 for x in vals),default=0)
    return {'channels':ch,'rate':sr,'duration':frames/sr,'peak_db':20*math.log10(max(peak,1e-12))}

def check_voice(path):
    d=wav_info(path)
    if d['channels'] != 1 or d['rate'] not in [24000,44100]: raise ValueError('mono WAV, 24 or 44.1 kHz required')
    if not 10<=d['duration']<=30: raise ValueError('reference must last 10..30 s')
    if not -12<=d['peak_db']<=-3: raise ValueError('reference peak must be near -6 dBFS (-12..-3)')
    return d

def image_size(path):
    # Header inspection in stdlib; decoding/proposal uses Pillow in render image.
    with open(path,'rb') as f:
        data=f.read(32)
        if data.startswith(b'\x89PNG\r\n\x1a\n') and data[12:16]==b'IHDR':
            return struct.unpack('>II',data[16:24])
        if data[:2]!=b'\xff\xd8': raise ValueError('PNG or JPEG required')
        f.seek(2)
        while True:
            marker=f.read(1)
            if not marker: break
            if marker!=b'\xff': continue
            while marker==b'\xff': marker=f.read(1)
            if not marker: break
            code=marker[0]
            if code in [0xd9,0xda]: break
            if code in [0x01,*range(0xd0,0xd9)]: continue
            raw=f.read(2)
            if len(raw)!=2: break
            size=int.from_bytes(raw,'big')
            if size<2: break
            body=f.read(size-2)
            if len(body)!=size-2: break
            if code in [0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf]:
                if len(body)<5: break
                h,w=struct.unpack('>HH',body[1:5]); return w,h
    raise ValueError('invalid image header')

def check_image(path):
    w,h=image_size(path)
    if min(w,h)<1024: raise ValueError('image must be at least 1024 px on each side')
    return {'width':w,'height':h}

def voice_config(name):
    c=read(ROOT/'voices'/f'{name}.json')
    if not isinstance(c.get('language'),str) or not c['language']: raise ValueError('voice language')
    for key,lo,hi in [('exaggeration',0,2),('cfg',0,1),('temperature',.05,2),('tempo',.5,2),('phrase_pause',0,.3)]:
        if not number(c.get(key),lo,hi): raise ValueError(key)
    sample=local(c['sample'])
    if not sample.is_relative_to(ROOT/'voices/samples'): raise ValueError('sample must be in voices/samples')
    return c,sample

def check_character(char):
    if not isinstance(char,dict): raise ValueError('character must be an object')
    for name in ['skin','hair','top','bottom','shoes','eyes']:
        if not isinstance(char.get('palette',{}).get(name),str) or not re.fullmatch(r'#[0-9a-fA-F]{6}',char['palette'][name]): raise ValueError('palette color')
    for key in ['headSize','torsoWidth','torsoHeight','legHeight']:
        if not number(char.get('proportions',{}).get(key),.1,1.2): raise ValueError('proportion must be .1..1.2')
    for key in ['hair','beard','glasses']:
        if type(char.get('features',{}).get(key)) is not bool: raise ValueError('feature must be boolean')
    return char

def check_all(s):
    result={}
    for name in s['characters']:
        c,sample=voice_config(name)
        if c['language']!=s['language']: raise ValueError('voice and script languages differ')
        vc=check_voice(sample)
        char=check_character(read(ROOT/'characters'/f'{name}.json'))
        for view in ['front','three_quarter']:
            p=local(char['references'][view])
            if not p.is_relative_to(ROOT/'characters/refs'): raise ValueError('reference location')
            check_image(p)
        result[name]=vc
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('episode'); a=p.parse_args()
    try:
        ep,s=episode(a.episode); print(check_all(s))
    except (ValueError,KeyError,OSError,wave.Error) as e: p.exit(1,f'INPUT ERROR: {e}\n')
