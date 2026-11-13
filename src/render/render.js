// Local deterministic frame rendering. No remote assets or serving of private inputs.
const fs=require('fs'),path=require('path'),http=require('http'),crypto=require('crypto');
const {spawnSync,spawn}=require('child_process');
const {once}=require('events');
const {chromium}=require('playwright-core');
const ROOT=path.resolve(__dirname,'../..');
function local(p){const r=fs.realpathSync(path.resolve(ROOT,p));if(r!==ROOT&&!r.startsWith(ROOT+path.sep))throw Error('Path escapes project');return r;}
function run(cmd,args,opts={}){const r=spawnSync(cmd,args,{encoding:'utf8',maxBuffer:128*1024*1024,...opts});if(r.error||r.status!==0)throw Error(`${cmd} failed: ${r.error||r.stderr}`);return r.stdout;}
const read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
function duration(wav){return Number(run('ffprobe',['-v','error','-show_entries','format=duration','-of','csv=p=0',wav]));}
function envelope(wav){const pcm=run('ffmpeg',['-v','error','-i',wav,'-f','s16le','-ar','24000','-ac','1','-'],{encoding:null}),env=[];for(let o=0;o<pcm.length;o+=1600){let sum=0,n=0;for(let k=o;k+1<Math.min(o+1600,pcm.length);k+=2){sum+=(pcm.readInt16LE(k)/32768)**2;n++;}env.push(Math.sqrt(sum/Math.max(n,1)));}const mx=Math.max(...env,1e-6);return env.map(v=>v/mx);}
async function pageFor(config){
  const files={'/':path.join(__dirname,'index.html'),'/scene.js':path.join(__dirname,'scene.js'),'/characters.js':path.join(__dirname,'characters.js'),'/three.js':require.resolve('three').replace(/build\/three\.cjs$/,'build/three.module.js')};
  const server=http.createServer((req,res)=>{const f=files[req.url];if(!f){res.writeHead(404);res.end();return;}res.setHeader('Content-Type',req.url==='/'?'text/html':'text/javascript');fs.createReadStream(f).pipe(res);});
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  let browser;
  try{
    browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--no-sandbox'],downloadsPath:path.join(ROOT,'cache/downloads')});
    const page=await browser.newPage({viewport:{width:config.width,height:config.height}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
    await page.goto(`http://127.0.0.1:${server.address().port}/`);await page.waitForFunction(()=>typeof window.initialize==='function');await page.evaluate(c=>window.initialize(c),config);
    return {page,errors,close:async()=>{await browser.close();await new Promise(r=>server.close(r));}};
  }catch(e){if(browser)await browser.close();server.close();throw e;}
}
async function main(){
  const ep=local(process.argv[2]||'episodes/example'),name=path.basename(ep),s=read(path.join(ep,'script.json'));
  const preview=process.argv.includes('--preview');
  // Common validation is shared with CLI and unit tests; the renderer never bypasses it.
  run('python3',['-c','import sys;sys.path.insert(0,"src");from common import episode;episode(sys.argv[1])',path.relative(ROOT,ep)],{cwd:ROOT});
  fs.mkdirSync(path.join(ROOT,'output'),{recursive:true});fs.mkdirSync(path.join(ROOT,'cache'),{recursive:true});
  const chars=s.characters.map(n=>read(local(`characters/${n}.json`)));
  run('python3',['-c','import sys,json;sys.path.insert(0,"src");from check_inputs import check_character;[check_character(c) for c in json.loads(sys.argv[1])]',JSON.stringify(chars)],{cwd:ROOT});
  const config={...s,width:s.width||720,height:s.height||1280,characters:chars,names:s.characters,subtitles:s.subtitles===true};
  if(preview){config.lines=s.lines.map((l,i)=>({...l,start:i,end:i+1,env:[]}));const view=await pageFor(config);try{await view.page.evaluate(()=>window.frame(.5));await view.page.screenshot({path:path.join(ROOT,'output',`${name}-preview.png`)});if(view.errors.length)throw Error(view.errors.join('\n'));}finally{await view.close();}return;}
  const temp=fs.mkdtempSync(path.join(ROOT,'cache/render-'));let view=null,encoder=null;
  try{
    const idxFile=path.join(ROOT,'cache',`${name}.json`),qaFile=path.join(ROOT,'cache',`${name}-qa.json`);
    const idx=fs.existsSync(idxFile)?read(idxFile):{lines:[]};
    const scriptHash=run('python3',['-c','import sys;sys.path.insert(0,"src");from common import digest,read;print(digest(read(sys.argv[1])))',path.join(ep,'script.json')],{cwd:ROOT}).trim();
    if(idx.lines.length&&idx.script_hash!==scriptHash)throw Error('Stale audio index; regenerate voices');
    const qa=fs.existsSync(qaFile)?read(qaFile):null;
    const currentIndexHash=run('python3',['-c','import sys;sys.path.insert(0,"src");from common import digest;import json;print(digest(json.loads(sys.argv[1])))',JSON.stringify(idx)],{cwd:ROOT}).trim();
    let t=.15; const lines=[],fallback=[];
    s.lines.forEach((l,i)=>{
      let wav;const entry=idx.lines[i];
      if(entry&&fs.existsSync(path.resolve(ROOT,entry.wav))){
        wav=local(entry.wav);
        if(!qa?.ok||qa.script_hash!==scriptHash||qa.index_hash!==currentIndexHash||qa.lines[i]?.wav_hash!==hash(wav))throw Error('Run line QA on current audio before rendering');
      }else{
        console.error(`WARNING: line ${i} uses Piper fallback; final QA MUST fail`);fallback.push(i);
        const vc=read(local(`voices/${l.who}.json`));if(!vc.piper_model)throw Error('No cloned voice and no configured Piper model');
        wav=path.join(temp,`${i}.wav`);run(process.env.PIPER||'/opt/piper/piper',['--model',local(vc.piper_model),'--output_file',wav],{input:l.say||l.text});
      }
      const d=duration(wav);lines.push({...l,wav,start:t,end:t+d,env:envelope(wav)});t+=d+(s.pause??.15);
    });
    const totalDuration=t+.15;config.lines=lines;
    const voice=path.join(temp,'voice.wav'),audio=path.join(temp,'audio.wav');
    const filters=lines.map((l,i)=>`[${i}:a]adelay=${Math.round(l.start*1000)}:all=1[a${i}]`).join(';')+';'+lines.map((_,i)=>`[a${i}]`).join('')+`amix=inputs=${lines.length}:normalize=0,apad=whole_dur=${totalDuration}[a]`;
    run('ffmpeg',['-nostdin','-y','-loglevel','error',...lines.flatMap(l=>['-i',l.wav]),'-filter_complex',filters,'-map','[a]','-t',String(totalDuration),voice]);
    if(s.music!==false){
      const music=typeof s.music==='string'?local(s.music):path.join(ROOT,'cache/music.wav');
      if(!fs.existsSync(music))run('python3',['src/music.py',music],{cwd:ROOT});
      const cuts=lines.filter((l,i)=>i&&l.shot!==lines[i-1].shot);
      const fmt='aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo';
      const f=[`[0:a]${fmt},asplit=2[v][sc]`,`[1:a]${fmt},volume=0.16,atrim=duration=${totalDuration}[m]`,'[m][sc]sidechaincompress=threshold=0.015:ratio=9:attack=15:release=400[duck]'];
      if(cuts.length){f.push(`[2:a]${fmt},highpass=f=450,lowpass=f=4500,afade=t=in:d=0.08,afade=t=out:st=0.08:d=0.17,volume=0.05,asplit=${cuts.length}${cuts.map((_,i)=>`[w${i}]`).join('')}`);cuts.forEach((l,i)=>f.push(`[w${i}]adelay=${Math.max(0,Math.round((l.start-.08)*1000))}:all=1[x${i}]`));}
      f.push(`[v][duck]${cuts.map((_,i)=>`[x${i}]`).join('')}amix=inputs=${2+cuts.length}:normalize=0,loudnorm=I=-15:TP=-1.5:LRA=9,aresample=44100[a]`);
      run('ffmpeg',['-nostdin','-y','-loglevel','error','-i',voice,'-stream_loop','-1','-i',music,...(cuts.length?['-f','lavfi','-i','anoisesrc=d=0.25:c=pink:r=44100:seed=7']:[]),'-filter_complex',f.join(';'),'-map','[a]','-t',String(totalDuration),audio]);
    }else run('ffmpeg',['-nostdin','-y','-loglevel','error','-i',voice,'-af','loudnorm=I=-15:TP=-1.5:LRA=9','-ar','44100',audio]);
    view=await pageFor(config);const dest=path.join(ROOT,'output',`${name}.mp4`),partial=path.join(temp,'result.mp4');
    encoder=spawn('ffmpeg',['-nostdin','-y','-loglevel','error','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-i',audio,'-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',partial],{stdio:['pipe','ignore','inherit']});
    const completed=new Promise((resolve,reject)=>{encoder.on('error',reject);encoder.on('close',c=>c===0?resolve():reject(Error('ffmpeg encoding failed')));});completed.catch(()=>{});
    encoder.stdin.on('error',()=>{});
    const count=Math.ceil(totalDuration*30);
    for(let n=0;n<count;n++){
      if(encoder.exitCode!==null)throw Error('ffmpeg exited early');
      await view.page.evaluate(t=>window.frame(t),n/30);if(view.errors.length)throw Error(view.errors.join('\n'));
      const buf=await view.page.screenshot({type:'jpeg',quality:92});
      if(!encoder.stdin.write(buf))await Promise.race([once(encoder.stdin,'drain'),completed.then(()=>{throw Error('encoder closed early');})]);
      if(n===Math.floor(count*.4))fs.writeFileSync(path.join(ROOT,'output',`${name}.jpg`),buf);
      if(n%300===0)console.log(`Frame ${n}/${count}`);
    }
    encoder.stdin.end();await completed;fs.renameSync(partial,dest);
    const meta={title:s.title,duration:totalDuration,script_hash:scriptHash,video_hash:hash(dest),fallback_lines:fallback,lines:s.lines};
    fs.writeFileSync(path.join(ROOT,'output',`${name}.json`),JSON.stringify(meta,null,2));
    // New render invalidates its previous approval; all other video states are preserved.
    const statusFile=path.join(ROOT,'output/status.json'),states=fs.existsSync(statusFile)?read(statusFile):{};delete states[name];fs.writeFileSync(statusFile,JSON.stringify(states,null,2));
    console.log(`Created ${name}.mp4; pending final QA and visual review`);
  }finally{if(encoder&&encoder.exitCode===null)encoder.kill();if(view)await view.close();fs.rmSync(temp,{recursive:true,force:true});}
}
module.exports={pageFor,envelope,duration};
if(require.main===module)main().catch(e=>{console.error(e.message);process.exitCode=1;});
