"""Audit authored distributable text; generated private/runtime paths are excluded."""
from pathlib import Path
import json
import re
import sys
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
patterns=[r'192'+r'\.168',r'10'+r'\.[0-9]+\.', 'duck'+'dns','ts'+r'\.net','/s'+'rv/','/ho'+'me/','mine'+'craft']
fail=[];count=0
for p in ROOT.rglob('*'):
    rel=p.relative_to(ROOT)
    if not p.is_file() or any(x in ['cache','node_modules','output','__pycache__','.git'] for x in rel.parts):continue
    if p.suffix in ('.png','.gif','.jpg'):continue
    if p.suffix=='.svg':ET.parse(p)
    if p.suffix=='.json':json.loads(p.read_text())
    text=p.read_text();count+=1
    for pattern in patterns:
        if re.search(pattern,text,re.I):fail.append(f'{rel}: privacy rule')
    if p.suffix=='.md':
        for href in re.findall(r'\]\(([^)]+)\)',text):
            if ':' in href or href.startswith('#'):continue
            target=(p.parent/href.split('#')[0])
            if not target.exists():fail.append(f'{rel}: missing link {href}')
required=['README.md','README.en.md','LICENSE','NOTICE.md','SECURITY.md','CHANGELOG.md','docs/feeding.md','docs/limitations.md','skill/ai-animated-shorts/SKILL.md','docker-compose.yml']
for name in required:
    if not (ROOT/name).is_file():fail.append(f'missing {name}')
for i,name in enumerate(['flujo','logica-control','hardware-red','herramientas','estados'],1):
    for ext in ['svg','png']:
        if not (ROOT/f'docs/assets/{i:02d}-{name}.{ext}').exists():fail.append(f'missing diagram {i}/{ext}')
if fail:print('\n'.join(fail));sys.exit(1)
print(f'OK: {count} text files, JSON/SVG parsing, local Markdown links, privacy patterns and required assets')
