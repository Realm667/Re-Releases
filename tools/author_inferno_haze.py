"""Explicit authoring of TNT04B island-base haze. Never invoked by packaging.
Run once on the authored inferno map. Thereafter edit the Things/models directly.
"""
from pathlib import Path
import math
from collections import defaultdict
from test_caldera_structure import parse
from build_environment_fx import geometry
from build_utnt import read_wad,write_wad,atomic_write
ROOT=Path(__file__).resolve().parents[1]
def author(root=ROOT):
 p=root/'tutnt/maps/tnt04b.wad';l,g=parse(p);geo=geometry(g)
 assert b'Authored inferno haze' not in l['TEXTMAP'],'Already authored; preserve manual map edits.'
 assert not any(25200<=int(t['type'])<25400 for t in g['thing'])
 groups=defaultdict(list)
 for si in (1463,2227):
  assert float(g['sector'][si]['heightfloor'])==-224
  for a,b,li,sd in geo[si]:
   line=g['linedef'][li];other=int(line.get('sideback',-1)) if int(line['sidefront'])==sd else int(line['sidefront'])
   if other<0:continue
   ns=int(g['sidedef'][other]['sector']);h=float(g['sector'][ns]['heightfloor'])
   if h<=-200:continue
   groups[(si,ns)].append((a,b,min(-48,h-28)))
 normals=defaultdict(list)
 for (si,ns),edges in groups.items():
  for a,b,h in edges:
   dx=b[0]-a[0];dy=b[1]-a[1];ln=math.hypot(dx,dy);n=(dy/ln,-dx/ln)
   normals[(si,a)].append(n);normals[(si,b)].append(n)
 folder=root/'tutnt/models/inferno';folder.mkdir(parents=True,exist_ok=True)
 models=[];classes=['''// Authored, serialized cosmetic Things. No collision or gameplay changes.
class UTNTInfernoHaze : Actor {
 Default { +NOGRAVITY +NOINTERACTION +NOBLOCKMAP +DONTSPLASH +NOTONAUTOMAP
 Radius 1; Height 1; RenderStyle "Translucent"; Alpha .88; }
 States { Spawn: SKED A -1 Bright; Stop; }
 override void Tick() {}
}'''];defs=[];things=[]
 for i,((si,ns),edges) in enumerate(sorted(groups.items())):
  # Origin stays in the void for stable lighting, clipping and serialization.
  a,b,h=edges[0];dx=b[0]-a[0];dy=b[1]-a[1];ln=math.hypot(dx,dy);ox=(a[0]+b[0])/2+dy/ln*12;oy=(a[1]+b[1])/2-dx/ln*12;oz=-192
  verts=[];uv=[];faces=[]
  for a,b,h in edges:
   dx=b[0]-a[0];dy=b[1]-a[1];ln=math.hypot(dx,dy);nx=dy/ln;ny=-dx/ln
   ends=[]
   for pt in (a,b):
    m=normals[(si,pt)];sx=sum(v[0] for v in m);sy=sum(v[1] for v in m);d=math.hypot(sx,sy);ex=sx/d;ey=sy/d;den=max(.35,ex*nx+ey*ny);ends.append((ex/den,ey/den))
   segments=max(1,math.ceil(ln/64));start=len(verts)
   for k in range(segments+1):
    t=k/segments;x=a[0]+dx*t;y=a[1]+dy*t;nx=ends[0][0]*(1-t)+ends[1][0]*t;ny=ends[0][1]*(1-t)+ends[1][1]*t
    for j,(dist,v) in enumerate([(1,0),(8,.22),(30,.48),(65,.74),(110,1)]):
     z=-144-236*v
     verts.append((x+nx*dist,y+ny*dist,z));uv.append((t,v))
   for k in range(segments):
    for j in range(4):
     q=start+k*5+j;faces.extend([(q,q+1,q+5),(q+1,q+6,q+5)])
  name=f'base_{si}_{ns}';cls='UTNTInferno_'+name
  obj=['# Editable island-base mist surface; no collision.','s off']
  obj += ['v %.6f %.6f %.6f'%(x-ox,z-oz,-(y-oy)) for x,y,z in verts]
  obj += ['vt %.6f %.6f'%v for v in uv]
  obj += ['vn 0 1 0']
  obj += ['f '+' '.join(f'{q+1}/{q+1}/1' for q in face) for face in faces]
  (folder/(name+'.obj')).write_text('\n'.join(obj)+'\n',encoding='ascii')
  radius=math.ceil(max(math.hypot(x-ox,y-oy) for x,y,z in verts)+16)
  classes.append(f'class {cls} : UTNTInfernoHaze {{ Default {{ RenderRadius {radius}; }} }}')
  models.append(f'Model {cls} {{ Path "models/inferno/" Model 0 "{name}.obj" Skin 0 "UFIU" Scale 1 1 1.2 DontCullBackfaces FrameIndex SKED A 0 0 }}')
  # Dedicated skin uses the haze shader, not the sky projection.
  models[-1]=models[-1].replace('Skin 0 "UFIU"','Skin 0 "UFIHAZE"')
  defs.append(f' {25200+i} = {cls}')
  things.append(f'thing {{ x={ox:.6f}; y={oy:.6f}; height={oz+224}; angle=0; type={25200+i}; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; coop=true; dm=true; }}')
 (root/'tutnt/zscript/UTNT_Inferno.zc').write_text('\n'.join(classes)+'\n',encoding='utf-8')
 (root/'tutnt/modeldef/MODELDEF.inferno').write_text('\n'.join(models)+'\n',encoding='utf-8')
 (root/'tutnt/mapinfo/MAPINFO.inferno').write_text('DoomEdNums {\n'+'\n'.join(defs)+'\n}\n',encoding='utf-8')
 for name,line in [('zscript.zc','#include "zscript/UTNT_Inferno.zc"'),('MODELDEF.txt','#include "modeldef/MODELDEF.inferno"'),('MAPINFO.txt','include "mapinfo/MAPINFO.inferno"')]:
  f=root/'tutnt'/name;s=f.read_text();assert line not in s;f.write_text(s+'\n'+line+'\n',encoding='utf-8')
 text=l['TEXTMAP']+('\n// Authored inferno haze; edit Things/models freely.\n'+'\n'.join(things)+'\n').encode()
 magic,entries=read_wad(p);atomic_write(p,write_wad(magic,[(n,text if n.rstrip(b'\0')==b'TEXTMAP' else d) for n,d in entries]))
 print(f'Authored {len(groups)} haze Things, {sum(len(v) for v in groups.values())} island edges.')
if __name__=='__main__':author()
