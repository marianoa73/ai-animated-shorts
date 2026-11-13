"""Offline QA; pure functions use stdlib. Whisper imports only at runtime."""
import argparse
import difflib
import json
import math
import re
import struct
import subprocess
import unicodedata
import wave
from common import ROOT, episode, spoken, read, save, local, digest, file_hash

def tokens(text):
    text=''.join(c for c in unicodedata.normalize('NFKD',text.casefold()) if not unicodedata.combining(c))
    return re.findall(r'[\u3400-\u9fff\u3040-\u30ff]|[^\W_\u3400-\u9fff\u3040-\u30ff]+',text,flags=re.UNICODE)

def equal(a,b):
    return a==b or (min(len(a),len(b))>=4 and difflib.SequenceMatcher(None,a,b).ratio()>=.8)

def align(expected,observed):
    """Fuzzy LCS returning ordered (expected index, observed index) pairs."""
    n,m=len(expected),len(observed)
    dp=[[0]*(m+1) for _ in range(n+1)]
    for i in range(n-1,-1,-1):
        for j in range(m-1,-1,-1):
            dp[i][j]=dp[i+1][j+1]+1 if equal(expected[i],observed[j]) else max(dp[i+1][j],dp[i][j+1])
    out=[]; i=j=0
    while i<n and j<m:
        if equal(expected[i],observed[j]): out.append((i,j)); i+=1; j+=1
        elif dp[i+1][j]>=dp[i][j+1]: i+=1
        else: j+=1
    return out

