// Production export of ImageGen artwork: native pixel grid, PLAYPAL and wrap.
const fs=require('fs'),path=require('path'),zlib=require('zlib'),crypto=require('crypto');
const sharp=require('sharp');
if(process.argv.length<4)throw Error('Usage: node export_palette.cjs <original-workspace> <revision-workspace>');
const W=path.resolve(process.argv[2]),R=path.resolve(process.argv[3]);
const groups=JSON.parse(fs.readFileSync(path.join(R,'groups.json'))),materials=JSON.parse(fs.readFileSync(path.join(W,'materials.json')));
const pal=fs.readFileSync(path.join(R,'PLAYPAL.pal')).subarray(0,768),colors=Array.from({length:256},(_,i)=>[...pal.subarray(i*3,i*3+3)]);
const lum=c=>.2126*c[0]+.7152*c[1]+.0722*c[2],L=colors.map(lum),sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const crcTable=Array.from({length:256},(_,n)=>{for(let j=0;j<8;j++)n=(n&1)?0xedb88320^(n>>>1):n>>>1;return n>>>0});
function chunk(type,data){const t=Buffer.from(type),b=Buffer.concat([t,data]);let crc=0xffffffff;for(const v of b)crc=crcTable[(crc^v)&255]^(crc>>>8);const n=Buffer.alloc(4),c=Buffer.alloc(4);n.writeUInt32BE(data.length);c.writeUInt32BE((crc^0xffffffff)>>>0);return Buffer.concat([n,b,c])}
function indexed(w,h,data){const header=Buffer.alloc(13);header.writeUInt32BE(w);header.writeUInt32BE(h,4);header[8]=8;header[9]=3;const rows=Buffer.alloc((w+1)*h);for(let y=0;y<h;y++)data.copy(rows,y*(w+1)+1,y*w,(y+1)*w);return Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]),chunk('IHDR',header),chunk('PLTE',pal),chunk('IDAT',zlib.deflateSync(rows)),chunk('IEND',Buffer.alloc(0))])}
function nearest(c,pool=colors.map((_,i)=>i),lo=-1,hi=256){let best=-1,score=Infinity;for(const i of pool){if(L[i]<lo||L[i]>hi)continue;let d=0;for(let k=0;k<3;k++)d+=(c[k]-colors[i][k])**2;if(d<score){score=d;best=i}}return best}
async function read(file,size){let s=sharp(file).removeAlpha();if(size)s=s.resize(size,size,{kernel:'nearest'});const {data,info}=await s.raw().toBuffer({resolveWithObject:true});return {data,w:info.width,h:info.height}}
function indices(img,pool){const result=Buffer.alloc(img.w*img.h),cache=new Map();for(let i=0;i<result.length;i++){const c=[...img.data.subarray(i*3,i*3+3)],key=c.join(',');if(!cache.has(key))cache.set(key,nearest(c,pool));result[i]=cache.get(key)}return result}
function cdf(data){const a=new Float64Array(256);for(let i=0;i<data.length;i+=3)a[Math.round(lum(data.subarray(i,i+3)))]++;for(let i=1;i<256;i++)a[i]+=a[i-1];return a.map(v=>v/(data.length/3))}
function matchTone(img,original){const a=cdf(img.data),b=cdf(original.data),map=[];let j=0;for(let i=0;i<256;i++){while(j<255&&b[j]<a[i])j++;map[i]=j}for(let i=0;i<img.data.length;i+=3){const l=lum(img.data.subarray(i,i+3)),d=map[Math.round(l)]-l;for(let k=0;k<3;k++)img.data[i+k]=Math.max(0,Math.min(255,Math.round(img.data[i+k]+d)))}}
function wrap(img){const {w,h,data}=img,src=Buffer.from(data);const smooth=t=>{t=Math.max(0,Math.min(1,t));return t*t*(3-2*t)};for(let y=0;y<h;y++)for(let x=0;x<w;x++){const ax=smooth(Math.min(x,w-1-x)/8),ay=smooth(Math.min(y,h-1-y)/8),xx=(x+(w>>1))%w,yy=(y+(h>>1))%h;for(let k=0;k<3;k++){const at=(xx,yy)=>src[(yy*w+xx)*3+k];data[(y*w+x)*3+k]=Math.round(ay*(ax*at(x,y)+(1-ax)*at(xx,y))+(1-ay)*(ax*at(x,yy)+(1-ax)*at(xx,yy)))}}}
(async()=>{const results=[];for(const m of materials){const name=m.name,original=await read(path.join(W,'originals',name+'.png')),oi=indices(original);let img,idx,detail={};
if(groups.reset.includes(name)){img=original;idx=oi;m.enabled=false;m.logical_size=m.original_size;m.edge_blend=false;detail.mode='restored-original';}
else if(groups.exact.includes(name)){
 const size=512,gen=await read(path.join(R,'before',name+'.png'),size),pool=[...new Set(oi)];img={w:size,h:size};idx=Buffer.alloc(size*size);let changed=0,gradientInversions=0;
 const orig=(x,y)=>oi[((y+original.h)%original.h)*original.w+(x+original.w)%original.w];
 for(let y=0;y<size;y++)for(let x=0;x<size;x++){const base=orig(x,y),v=L[base];let lo=Math.max(0,v-7),hi=Math.min(255,v+7);
  for(let dy=-1;dy<=1;dy++)for(let dx=-1;dx<=1;dx++){if(!dx&&!dy)continue;const n=L[orig(x+dx,y+dy)];if(n<v)lo=Math.max(lo,(n+v)/2+.001);if(n>v)hi=Math.min(hi,(n+v)/2-.001);}
  let avg=0;for(let dy=-2;dy<=2;dy++)for(let dx=-2;dx<=2;dx++)avg+=lum(gen.data.subarray((((y+dy+size)%size)*size+(x+dx+size)%size)*3,(((y+dy+size)%size)*size+(x+dx+size)%size)*3+3));avg/=25;
  const value=lum(gen.data.subarray((y*size+x)*3,(y*size+x)*3+3)),edge=Math.min(1,x/4,y/4,(size-1-x)/4,(size-1-y)/4),delta=Math.max(-7,Math.min(7,(value-avg)*2))*edge;
  const c=colors[base].map(v=>v+delta),candidate=nearest(c,pool,lo,hi);idx[y*size+x]=candidate<0?base:candidate;if(idx[y*size+x]!==base)changed++;
 }
 // A strict original gradient must not reverse or collapse in the final pixels.
 for(let y=0;y<size;y++)for(let x=0;x<size;x++)for(const [dx,dy] of [[1,0],[0,1],[1,1],[-1,1]]){const a=L[orig(x,y)],b=L[orig(x+dx,y+dy)],u=L[idx[y*size+x]],v=L[idx[((y+dy)%size)*size+(x+dx+size)%size]];if(a!==b&&Math.sign(a-b)!==Math.sign(u-v))gradientInversions++;}
 if(gradientInversions)throw Error(name+' structural gradient changed: '+gradientInversions);
 m.logical_size=[512,512];m.preserve_phase=true;m.edge_blend=false;detail={mode:'original-grid-constrained-detail',changed_pixels:changed,gradient_inversions:gradientInversions,pixels_per_map_unit:1};
}else{
 const regen=groups.regenerate.includes(name);img=await read(path.join(R,regen?'raw':'before',name+'.png'),regen?512:undefined);
 if(regen){matchTone(img,original);wrap(img);m.logical_size=[512,512];m.edge_blend=false;}
 idx=indices(img,regen?[...new Set(oi)]:undefined);
 if(regen){for(let y=0;y<img.h;y++)idx[y*img.w+img.w-1]=idx[y*img.w];for(let x=0;x<img.w;x++)idx[(img.h-1)*img.w+x]=idx[x];}
 detail.mode=regen?'regenerated-original-reference':'palette-export';
}
const output=indexed(img.w,img.h,idx);fs.writeFileSync(path.join(R,'assets',name+'.png'),output);m.png_sha256=sha(output);m.palette_sha256=sha(pal);
results.push({name,...detail,size:[img.w,img.h],colors:new Set(idx).size,palette_sha256:sha(pal),png_sha256:m.png_sha256});console.log(name,detail.mode,detail.changed_pixels??'');
}
fs.writeFileSync(path.join(R,'materials.json'),JSON.stringify(materials,null,2));fs.writeFileSync(path.join(R,'export-checks.json'),JSON.stringify(results,null,2));})();
