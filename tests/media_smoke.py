"""Opt-in real FFmpeg/Chromium smoke, synthetic tones only; requires JS dependencies."""
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import wave
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from common import ROOT,read,save,digest,file_hash
name='synthetic-check';ep=ROOT/'episodes'/name;cache=ROOT/'cache/media-check';out=ROOT/'output'
if ep.exists():raise SystemExit('refusing to overwrite existing synthetic-check episode')
status_path=out/'status.json'
status_before=status_path.read_bytes() if status_path.exists() else None
ep.mkdir();cache.mkdir(parents=True,exist_ok=True);out.mkdir(exist_ok=True)
try:
 s=read(ROOT/'episodes/example/script.json');s.update(width=160,height=284);save(ep/'script.json',s)
 wav=cache/'tone.wav'
 with wave.open(str(wav),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000)
  w.writeframes(b''.join(struct.pack('<h',int(3000*math.sin(i*.1))) for i in range(62400)))
 entries=[{'wav':str(wav.relative_to(ROOT)),'seed':1,'engine':'chatterbox','key':'synthetic-fixture-only'} for _ in s['lines']]
 idx={'script_hash':digest(s),'lines':entries};save(ROOT/'cache'/f'{name}.json',idx)
 save(ROOT/'cache'/f'{name}-qa.json',{'ok':True,'script_hash':digest(s),'index_hash':digest(idx),'lines':[{'wav_hash':file_hash(wav)} for _ in entries]})
 # This fixture is NOT a voice QA pass: bypassed transcription is explicit and isolated.
 runtime=os.environ.get('JS_RUNTIME','node')
 subprocess.run([runtime,'src/render/render.js',str(ep.relative_to(ROOT))],cwd=ROOT,check=True)
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out/f'{name}.mp4')]))
 assert float(info['format']['duration'])>30
 assert {s['codec_name'] for s in info['streams']}=={'h264','aac'}
 v=next(s for s in info['streams'] if s['codec_type']=='video');assert (v['width'],v['height'],v['r_frame_rate'])==(160,284,'30/1')
 assert not read(out/f'{name}.json')['fallback_lines']
 print('OK: synthetic full render, music + ducking + whooshes, H.264/AAC, 30 fps, >30 s; NOT a voice/model validation')
finally:
 if status_before is None:status_path.unlink(missing_ok=True)
 else:status_path.write_bytes(status_before)
 shutil.rmtree(ep)
 shutil.rmtree(cache)
 for f in out.glob(name+'*'):f.unlink()
 for f in (ROOT/'cache').glob(name+'*'):f.unlink()