def db(x): return 20*math.log10(max(x,1e-12))
def rms(a): return math.sqrt(sum(x*x for x in a)/max(1,len(a)))
def pcm(path):
    with wave.open(str(path),'rb') as w:
        if w.getsampwidth()!=2 or w.getnchannels()!=1: raise ValueError('QA needs mono PCM16')
        sr=w.getframerate(); raw=w.readframes(w.getnframes())
    return [x/32768 for x in struct.unpack('<'+'h'*(len(raw)//2),raw)],sr

def review(samples,sr,text,words,engine='chatterbox'):
    fail=[]; duration=len(samples)/sr
    e=tokens(text); o=tokens(' '.join(w['word'] for w in words))
    pairs=align(e,o); ratio=len(pairs)/max(1,len(e))
    if ratio<.9: fail.append('words_below_90_percent')
    if not e or not o or not equal(e[-1],o[-1]): fail.append('last_word_missing')
    peak=db(max(map(abs,samples),default=0)); tail=db(rms(samples[-round(.15*sr):]))
    if peak>=-1: fail.append('clipping')
    if tail>=-45: fail.append('tail_not_silent')
    if not words or duration-words[-1]['end']>.6: fail.append('tail_after_word')
    if words and (words[0]['start']<0 or words[-1]['end']>duration+.1): fail.append('invalid_word_timestamps')
    n=max(1,round(.01*sr))
    activity=[max(map(abs,samples[i:i+n]),default=0)>=10**(-45/20) for i in range(0,len(samples),n)]
    active=[i for i,v in enumerate(activity) if v]
    longest=run=0
    if active:
        for v in activity[active[0]:active[-1]+1]:
            run=0 if v else run+1; longest=max(longest,run)
    else: fail.append('empty_audio')
    if longest*n/sr>.6: fail.append('internal_silence')
    cps=len(text)/max(duration,1e-9)
    if not 9<=cps<=20: fail.append('speech_rate')
    if engine!='chatterbox': fail.append('fallback_voice')
    return {'ok':not fail,'failures':fail,'duration':duration,'coverage':ratio,'peak_db':peak,'tail_db':tail,'cps':cps}

def transcribe(path,language,model=None):
    if model is None:
        from faster_whisper import WhisperModel
        model=WhisperModel('small',device='cpu',compute_type='int8',download_root=str(ROOT/'cache/models/whisper'))
    segments,_=model.transcribe(str(path),language=language,word_timestamps=True,vad_filter=False,condition_on_previous_text=False)
    return [dict(word=w.word,start=w.start,end=w.end) for seg in segments for w in (seg.words or [])]

def final_alignment(lines,words,duration):
    expected=[(i,t) for i,l in enumerate(lines) for t in tokens(spoken(l))]
    heard=[(t,w['start'],w['end']) for w in words for t in tokens(w['word'])]
    mapping=dict(align([x[1] for x in expected],[x[0] for x in heard]))
    failures=[]; ranges=[]
    for i,l in enumerate(lines):
        inds=[j for j,(li,_) in enumerate(expected) if li==i]
        matched=[mapping[j] for j in inds if j in mapping]
        if not inds or len(matched)/len(inds)<.9 or inds[-1] not in mapping: failures.append(f'line_{i}_text')
        ranges.append((heard[matched[0]][1],heard[matched[-1]][2]) if matched else None)
    for i in range(len(ranges)-1):
        if ranges[i] and ranges[i+1] and ranges[i+1][0]-ranges[i][1]>1: failures.append(f'gap_after_{i}')
    if duration<=30: failures.append('duration_not_over_30')
    return failures

def main():
    p=argparse.ArgumentParser(); p.add_argument('mode',choices=['lines','video']); p.add_argument('episode'); p.add_argument('--short',action='store_true'); a=p.parse_args()
    ep,s=episode(a.episode,a.short); name=ep.name
    report={'script_hash':digest(s),'failures':[],'lines':[]}
    from faster_whisper import WhisperModel
    m=WhisperModel('small',device='cpu',compute_type='int8',download_root=str(ROOT/'cache/models/whisper'))
    if a.mode=='lines':
        idx=read(ROOT/'cache'/f'{name}.json')
        if idx.get('script_hash')!=digest(s): raise ValueError('stale voice index')
        for i,l in enumerate(s['lines']):
            entry=idx['lines'][i]; f=local(entry['wav'])
            data,sr=pcm(f); words=transcribe(f,s['language'],m)
            r=review(data,sr,spoken(l),words,entry['engine'])
            r.update(index=i,wav_hash=file_hash(f)); report['lines'].append(r)
            if not r['ok']: report['failures'].append(i)
        report['index_hash']=digest(idx)
        dest=ROOT/'cache'/f'{name}-qa.json'
    else:
        video=ROOT/'output'/f'{name}.mp4'; meta=read(ROOT/'output'/f'{name}.json')
        if meta['script_hash']!=digest(s): raise ValueError('stale render')
        words=transcribe(video,s['language'],m)
        dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(video)],text=True))
        report['failures']=final_alignment(s['lines'],words,dur)
        if meta.get('fallback_lines'): report['failures'].append('fallback_voice')
        stats=subprocess.run(['ffmpeg','-nostdin','-i',str(video),'-af','loudnorm=I=-15:TP=-1.5:print_format=json','-f','null','-'],capture_output=True,text=True,check=True).stderr
        measured=json.loads(stats[stats.rfind('{'):stats.rfind('}')+1])
        loud=float(measured['input_i']); peak=float(measured['input_tp'])
        if not math.isfinite(loud) or abs(loud+15)>1.5: report['failures'].append('loudness')
        if not math.isfinite(peak) or peak>=-1: report['failures'].append('true_peak')
        report.update(duration=dur,lufs=loud,true_peak=peak,video_hash=file_hash(video))
        frames=[]
        for i,fraction in enumerate([.1,.35,.65,.9]):
            frame=ROOT/'output'/f'{name}-qa-{i}.png'
            subprocess.run(['ffmpeg','-nostdin','-y','-loglevel','error','-ss',str(dur*fraction),'-i',str(video),'-frames:v','1',str(frame)],check=True)
            frames.append(frame.name)
        report.update(frames=frames,visual_review='pending_human')
        dest=ROOT/'output'/f'{name}-qa.json'
    report['ok']=not report['failures']; save(dest,report)
    print(json.dumps(report,ensure_ascii=False,indent=2)); return 0 if report['ok'] else 1

if __name__=='__main__':
    try: raise SystemExit(main())
    except (ValueError,OSError,KeyError,IndexError) as e: raise SystemExit(f'QA ERROR: {e}')
