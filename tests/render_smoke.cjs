// Pure synthetic animation; no private samples, cloned voices or long render.
const fs=require('fs'),path=require('path'),assert=require('assert');
const {pageFor}=require('../src/render/render.js');
(async()=>{
const root=path.resolve(__dirname,'..'),out=path.join(root,'cache/visual');fs.mkdirSync(out,{recursive:true});
const chars=['example-a','example-b'].map(n=>JSON.parse(fs.readFileSync(path.join(root,'characters',n+'.json'))));
const shots=['close','medium','orbit','pan','closing'];let checks=0;
const c={width:390,height:694,scenario:'studio',characters:chars,names:['example-a','example-b'],subtitles:false,lines:shots.map((shot,i)=>({who:i%2?'example-b':'example-a',text:'Texto de prueba',shot,face:'surprised',start:i,end:i+1,env:Array(30).fill(.6)}))};
const v=await pageFor(c);
try{for(let i=0;i<shots.length;i++){await v.page.evaluate(t=>window.frame(t),i+.5);await v.page.screenshot({path:path.join(out,shots[i]+'.png')});assert.equal(await v.page.locator('canvas').count(),1);checks++;}assert.equal(v.errors.length,0,v.errors.join('\n'));checks++;assert.equal(await v.page.getByText('Texto de prueba',{exact:true}).count(),0);checks++;}finally{await v.close();}
const w=await pageFor({...c,subtitles:true});try{await w.page.evaluate(()=>window.frame(.5));assert.equal(await w.page.getByText('Texto de prueba',{exact:true}).count(),1);checks++;}finally{await w.close();}
console.log(`OK: ${checks} render checks, five shots, no page errors, subtitles off/on`);
})().catch(e=>{console.error(e);process.exit(1);});
