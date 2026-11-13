"""Host orchestration: bounded retries, explicit long-render authorization."""
import argparse
import subprocess
from common import ROOT, episode, read

def command(service,*args):
    return subprocess.run(['docker','compose','run','--rm',service,*args],cwd=ROOT).returncode

def retry_loop(generate,check,failed,max_retries=5):
    if generate(None,0): return False
    for attempt in range(max_retries+1):
        if check()==0: return True
        indices=failed()
        if not indices or attempt==max_retries: return False
        if generate(indices,attempt+1): return False
    return False

def main():
    p=argparse.ArgumentParser(); p.add_argument('episode'); p.add_argument('--confirm-render',action='store_true'); a=p.parse_args()
    ep,s=episode(a.episode)
    if not a.confirm_render: p.error('Ask the operator before a long render; pass --confirm-render after confirmation')
    if command('voice','python','src/check_inputs.py',a.episode): return 1
    def gen(indices,attempt):
        args=['python','src/voice.py',a.episode]
        if indices is not None: args+=['--retry',','.join(map(str,indices)),'--attempt',str(attempt)]
        return command('voice',*args)
    def check():
        report=ROOT/'cache'/f'{ep.name}-qa.json'
        report.unlink(missing_ok=True)  # never consume a stale report after a crashed QA
        return command('qa','python','src/qa_audio.py','lines',a.episode)
    def failed():
        path=ROOT/'cache'/f'{ep.name}-qa.json'
        return read(path)['failures'] if path.exists() else []
    if not retry_loop(gen,check,failed):
        print('STOP: inspect cache/*-qa.json and rewrite say for failed lines; text/subtitles need not change.'); return 1
    if command('render','node','src/render/render.js',a.episode): return 1
    return command('qa','python','src/qa_audio.py','video',a.episode)

if __name__=='__main__': raise SystemExit(main())
