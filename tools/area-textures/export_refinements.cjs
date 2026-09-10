// Palette/native-size export and minimum-error periodic joins for v4 artwork.
const fs=require('fs'),path=require('path'),vm=require('vm');
const W=path.resolve(process.argv[2]||__dirname),root=path.resolve(process.argv[3]||path.join(__dirname,'../..'));
let code=fs.readFileSync(path.join(root,'tools/area-textures/export_palette.cjs'),'utf8').split('(async()=>{const results=[];')[0];
code+='\nObject.assign(globalThis,{sharp,read,indices,indexed,colors,L,lum,sha,nearest,matchTone});';
const ctx={require,Buffer,process:{argv:['node','export_palette.cjs',W,W]},globalThis:{}};vm.runInNewContext(code,ctx);
const {sharp,read,indices,indexed,colors,L,lum,sha,nearest,matchTone}=ctx.globalThis;
const names=['GROUND2','GROUND3','ADEL_B01','ROCKF2','OBROWN1'],N=512,K=32;
const mod=(x,n)=>(x%n+n)%n;
function cut(a,b,h,k){let prev=new Float64Array(k),back=new Int16Array(h*k);
for(let y=0;y<h;y++){let next=new Float64Array(k);for(let x=0;x<k;x++){let v=x;if(y){for(let j=Math.max(0,x-1);j<=Math.min(k-1,x+1);j++)if(prev[j]<prev[v])v=j;}let e=0;for(let c=0;c<3;c++)e+=(a[(y*k+x)*3+c]-b[(y*k+x)*3+c])**2;next[x]=e+(y?prev[v]:0);back[y*k+x]=v;}prev=next;}
let x=0;for(let j=1;j<k;j++)if(prev[j]<prev[x])x=j;const result=[];for(let y=h-1;y>=0;y--){result[y]=x;x=back[y*k+x];}return result;}
function periodic(src){const {data,w,h}=src;const dest=Buffer.alloc(N*N*3);
const a=Buffer.alloc(h*K*3),b=Buffer.alloc(h*K*3);
for(let y=0;y<h;y++)for(let x=0;x<K;x++)for(let c=0;c<3;c++){a[(y*K+x)*3+c]=data[(y*w+N+x)*3+c];b[(y*K+x)*3+c]=data[(y*w+x)*3+c];}
const sx=cut(a,b,h,K),wide=Buffer.alloc(N*h*3);
for(let y=0;y<h;y++)for(let x=0;x<N;x++)for(let c=0;c<3;c++)wide[(y*N+x)*3+c]=data[(y*w+(x<K&&x<=sx[y]?N+x:x))*3+c];
const aa=Buffer.alloc(N*K*3),bb=Buffer.alloc(N*K*3);
for(let x=0;x<N;x++)for(let y=0;y<K;y++)for(let c=0;c<3;c++){aa[(x*K+y)*3+c]=wide[((N+y)*N+x)*3+c];bb[(x*K+y)*3+c]=wide[(y*N+x)*3+c];}
const sy=cut(aa,bb,N,K);
for(let y=0;y<N;y++)for(let x=0;x<N;x++)for(let c=0;c<3;c++)dest[(y*N+x)*3+c]=wide[((y<K&&y<=sy[x]?N+y:y)*N+x)*3+c];
return {data:dest,w:N,h:N};}
function seeded(x,y){let n=(Math.imul(x+167,374761393)^Math.imul(y+911,668265263))>>>0;n=Math.imul(n^(n>>>13),1274126177)>>>0;return (n^(n>>>16))>>>0;}
(async()=>{const materials=JSON.parse(fs.readFileSync(path.join(W,'materials-before.json'))),checks=[];
for(const name of names){const o=await read(path.join(W,'originals',name+'.png')),oi=indices(o),pool=[...new Set(oi)];let idx,w=N,h=N,detail={};
const m=materials.find(x=>x.name===name);
if(name==='OBROWN1'){idx=oi;w=o.w;h=o.h;m.enabled=false;m.logical_size=[w,h];detail.mode='restored-original';}
else if(name==='ADEL_B01'){
const gen=await read(path.join(W,'raw',name+'.png'),512);
const mask=await sharp(path.join(W,'ADEL_B01-mask.png')).toColourspace('b-w').raw().toBuffer();
const rows=[127,15,31,47,63,79,95,111].sort((a,b)=>a-b);
const prev=JSON.parse(fs.readFileSync(path.join(W,'previous-interiors-checks.json'))).find(x=>x.name===name);
const phases=prev.joint_columns,rs=prev.joint_rows;
const at=(x,y)=>oi[mod(y,o.h)*o.w+mod(x,o.w)];
const variants=[],variantOrigins=[];
for(let r=0;r<8;r++)for(let c=0;c<2;c++){const vals=[];for(let y=4;y<13;y++)for(let x=4;x<29;x++)vals.push(at(phases[r]+c*32+x,rs[r]+y));variants.push(vals.sort((a,b)=>L[a]-L[b]));variantOrigins.push([phases[r]+c*32,rs[r]]);}
idx=Buffer.alloc(N*N);let protectedCount=0;
const cellMaps=new Map();
const grain=(x,y,phase,cx,y0)=>{const gx=mod(Math.round(phase+cx*32+8+Math.max(0,Math.min(1,(x-phase-cx*32-3)/26))*16),512),gy=mod(Math.round(y0+5+Math.max(0,Math.min(1,(y-y0-3)/10))*6),512);return lum(gen.data.subarray((gy*512+gx)*3,(gy*512+gx)*3+3));};
for(let y=0;y<N;y++)for(let x=0;x<N;x++){
let row=rs.findLastIndex(r=>r<=mod(y,128));if(row<0)row=7;
const phase=phases[row],cx=Math.floor((x-phase)/32),cy=Math.floor((y-rs[row])/128)*8+row;
const key=cx+','+cy;
if(!cellMaps.has(key)){
const vals=[];const y0=cy<0?rs[row]-128:Math.floor(cy/8)*128+rs[row];
for(let yy=4;yy<13;yy++)for(let xx=4;xx<29;xx++){vals.push(grain(phase+cx*32+xx,y0+yy,phase,cx,y0));}
vals.sort((a,b)=>a-b);const vi=seeded(mod(cx,16),mod(cy,32))%variants.length;cellMaps.set(key,{y0,vals,target:variants[vi],origin:variantOrigins[vi]});
}
const cm=cellMaps.get(key),v=grain(x,y,phase,cx,cm.y0);let rank=cm.vals.findIndex(a=>a>=v);if(rank<0)rank=cm.vals.length-1;
const generated=cm.target[Math.round(rank/(cm.vals.length-1)*(cm.target.length-1))],native=at(cm.origin[0]+mod(x-phase,32),cm.origin[1]+mod(y-cm.y0,16)),fresh=nearest(colors[native].map((c,k)=>c*.7+colors[generated][k]*.3),pool),base=at(x,y);
let a=mask[mod(y,o.h)*o.w+mod(x,o.w)]/255;
a*=Math.min(1,x/3,y/3,(511-x)/3,(511-y)/3);
idx[y*N+x]=a===0?base:nearest(colors[base].map((b,k)=>b*(1-a)+colors[fresh][k]*a),pool);
if(a===0)protectedCount++;
}
detail={mode:'original-joints-and-brick-tones-fresh-interiors',protected_pixels:protectedCount,brick_width:32,course_height:16};

}
else {let gen=await read(path.join(W,'raw',name+'.png'),N+K);gen=periodic(gen);matchTone(gen,o);idx=indices(gen,pool);detail.mode='original-reference-periodic-minimum-error-join';}
const png=indexed(w,h,idx);fs.writeFileSync(path.join(W,'assets',name+'.png'),png);
m.logical_size=[w,h];m.edge_blend=false;m.png_sha256=sha(png);m.palette_sha256=sha(fs.readFileSync(path.join(W,'PLAYPAL.pal')).subarray(0,768));
checks.push({name,size:[w,h],...detail,png_sha256:m.png_sha256,palette_sha256:m.palette_sha256});
await sharp(png).linear(name.startsWith('GROUND')?3:1).png().toFile(path.join(W,'review',name+'-visible.png'));
const originTile=Buffer.alloc(N*N*3);for(let y=0;y<N;y++)for(let x=0;x<N;x++)for(let c=0;c<3;c++)originTile[(y*N+x)*3+c]=o.data[((y%o.h)*o.w+x%o.w)*3+c];
await sharp(originTile,{raw:{width:N,height:N,channels:3}}).linear(name.startsWith('GROUND')?3:1).png().toFile(path.join(W,'review',name+'-original-tiled.png'));
}
fs.writeFileSync(path.join(W,'materials.json'),JSON.stringify(materials,null,2));fs.writeFileSync(path.join(W,'export-checks.json'),JSON.stringify(checks,null,2));console.log(checks);})();