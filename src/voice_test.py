"""Create a local three-line test episode (ignored output); then synthesize and QA."""
import argparse
import subprocess
from common import ROOT, save
p=argparse.ArgumentParser(); p.add_argument('character'); p.add_argument('--other',required=True); p.add_argument('--language',default='es'); p.add_argument('--phrases',nargs=3,default=['Esta es una prueba de mi voz natural.','Quiero que se escuche completa cada palabra.','Esta última frase termina con claridad.']); a=p.parse_args()
# Two characters preserve the shared schema; all three reference samples are supplied by the operator.
s={'title':'Prueba de voz','scenario':'studio','language':a.language,'characters':[a.character,a.other],'lines':[{'who':a.character if i%2==0 else a.other,'text':t,'shot':'closing' if i==2 else 'medium'} for i,t in enumerate(a.phrases)]}
from common import validate_script
validate_script(s,short=True)
save(ROOT/'episodes/voice-test/script.json',s)
for args in [['python','src/voice.py','episodes/voice-test','--short'],['python','src/qa_audio.py','lines','episodes/voice-test','--short']]:
    subprocess.run(args,check=True)
