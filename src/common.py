"""Shared, dependency-free configuration and file boundaries."""
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOTS = {'close', 'medium', 'orbit', 'pan', 'closing'}
FACES = {'neutral', 'happy', 'sad', 'surprised', 'serious'}

def local(path, root=ROOT):
    p = (root / path).resolve()
    if not p.is_relative_to(root.resolve()):
        raise ValueError('Path must stay inside the project')
    return p

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def save(path, value):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(p)

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def file_hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()

def spoken(line):
    return line.get('say', line['text']).replace('|', ' ')

def number(x, lo, hi):
    return type(x) in (int, float) and math.isfinite(x) and lo <= x <= hi

def validate_script(s, short=False):
    if not isinstance(s, dict): raise ValueError('script must be an object')
    for k in ['title', 'scenario', 'language']:
        if not isinstance(s.get(k), str) or not s[k].strip(): raise ValueError(k)
    if s['scenario'] not in ['studio','night','garden']: raise ValueError('unknown scenario; extend scene.js first')
    chars = s.get('characters')
    if not isinstance(chars, list) or len(chars) != 2 or any(not isinstance(c,str) for c in chars) or len(set(chars)) != 2:
        raise ValueError('exactly two distinct characters required')
    if any(not isinstance(c, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]*', c) for c in chars):
        raise ValueError('character identifiers')
    if type(s.get('subtitles', False)) is not bool: raise ValueError('subtitles must be boolean')
    if s.get('fps', 30) != 30: raise ValueError('fps must be 30')
    for k, default in [('width',720), ('height',1280)]:
        n = s.get(k,default)
        if type(n) is not int or n < 64 or n > 2160 or n % 2: raise ValueError(k)
    if not number(s.get('pause',.15),0,.3): raise ValueError('pause must be 0..0.3')
    lines = s.get('lines')
    if not isinstance(lines,list) or not 2 <= len(lines) <= 200: raise ValueError('lines: 2..200')
    for i,l in enumerate(lines):
        if not isinstance(l,dict) or l.get('who') not in chars: raise ValueError('who')
        if i and l['who'] == lines[i-1]['who']: raise ValueError('alternate speakers')
        if not isinstance(l.get('text'),str) or not l['text'].strip() or len(l['text']) > 500: raise ValueError('text')
        if 'say' in l and (not isinstance(l['say'],str) or not l['say'].strip() or len(l['say'])>500): raise ValueError('say')
        if l.get('shot') not in SHOTS: raise ValueError('shot')
        if l.get('face','neutral') not in FACES: raise ValueError('face')
        if l.get('transition','cut') not in ['cut','fade']: raise ValueError('transition')
        if type(l.get('seed',1)) is not int or not 0 <= l.get('seed',1) < 2**31: raise ValueError('seed')
    if lines[-1]['shot'] != 'closing': raise ValueError('last shot must be closing')
    estimate = sum(len(spoken(l)) for l in lines) / 15
    if not short and estimate <= 30: raise ValueError('estimated speech must exceed 30 s')
    return estimate

def episode(path, short=False):
    ep = local(path)
    if ep.parent != ROOT/'episodes': raise ValueError('use episodes/<name>')
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*',ep.name): raise ValueError('episode name')
    s = read(ep/'script.json'); validate_script(s,short)
    return ep,s
