"""Chatterbox CPU synthesis, content-addressed cache and per-line retry seeds."""
import argparse
import os
import re
import subprocess
from common import ROOT, episode, spoken, digest, file_hash, read, save, local
from check_inputs import voice_config, check_voice

def phrases(text):
    parts=[p.strip() for p in re.findall(r'[^.?!|。！？]+[.?!。！？]*',text) if p.strip(' |')]
    out=[]
    for p in parts:
        if out and len(out[-1].split())<3: out[-1]+=' '+p
        else: out.append(p)
    if len(out)>1 and len(out[-1].split())<3:
        last=out.pop()   # remove BEFORE indexing the previous phrase
        out[-1]+=' '+last
    return out

def cache_key(text,seed,config,sample_hash):
    return digest({'text':text,'seed':seed,'config':config,'sample':sample_hash,'engine':'chatterbox-0.1.7','processing':1})

class Synth:
    def __init__(self):
        import torch
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS
        torch.set_num_threads(max(1,os.cpu_count() or 1))
        self.model=ChatterboxMultilingualTTS.from_pretrained(device='cpu')
    def generate(self,text,seed,c,sample,path):
        import torch
        import torchaudio
        torch.manual_seed(seed)
        sr=self.model.sr; clips=[]
        for phrase in phrases(text):
            audio=self.model.generate(phrase,language_id=c['language'],audio_prompt_path=str(sample),exaggeration=c['exaggeration'],cfg_weight=c['cfg'],temperature=c['temperature'])
            n=max(1,int(.02*sr)); bins=audio[0,:audio.shape[-1]//n*n].reshape(-1,n)
            active=(bins.pow(2).mean(1).sqrt()>.006).nonzero()
            if len(active):
                audio=audio[...,max(0,int(active[0])*n-int(.12*sr)):min(audio.shape[-1],(int(active[-1])+1)*n+int(.12*sr))]
            clips.extend([audio,torch.zeros(1,int(c['phrase_pause']*sr))])
        if not clips: raise ValueError('no speakable phrases')
        raw=path.with_suffix('.raw.wav')
        try:
            torchaudio.save(str(raw),torch.cat(clips[:-1],dim=-1),sr)
            # QA sees the exact final tempo. A quiet 180 ms pad protects the last phoneme.
            subprocess.run(['ffmpeg','-nostdin','-y','-loglevel','error','-i',str(raw),'-af',f"atempo={c['tempo']},apad=pad_dur=0.18,alimiter=limit=0.8:level=disabled",'-ar','24000','-ac','1','-c:a','pcm_s16le',str(path)],check=True)
        finally: raw.unlink(missing_ok=True)

def generate(ep,s,retry=None,attempt=0,synth_factory=Synth):
    index_path=ROOT/'cache'/f'{ep.name}.json'
    old=read(index_path) if index_path.exists() else {}
    if old.get('script_hash')!=digest(s): old={}
    output=[]; synth=None
    for i,l in enumerate(s['lines']):
        c,sample=voice_config(l['who']); check_voice(sample)
        seed=l.get('seed',1)+attempt
        if retry is not None and i not in retry:
            previous=old.get('lines',[])
            if i>=len(previous): raise ValueError('retry needs a complete current index')
            # Reuse only entries whose sample/config/text still match the content key.
            candidate=previous[i]
            key=cache_key(l.get('say',l['text']),candidate['seed'],c,file_hash(sample))
            if key!=candidate['key'] or not local(candidate['wav']).exists(): raise ValueError('inputs changed; regenerate initial episode')
            output.append(candidate); continue
        key=cache_key(l.get('say',l['text']),seed,c,file_hash(sample)); path=ROOT/'cache/audio'/f'{key}.wav'
        if not path.exists():
            path.parent.mkdir(parents=True,exist_ok=True)
            if synth is None: synth=synth_factory()
            tmp=path.with_name(key+'.partial.wav')
            try:
                synth.generate(l.get('say',l['text']),seed,c,sample,tmp)
                tmp.replace(path)
            finally: tmp.unlink(missing_ok=True)
        output.append(dict(key=key,wav=str(path.relative_to(ROOT)),seed=seed,engine='chatterbox'))
    save(index_path,dict(script_hash=digest(s),lines=output))
    return output

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('episode'); p.add_argument('--retry',help='comma-separated zero-based indices'); p.add_argument('--attempt',type=int,default=0); p.add_argument('--short',action='store_true'); a=p.parse_args()
    try:
        if not 0<=a.attempt<=5: raise ValueError('attempt must be 0..5')
        ep,s=episode(a.episode,a.short)
        retry=None if a.retry is None else set(map(int,a.retry.split(',')))
        if retry is not None and not retry<=set(range(len(s['lines']))): raise ValueError('retry indices')
        print(f'{len(generate(ep,s,retry,a.attempt))} indexed lines')
    except (ValueError,KeyError,OSError) as e: p.exit(1,f'VOICE ERROR: {e}\n')
