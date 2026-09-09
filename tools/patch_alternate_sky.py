"""Add plain-ceiling SkyPickers to TNT04C's decorative room and final arena.

The original 770 pickers and three viewpoints are preserved byte-for-byte.
No vertices, lines, sectors, scripts or BSP lumps change. New things only select
portal 1 (plain sky); ClearPortal would incorrectly select default viewpoint 0.
"""
from pathlib import Path
import re,math,collections,argparse
from build_utnt import read_wad,write_wad,atomic_write
from test_caldera_structure import parse
ROOT=Path(__file__).resolve().parent.parent
MARK='// TNT04C alternate sky: plain ceiling pickers'

def patch(path):
 magic,entries=read_wad(path);lumps,g=parse(path)
 source=lumps['TEXTMAP'].decode()
 if MARK in source:return 0
 edges=collections.defaultdict(list)
 for line in g['linedef']:
  for key in ('sidefront','sideback'):
   if key in line:
    sec=int(g['sidedef'][int(line[key])]['sector'])
    edges[sec].append(tuple((float(g['vertex'][int(line[k])]['x']),float(g['vertex'][int(line[k])]['y'])) for k in ('v1','v2')))
 def inside(sec,x,y):
  hit=False
  for (ax,ay),(bx,by) in edges[sec]:
   if (ay>y)!=(by>y) and x<(bx-ax)*(y-ay)/(by-ay)+ax:hit=not hit
  return hit
 targets=[]
 for i,s in enumerate(g['sector']):
  if s.get('textureceiling')=='"STARSKY1"' or (s.get('textureceiling')=='"F_SKY1"' and min(p[1] for e in edges[i] for p in e)>11000):targets.append(i)
 assert len(targets)==87,len(targets)
 additions=[MARK]
 for i in targets:
  candidates=[]
  for (ax,ay),(bx,by) in edges[i]:
   dx,dy=bx-ax,by-ay;length=math.hypot(dx,dy)
   if length<1:continue
   for sign in (1,-1):
    x=round((ax+bx)/2-sign*dy/length*.25,5);y=round((ay+by)/2+sign*dx/length*.25,5)
    if inside(i,x,y):candidates.append((x,y))
  assert candidates,i
  x,y=candidates[0]
  additions.append(f'''thing // plain ceiling for sector {i}
{{
x = {x};
y = {y};
type = 9081;
arg0 = 0;
arg1 = 1;
skill1 = true;
skill2 = true;
skill3 = true;
skill4 = true;
skill5 = true;
single = true;
coop = true;
dm = true;
}}''')
 text=(source+'\n'+'\n\n'.join(additions)+'\n').encode()
 atomic_write(path,write_wad(magic,[(n,text if n.rstrip(b'\0')==b'TEXTMAP' else d) for n,d in entries]))
 return len(targets)

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--map',type=Path,default=ROOT/'tutnt/maps/tnt04c.wad');a=p.parse_args();print('Added ceiling SkyPickers:',patch(a.map))
