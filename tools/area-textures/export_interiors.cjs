// Original joint masks + fresh ImageGen stone interiors, exported in PLAYPAL.
const fs=require('fs'),path=require('path'),vm=require('vm');
const W=path.resolve(process.argv[2]),V=path.resolve(process.argv[3]);
let code=fs.readFileSync(path.join(__dirname,'export_palette.cjs'),'utf8').split('(async()=>{const results=[];')[0];
code+='\nObject.assign(globalThis,{sharp,read,indices,indexed,colors,L,lum,sha,wrap,pal,nearest});';
const ctx={require,Buffer,process:{argv:["node","export_palette.cjs",W,V]},globalThis:{}};vm.runInNewContext(code,ctx);const {sharp,read,indices,indexed,colors,L,lum,sha,wrap,pal,nearest}=ctx.globalThis;
const materials=JSON.parse(fs.readFileSync(path.join(V,'materials-before.json'))),names=['ADEL_B14','ADEL_B15','ADEL_F48','ADEL_B01','QBRICK3','QBRICK6','QWIZ','QCHURCH','COMPBLUE'],restore=['QGRASS','ADEL_V99','ADEL_M02'];
const mod=(n,d)=>(n%d+d)%d,clamp=(x,a,b)=>Math.min(b,Math.max(a,x)),smooth=x=>{x=clamp(x,0,1);return x*x*(3-2*x)};
function match(img,values){const a=Array.from({length:256},()=>0),b=Array.from({length:256},()=>0);for(let i=0;i<img.data.length;i+=3)a[Math.round(lum(img.data.subarray(i,i+3)))]++;for(const v of values)b[Math.round(v)]++;for(let i=1;i<256;i++){a[i]+=a[i-1];b[i]+=b[i-1]}let j=0;const map=[];for(let i=0;i<256;i++){while(j<255&&b[j]/b[255]<a[i]/a[255])j++;map[i]=j}for(let i=0;i<img.data.length;i+=3){const d=map[Math.round(lum(img.data.subarray(i,i+3)))]-lum(img.data.subarray(i,i+3));for(let k=0;k<3;k++)img.data[i+k]=clamp(Math.round(img.data[i+k]+d),0,255)}}
(async()=>{const checks=[];fs.mkdirSync(path.join(V,'masks'),{recursive:true});
for(const n of [...names,...restore]){
const m=materials.find(x=>x.name===n),o=await read(path.join(W,'originals',n+'.png')),oi=indices(o),pool=[...new Set(oi)],at=(x,y)=>oi[mod(y,o.h)*o.w+mod(x,o.w)];let idx,w=512,h=512,detail={};
if(restore.includes(n)){idx=oi;w=o.w;h=o.h;m.enabled=false;m.logical_size=[w,h];m.edge_blend=false;detail.mode='restored-original';}
else {
const gen=await read(path.join(V,'raw',n+'.png'),512);wrap(gen);
if(n==='COMPBLUE') {match(gen,Array.from(oi,i=>L[i]));idx=indices(gen,pool);for(let y=0;y<512;y++)idx[y*512+511]=idx[y*512];for(let x=0;x<512;x++)idx[511*512+x]=idx[x];detail.mode='new-circuit-topology';}
else {
 const course=n.startsWith('ADEL')?16:32,bw=n.startsWith('ADEL')?32:64;
 const rows=Array.from({length:o.h/course},(_,i)=>{let best=Infinity,yy=0;for(let d=-3;d<=2;d++){const y=mod(i*course+d,o.h);let sum=0;for(let x=0;x<o.w;x++)sum+=L[at(x,y)];if(sum<best){best=sum;yy=y}}return yy}).sort((a,b)=>a-b);
 const phases=rows.map((a,i)=>{const b=i+1<rows.length?rows[i+1]:rows[0]+o.h;let best=Infinity,phase=0;for(let x=0;x<bw;x++){let sum=0;for(let y=a+4;y<b-3;y++)for(let xx=x;xx<o.w;xx+=bw)sum+=L[at(xx,y)];if(sum<best){best=sum;phase=x}}return phase});
 const alpha=new Float32Array(o.w*o.h),vals=[];
 for(let y=0;y<o.h;y++)for(let x=0;x<o.w;x++){
  let i=rows.findLastIndex(v=>v<=y);if(i<0)i=rows.length-1;let dy=Math.min(...rows.map(r=>Math.min(mod(y-r,o.h),mod(r-y,o.h)))),dx=Math.min(mod(x-phases[i],bw),mod(phases[i]-x,bw));
  // Explicit original-coordinate mortar/edge guard; full new grain inside.
  const a=smooth((Math.min(dx,dy)-1)/2);alpha[y*o.w+x]=a;if(a>.9)vals.push(L[at(x,y)]);
 }
 match(gen,vals);const gi=Buffer.alloc(512*512),nearestL=v=>pool.reduce((a,b)=>Math.abs(L[a]-v)<Math.abs(L[b]-v)?a:b);
 for(let i=0;i<gi.length;i++)gi[i]=nearestL(lum(gen.data.subarray(i*3,i*3+3)));
 const mean=vals.reduce((a,b)=>a+b,0)/vals.length,shape=new Float64Array(o.w*o.h);
 for(let y=0;y<o.h;y++)for(let x=0;x<o.w;x++){let sum=0,weight=0;for(let dy=-3;dy<=3;dy++)for(let dx=-3;dx<=3;dx++){const k=Math.exp(-(dx*dx+dy*dy)/5);sum+=k*L[at(x+dx,y+dy)];weight+=k}shape[y*o.w+x]=sum/weight;}
 idx=Buffer.alloc(512*512);let protectedCount=0,changed=0,protectedChanged=0;
 const mask=Buffer.alloc(o.w*o.h);for(let i=0;i<mask.length;i++)mask[i]=Math.round(alpha[i]*255);await sharp(mask,{raw:{width:o.w,height:o.h,channels:1}}).png().toFile(path.join(V,'masks',n+'.png'));
 for(let y=0;y<512;y++)for(let x=0;x<512;x++){
  const base=at(x,y),a=alpha[mod(y,o.h)*o.w+mod(x,o.w)]*smooth(Math.min(x,y,511-x,511-y)/3);let result=base;
  if(a>0){const fresh=n.startsWith('Q')?shape[mod(y,o.h)*o.w+mod(x,o.w)]+1.2*(L[gi[y*512+x]]-mean):L[gi[y*512+x]];result=nearestL(L[base]*(1-a)+fresh*a)}
  idx[y*512+x]=result;if(result!==base)changed++;if(a===0){protectedCount++;if(result!==base)protectedChanged++;}
 }
 if(protectedChanged)throw Error(n+' protected mortar changed');detail={mode:'fresh-stone-interiors',protected_pixels:protectedCount,protected_changed:protectedChanged,changed_pixels:changed,joint_rows:rows,joint_columns:phases,brick_width:bw,course_height:course};
}
 m.logical_size=[512,512];m.edge_blend=false;
}
const png=indexed(w,h,idx);fs.writeFileSync(path.join(V,'assets',n+'.png'),png);m.png_sha256=sha(png);m.palette_sha256=sha(pal);checks.push({name:n,...detail,size:[w,h],png_sha256:m.png_sha256,palette_sha256:m.palette_sha256});}
fs.writeFileSync(path.join(V,'materials.json'),JSON.stringify(materials,null,2));fs.writeFileSync(path.join(V,'export-checks.json'),JSON.stringify(checks,null,2));console.log(checks.map(c=>({name:c.name,mode:c.mode,changed:c.changed_pixels,protected:c.protected_pixels})));})();
