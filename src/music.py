"""Deterministic procedural background loop; no recordings or external service."""
import argparse
import math
import random
import struct
import wave
from pathlib import Path

def generate(path,seconds=24,sr=24000):
    rng=random.Random(7); path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    chords=[(220,261.63,329.63),(174.61,220,261.63),(130.81,164.81,196),(196,246.94,293.66)]
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        block=[]
        for i in range(round(seconds*sr)):
            t=i/sr; phase=t%6; notes=chords[int(t//6)%4]
            pad=sum(math.sin(2*math.pi*f*t) for f in notes)/3
            env=min(1,phase/.4,(6-phase)/.4)*min(1,t/.5,(seconds-t)/.5)
            pulse=math.exp(-(t%.6)*20)*math.sin(2*math.pi*55*t)
            val=.17*pad*env+.04*pulse+.003*(rng.random()*2-1)
            block.append(struct.pack('<h',int(val*32767)))
            if len(block)==4096: w.writeframes(b''.join(block)); block=[]
        w.writeframes(b''.join(block))
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('output'); p.add_argument('--seconds',type=float,default=24); a=p.parse_args()
    if not .5<=a.seconds<=600: p.error('seconds must be .5..600')
    generate(a.output,a.seconds)
