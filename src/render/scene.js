import * as THREE from 'three';
import {createCharacter} from './characters.js';
let scene,camera,renderer,config,actors,subtitle,veil;
window.initialize=function(c) {
  config=c;scene=new THREE.Scene();scene.background=new THREE.Color(c.scenario==='night'?'#111827':c.scenario==='garden'?'#9db8a2':'#343d49');
  camera=new THREE.PerspectiveCamera(36,c.width/c.height,.05,100);
  renderer=new THREE.WebGLRenderer({antialias:true,preserveDrawingBuffer:true});renderer.setSize(c.width,c.height);renderer.setPixelRatio(1);
  renderer.shadowMap.enabled=true;renderer.outputColorSpace=THREE.SRGBColorSpace;document.body.append(renderer.domElement);
  scene.add(new THREE.HemisphereLight(0xffffff,0x596375,2));
  const light=new THREE.DirectionalLight(0xffe4cc,3);light.position.set(3,6,4);light.castShadow=true;scene.add(light);
  const floor=new THREE.Mesh(new THREE.PlaneGeometry(100,100),new THREE.MeshStandardMaterial({color:0x555966,roughness:1}));floor.rotation.x=-Math.PI/2;floor.receiveShadow=true;scene.add(floor);
  actors=c.characters.map((char,i)=>{const a=createCharacter(char);a.root.position.x=i?.58:-.58;scene.add(a.root);return a;});
  subtitle=document.createElement('div');Object.assign(subtitle.style,{position:'fixed',bottom:'7%',left:'5%',width:'90%',textAlign:'center',color:'white',font:'bold 32px sans-serif',textShadow:'0 2px 5px black',whiteSpace:'pre-wrap'});document.body.append(subtitle);
  veil=document.createElement('div');Object.assign(veil.style,{position:'fixed',inset:'0',background:'black',pointerEvents:'none'});document.body.append(veil);
};
window.frame=function(t) {
  const l=config.lines.find(l=>t>=l.start && t<l.end)||config.lines.find(l=>t<l.end)||config.lines.at(-1);
  const index=config.names.indexOf(l.who),actor=actors[index];
  actors.forEach((a,i)=>a.animate(t,i===index && t>=l.start && t<l.end?(l.env[Math.floor((t-l.start)*30)]||0):0,i===index?(l.face||'neutral'):'neutral'));
  const center=new THREE.Vector3(0,1.15,0), target=new THREE.Vector3(actor.root.position.x,actor.height-.3,0);
  switch(l.shot){
    case 'close':camera.position.set(actor.root.position.x,actor.height-.2,2);camera.lookAt(target);break;
    case 'medium':camera.position.set(actor.root.position.x*.5,1.45,4.3);camera.lookAt(actor.root.position.x*.5,1.05,0);break;
    case 'orbit':camera.position.set(Math.sin(t*.15)*3,1.7,5+Math.cos(t*.15));camera.lookAt(center);break;
    case 'pan':camera.position.set(Math.sin(t*.3)*1.1,1.5,5.2);camera.lookAt(center);break;
    default:camera.position.set(0,1.55,6);camera.lookAt(center);
  }
  subtitle.textContent=config.subtitles && t>=l.start && t<l.end?l.text:'';
  veil.style.opacity=l.transition==='fade'?String(Math.max(0,1-(t-l.start)/.18)):0;
  renderer.render(scene,camera);
};
