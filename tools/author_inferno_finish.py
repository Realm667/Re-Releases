"""Explicit editable TNT04B fade-band, cinder and lighting authoring. Not packaging."""
from pathlib import Path
from collections import defaultdict
import math,json,subprocess
from PIL import Image
from test_caldera_structure import parse
from build_environment_fx import geometry,bounds
from build_sky_edges import wall_uv,mapping
from author_cavern import edit_text
from build_utnt import read_wad,write_wad,atomic_write
ROOT=Path(__file__).resolve().parents[1]
def author(root=ROOT):
 p=root/'tutnt/maps/tnt04b.wad';l,g=parse(p);assert b'Inferno alpha bases' not in l['TEXTMAP']
 assert not any('64123' in (s.get('id','')+' '+s.get('moreids','').strip(chr(34))).split() for s in g['sector'])
 geo=geometry(g);changes={'sector':{}};groups=defaultdict(list);emit=[]
 variants={}
 for tex in ['HOTROCK','HOTSTONE']:
  file=next(q for q in (root/'tutnt/textures').iterdir() if q.stem.upper()==tex)
  variants[tex]={'logical':Image.open(file).size}
 bindings=mapping(root,'tnt04b')
 for si in (1463,2227):
  changes['sector'][si]={'moreids':'"64123"'}
  occupied=set()
  for a,b,li,sd in geo[si]:
   line=g['linedef'][li];face=0 if int(line['sidefront'])==sd else 1;other=int(line.get('sideback',-1)) if face==0 else int(line['sidefront'])
   if other<0:continue
   ns=int(g['sidedef'][other]['sector']);h=float(g['sector'][ns]['heightfloor'])
   if h<=-200:continue
   raw=g['sidedef'][sd]['texturebottom'].strip('"');assert raw in variants
   c=wall_uv(dict(side=g['sidedef'][sd],linedef=line,front=g['sector'][si],back=g['sector'][ns],part=2,texture=raw,line=li,face=face),variants,bindings)
   groups[(si,ns,raw)].append((a,b,c))
   dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);nx=dy/length;ny=-dx/length;x=(a[0]+b[0])/2+nx*28;y=(a[1]+b[1])/2+ny*28
   cell=(int(x//512),int(y//512))
   if cell not in occupied and length>=48:
    occupied.add(cell);emit.append((x,y,max(-104,h-32),si,0,len(occupied)%3==0))
 # Warm ambient color restricted to the two island rooms, including the tower.
 tinted=[]
 for si,edges in geo.items():
  x0,y0,x1,y1=bounds(edges)
  if x0>=0 and x1<=5120 and ((y0>=-6144 and y1<=-3584) or (y0>=-8832 and y1<=-6272)):
   changes['sector'].setdefault(si,{})['lightcolor']=0xf2c9af;tinted.append(si)
 # An explicitly authored fake floor changes rendering only. Physical void stays -224.
 vi=len(g['vertex']);sd0=len(g['sidedef']);si0=len(g['sector']);append=['// Inferno alpha bases: visual floor only; original damage/collision floor stays -224.']
 for x,y in [(30000,30000),(30000,30064),(30064,30064),(30064,30000)]:append.append(f'vertex {{ x={x}; y={y}; }}')
 append.append('sector { heightfloor=-128; heightceiling=1536; texturefloor="F_SKY1"; textureceiling="F_SKY1"; lightlevel=255; }')
 for i in range(4):
  append.append(f'sidedef {{ sector={si0}; texturemiddle="STARTAN3"; }}')
  append.append(f'linedef {{ v1={vi+i}; v2={vi+(i+1)%4}; sidefront={sd0+i}; blocking=true; '+('special=209; arg0=64123; arg1=34;' if i==0 else '')+' }')
 placed=[]
 def place(number,x,y,z,floor,args=''):
  placed.append(f'thing {{ type={number}; x={x:.6f}; y={y:.6f}; height={z-floor:.6f}; angle=0; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; coop=true; dm=true; {args} }}')
 folder=root/'tutnt/models/inferno/fade';folder.mkdir(parents=True,exist_ok=True);models=[];classes=[];defs=[]
 for i,((si,ns,raw),edges) in enumerate(sorted(groups.items())):
  a,b,c=edges[0];dx=b[0]-a[0];dy=b[1]-a[1];ln=math.hypot(dx,dy);ox=(a[0]+b[0])/2+dy/ln*4;oy=(a[1]+b[1])/2-dx/ln*4;oz=-128
  vs=[];uv=[];fs=[];normals=[]
  for a,b,c in edges:
   dx=b[0]-a[0];dy=b[1]-a[1];ln=math.hypot(dx,dy);nx=dy/ln;ny=-dx/ln;start=len(vs)
   # Top overlap sits slightly outside the original wall; fade begins below it.
   for t in (0,1):
    for z in (-120,-224):
     vs.append((a[0]+dx*t+nx*.04,a[1]+dy*t+ny*.04,z));uv.append(((t*ln*c['sx']+c['ox'])/c['width'],1-((c['ref']-z)*c['sy']+c['oy'])/c['height']));normals.append((nx,0,-ny))
   fs.extend([(start,start+2,start+1),(start+1,start+2,start+3)])
  name=f'wall_{si}_{ns}';cls='UTNTInfernoFade_'+str(i);skin='UFIROCK' if raw=='HOTROCK' else 'UFISTONE'
  out=['# Editable translucent continuation of original island walls.']+['v %.6f %.6f %.6f'%(x-ox,z-oz,-(y-oy)) for x,y,z in vs]+['vt %.8f %.8f'%q for q in uv]+['vn %.6f %.6f %.6f'%q for q in normals]+['f '+' '.join(f'{q+1}/{q+1}/{q+1}' for q in f) for f in fs]
  (folder/(name+'.obj')).write_text('\n'.join(out)+'\n',encoding='ascii')
  radius=math.ceil(max(math.hypot(x-ox,y-oy) for x,y,z in vs)+16)
  classes.append(f'class {cls} : UTNTInfernoFade {{ Default {{ RenderRadius {radius}; }} }}')
  models.append(f'Model {cls} {{ Path "models/inferno/fade/" Model 0 "{name}.obj" Skin 0 "{skin}" Scale 1 1 1.2 DontCullBackfaces FrameIndex SKED A 0 0 }}')
  defs.append(f' {25300+i} = {cls}');place(25300+i,ox,oy,oz,-224)
 assert len(groups)<100
 for x,y,z,si,kind,light in emit:place(25400,x,y,z,-224,f'arg0={kind}; arg1={int(light)};')
 for i in range(8):
  a=2*math.pi*i/8;place(25400,-1280+math.cos(a)*95,256+math.sin(a)*95,20+(i%3)*24,0,'arg0=1;')
 (root/'tutnt/zscript/inferno-fade-actors.zc').write_text('\n'.join(classes)+'\n',encoding='utf-8')
 (root/'tutnt/modeldef/MODELDEF.inferno-fade').write_text('\n'.join(models)+'\n',encoding='utf-8')
 (root/'tutnt/mapinfo/MAPINFO.inferno-fade').write_text('DoomEdNums {\n'+'\n'.join(defs)+'\n 25400 = UTNTInfernoEmitter\n}\n',encoding='utf-8')
 texturedefs=[]
 for raw,alias in [('HOTROCK','UFIROCK'),('HOTSTONE','UFISTONE')]:
  w,h=variants[raw]['logical'];texturedefs.append(f'Texture {alias}, {w}, {h} {{ Patch {raw}, 0, 0 }}')
 (root/'tutnt/textures/definitions/TEXTURES.inferno-fade').write_text('\n'.join(texturedefs)+'\n',encoding='utf-8')
 for name,line in [('MODELDEF.txt','#include "modeldef/MODELDEF.inferno-fade"'),('MAPINFO.txt','include "mapinfo/MAPINFO.inferno-fade"'),('textures/definitions/TEXTURES.base','#include "textures/definitions/TEXTURES.inferno-fade"')]:
  f=root/'tutnt'/name;s=f.read_text(encoding='utf-8');assert line not in s;f.write_text(s+'\n'+line+'\n',encoding='utf-8')
 text=edit_text(l['TEXTMAP'].decode(),changes,'\n'.join(append+placed)+'\n');magic,entries=read_wad(p)
 atomic_write(p,write_wad(magic,[(n,text.encode() if n.rstrip(b'\0')==b'TEXTMAP' else d) for n,d in entries]))
 work=root/'tutnt/.codex/work/tnt04b-inferno-finish';out=work/'nodes.wad'
 run=subprocess.run(['F:/DoomDev/Tools/UltimateDoombuilder/Compilers/Nodebuilders/zdbsp.exe','-q','-X','-g','-o',str(out),str(p)],capture_output=True);assert run.returncode==0,run.stdout+run.stderr
 # UDMF authored text must not change/reindex during node compilation.
 mm,ee=read_wad(out);_,authored=parse(p);_,rebuilt=parse(out);assert authored==rebuilt
 atomic_write(p,write_wad(mm,[(n,text.encode() if n.rstrip(b'\0')==b'TEXTMAP' else d) for n,d in ee]));print(json.dumps({'tinted_sectors':len(tinted),'fade_models':len(groups),'emitters':len(emit)+8,'lights':sum(v[-1] for v in emit)}))
if __name__=='__main__':author()
