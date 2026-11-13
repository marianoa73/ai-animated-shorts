import * as THREE from 'three';
export function createCharacter(c) {
  const root = new THREE.Group(), p=c.proportions, pal=c.palette;
  const material = color => {
    const canvas=document.createElement('canvas'); canvas.width=canvas.height=16;
    const ctx=canvas.getContext('2d'), base=new THREE.Color(color);
    for(let y=0;y<16;y++) for(let x=0;x<16;x++) {
      const shade=base.clone().multiplyScalar(.92+((x*13+y*7)%11)/70);
      ctx.fillStyle='#'+shade.getHexString(); ctx.fillRect(x,y,1,1);
    }
    const map=new THREE.CanvasTexture(canvas); map.magFilter=map.minFilter=THREE.NearestFilter; map.colorSpace=THREE.SRGBColorSpace;
    return new THREE.MeshStandardMaterial({map,roughness:.85});
  };
  const mats=Object.fromEntries(Object.entries(pal).map(([k,v])=>[k,material(v)]));
  function box(w,h,d,x,y,z,mat,parent=root) {
    const m=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),mats[mat]);m.position.set(x,y,z);m.castShadow=m.receiveShadow=true;parent.add(m);return m;
  }
  const leg=p.legHeight, torso=p.torsoHeight, head=p.headSize;
  for(const side of [-1,1]) {box(.22,leg,.28,side*.18,leg/2,0,'bottom');box(.25,.12,.4,side*.18,.06,.07,'shoes');}
  box(p.torsoWidth,torso,.38,0,leg+torso/2,0,'top');
  const arms=[];
  for(const side of [-1,1]) {
    const pivot=new THREE.Group();pivot.position.set(side*(p.torsoWidth/2+.12),leg+torso-.08,0);root.add(pivot);
    box(.18,torso*.85,.22,0,-torso*.4,0,'top',pivot);box(.18,.17,.23,0,-torso*.85,0,'skin',pivot);arms.push(pivot);
  }
  const face=new THREE.Group();face.position.y=leg+torso+head/2+.06;root.add(face);
  box(head,head,head*.85,0,0,0,'skin',face);
  if(c.features.hair)box(head*1.04,head*.18,head*.9,0,head*.44,0,'hair',face);
  const brows=[];
  for(const side of [-1,1]) {
    box(head*.1,head*.1,.025,side*head*.2,head*.08,head*.44,'eyes',face);
    brows.push(box(head*.18,head*.035,.03,side*head*.2,head*.2,head*.44,'hair',face));
    if(c.features.glasses) {
      const ring=new THREE.Mesh(new THREE.TorusGeometry(head*.12,.015,4,12),mats.eyes);ring.position.set(side*head*.2,head*.08,head*.48);face.add(ring);
    }
  }
  const mouth=box(head*.22,head*.04,.03,0,-head*.2,head*.44,'eyes',face);
  if(c.features.beard)box(head*.7,head*.1,.04,0,-head*.4,head*.43,'hair',face);
  return {root,face,mouth,arms,brows,height:leg+torso+head+.06,animate(t,volume,expression){
    root.position.y=Math.sin(t*2)*.012;face.rotation.y=Math.sin(t*.7)*.05;
    mouth.scale.y=1+volume*6; arms[0].rotation.z=Math.sin(t*2)*volume*.16;arms[1].rotation.z=-Math.sin(t*2)*volume*.16;
    brows.forEach((b,i)=>{b.rotation.z=(expression==='serious'?.25:expression==='sad'?-.25:0)*(i?1:-1);b.position.y=head*(expression==='surprised'?.3:.2);});
    mouth.rotation.z=expression==='happy'?.08:0;
  }};
}
