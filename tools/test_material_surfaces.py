"""Source landmarks, family phases and unchanged material protection."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from build_organic_materials import ROOT,height_depth,relief
from material_surface_geometry import NAMES

# Source-pixel points: solid face followed by the actual recess.
LANDMARKS=[('CITYF17',(8,8),(8,16)),('CITYF18',(24,16),(16,24)),
 ('CITYF17',(40,8),(32,8)),('CITYF18',(40,40),(40,48)),
 ('FLOOR4',(12,14),(12,8)),('FLOOR4',(32,30),(32,32)),
 ('SFLOOR1',(15,30),(8.5,30)),('SFLOOR1',(26,32),(20.5,32)),
 ('ADEL_G01',(30,60),(43.5,60)),('ADEL_F71',(30,30),(43.5,30)),
 ('ADEL_F67',(18,12),(24,24)),('ADEL_F68',(45,12),(39,24)),
 ('OBR09',(30,30),(30,64)),('OBR09',(4,15),(30,15)),
 ('OBR10',(16,117),(22,117)),('OBR10',(22,122),(32,122)),
 ('OBR04',(3,3),(7,7)),('OBR04',(7,7),(16,7)),
 ('ADEL_G02',(32,30),(18,30)),('ADEL_G03',(32,55),(18,55)),
 ('ADEL_G04',(30,8),(30,60))]


def check():
 g=json.loads((ROOT/'tools/organic-materials/generated.json').read_text());fields={};report=[]
 for n in sorted(NAMES):
  v=g['variants'][n];a=np.array(Image.open(ROOT/'tutnt'/(v['stem']+'-height.png')))
  z=-height_depth(a)*v['depth'];fields[n]=z
  assert -2<=z.min()<0 and 0<=z.max()<=2.3,n
  assert (a==127).any(),n
  dx=(np.roll(z,-1,1)-np.roll(z,1,1))*.5*z.shape[1]/v['logical'][0]
  dy=(np.roll(z,-1,0)-np.roll(z,1,0))*.5*z.shape[0]/v['logical'][1]
  normal=np.stack([-dx,dy,np.ones_like(z)],2);normal/=np.linalg.norm(normal,axis=2)[:,:,None]
  expected=np.clip((normal*.5+.5)*255,0,255).astype(np.uint8)
  actual=np.array(Image.open(ROOT/'tutnt'/(v['stem']+'-normal.png')))
  assert abs(expected.astype(int)-actual.astype(int)).max()<=1,n
  if n!='QFLAT06':
   m=next(m for m in g['materials'] if m['name']==n);w,h=v['size']
   a,_=relief(np.zeros((h,w,3),np.uint8),m['profile'],m['depth'],v['logical'],m['height_detail'])
   b,_=relief(np.full((h,w,3),255,np.uint8),m['profile'],m['depth'],v['logical'],m['height_detail'])
   assert np.array_equal(a,b),n
  report.append(dict(name=n,min=float(z.min()),max=float(z.max()),neutral_fraction=float((a==127).mean())))
 def at(n,p):
  z=fields[n];x,y=p;w,h=g['variants'][n]['size'];return float(z[min(int(y*z.shape[0]/h),z.shape[0]-1),min(int(x*z.shape[1]/w),z.shape[1]-1)])
 for n,front,back in LANDMARKS:
  assert at(n,front)>at(n,back)+.12,(n,front,back,at(n,front),at(n,back))
 assert np.array_equal(fields['CITYF17'],fields['CITYF18'])
 assert np.array_equal(fields['ADEL_F68'],fields['ADEL_F67'][:,::-1])
 # Compare exposed wood after undoing the source artwork's 32-pixel phase.
 for n in ('ADEL_G02','ADEL_G03'):
  assert np.allclose(np.roll(fields[n],-64,axis=1)[200:208],fields['ADEL_G01'][200:208],atol=.025),n
 assert np.allclose(fields['ADEL_G04'][40:200],fields['ADEL_G01'][40:200],atol=.025)
 assert np.array_equal(fields['OBR09'][:128],fields['OBR09'][128:])
 before=ROOT/'tutnt/.codex/work/material-next-pass/before-manifest.json'
 unchanged=0
 if before.exists():
  old=json.loads(before.read_text())
  for n,v in old['variants'].items():
   if v['family'] in NAMES:continue
   new=g['variants'][n]
   for suffix in ('-height.png','-normal.png'):
    key='tutnt/'+v['stem']+suffix;newkey='tutnt/'+new['stem']+suffix
    assert old['outputs'][key]==g['outputs'][newkey],n
   unchanged+=1
 r=dict(ok=True,materials=len(NAMES),landmarks=len(LANDMARKS),unchanged_variants=unchanged,data=report)
 out=ROOT/'tutnt/.codex/validation/material-next-pass';out.mkdir(exist_ok=True)
 (out/'data.json').write_text(json.dumps(r,indent=2));return r

if __name__=='__main__':
 r=check();print(json.dumps({k:v for k,v in r.items() if k!='data'}))
