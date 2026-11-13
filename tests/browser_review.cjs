const {chromium}=require('playwright-core'),fs=require('fs'),path=require('path'),assert=require('assert');
(async()=>{
const root=path.resolve(__dirname,'..'),out=path.join(root,'cache/visual');fs.mkdirSync(out,{recursive:true});
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||undefined,args:['--no-sandbox','--disable-gpu']});let checks=0;
try{
for(const width of [390,1280]){
 const page=await browser.newPage({viewport:{width,height:900}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.route('http://localhost/**',async route=>{
  const url=new URL(route.request().url()),p=url.pathname;
  let body,type='application/json';
  if(p==='/'){body=fs.readFileSync(path.join(root,'web/index.html'),'utf8');type='text/html';}
  else if(p==='/listing/')body=JSON.stringify([{name:'nuevo.mp4',type:'file'},{name:'aprobado.mp4',type:'file'}]);
  else if(p==='/media/status.json')body=JSON.stringify({aprobado:{state:'aprobados',video_hash:'hash'}});
  else if(p==='/media/aprobado.json')body=JSON.stringify({title:'Video aprobado',video_hash:'hash'});
  else if(p==='/media/nuevo.json')body=JSON.stringify({title:'<script>test</script> título literal',video_hash:'new'});
  else if(p==='/media/aprobado-qa.json')body=JSON.stringify({ok:true,video_hash:'hash'});
  else body='{}';
  await route.fulfill({status:200,contentType:type,body});
 });
 await page.goto('http://localhost/');await page.getByRole('heading',{name:'<script>test</script> título literal'}).waitFor();checks++;
 assert.equal(await page.locator('article').count(),1);checks++;
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));checks++;
 await page.screenshot({path:path.join(out,`web-${width}.png`),fullPage:true});
 await page.getByRole('button',{name:'Aprobados',exact:true}).click();await page.getByRole('heading',{name:'Video aprobado'}).waitFor();checks++;
 assert.equal(errors.length,0);checks++;await page.close();
}
const p=await browser.newPage({viewport:{width:1500,height:1000}});
for(const theme of ['white','#0F1115']){
 const imgs=['01-flujo','02-logica-control','03-hardware-red','04-herramientas','05-estados'].map(n=>`<img alt="${n}" style="width:680px;margin:10px;border:1px solid #888" src="data:image/svg+xml;base64,${fs.readFileSync(path.join(root,'docs/assets',n+'.svg')).toString('base64')}">`).join('');
 await p.setContent(`<body style="background:${theme};margin:10px">${imgs}</body>`);
 await p.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));checks+=5;
 await p.screenshot({path:path.join(out,`diagrams-${theme==='white'?'light':'dark'}.png`),fullPage:true});
}
console.log(`OK: ${checks} browser checks; mobile/desktop, state/default, literal text, diagrams light/dark`);
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
