"""Validate source landmarks, family construction and all pre-existing assets."""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from build_organic_materials import ROOT,height_depth,relief
from material_support_geometry import NAMES

# Independently read native artwork coordinates: front surface then recess.
LANDMARKS=[('CFLOOR2',(18,18),(31,18)),('CFLOOR2',(46,42),(46,32)),
 ('CFLOOR4',(39,8),(32,8)),('OBSUP1',(8,8),(8,16)),
 ('IKSUP5',(8,3),(8,7)),('QTECH17',(8,8),(8,16)),
 ('QTECH22',(44,45),(12,45)),('QTECH22',(57,35),(54,35)),
 ('OBR01',(30,8),(30,16.5)),('OBRL11',(20,35),(24,35)),
 ('OBRL11',(6.5,120),(10,120)),('QCITY07',(30,60),(30,61)),
 ('QCITY10',(30,7),(30,11)),('QCITY11',(30,66),(30,67)),
 ('IKWALL70',(64,64),(78,64))]


def check():
 g=json.loads((ROOT/'tools/organic-materials/generated.json').read_text());fields={};data=[]
 for n in sorted(NAMES):
  v=g['variants'][n];a=np.array(Image.open(ROOT/'tutnt'/(v['stem']+'-height.png')))
  z=-height_depth(a)*v['depth'];fields[n]=z
  assert -2.55<=z.min()<=0 and 0<=z.max()<=.9,n
  assert (a==127).any(),n
  dx=(np.roll(z,-1,1)-np.roll(z,1,1))*.5*z.shape[1]/v['logical'][0]
  dy=(np.roll(z,-1,0)-np.roll(z,1,0))*.5*z.shape[0]/v['logical'][1]
  normal=np.stack([-dx,dy,np.ones_like(z)],2);normal/=np.linalg.norm(normal,axis=2)[:,:,None]
  expected=np.clip((normal*.5+.5)*255,0,255).astype(np.uint8)
  actual=np.array(Image.open(ROOT/'tutnt'/(v['stem']+'-normal.png')))
  assert abs(expected.astype(int)-actual.astype(int)).max()<=1,n
  m=next(m for m in g['materials'] if m['name']==n);w,h=v['size']
  black,_=relief(np.zeros((h,w,3),np.uint8),m['profile'],m['depth'],v['logical'],m['height_detail'])
  white,_=relief(np.full((h,w,3),255,np.uint8),m['profile'],m['depth'],v['logical'],m['height_detail'])
  assert np.array_equal(black,white),n
  data.append(dict(name=n,min=float(z.min()),max=float(z.max()),neutral_fraction=float((a==127).mean())))
 def at(n,p):
  z=fields[n];x,y=p;w,h=g['variants'][n]['size'];return float(z[int(y*z.shape[0]/h),int(x*z.shape[1]/w)])
 for n,front,back in LANDMARKS:assert at(n,front)>at(n,back)+.12,(n,front,back,at(n,front),at(n,back))
 # Matching family geometry is checked in the actual encoded outputs.
 def other(n):
  v=g['variants'][n];return -height_depth(np.array(Image.open(ROOT/'tutnt'/(v['stem']+'-height.png'))))*v['depth']
 assert np.array_equal(fields['IKWALL70'],other('IKWALL73'))
 assert np.array_equal(fields['QTECH22'][38:238,:30],other('QTECH20')[38:238,:30])
 assert np.array_equal(fields['QTECH22'][38:238,226:],other('QTECH20')[38:238,226:])
 assert np.array_equal(fields['QCITY10'][:48],fields['QCITY11'][:48])
 assert np.array_equal(fields['QCITY07'][100:152],fields['QCITY11'][100:152])
 assert np.array_equal(fields['OBR01'][14:18],fields['OBRL11'][14:18])
 before=ROOT/'tutnt/.codex/work/material-support-pass/before-manifest.json'
 old=json.loads(before.read_text()) if before.exists() else {'variants':{}}
 for n,v in old['variants'].items():
  for suffix in ('-height.png','-normal.png'):
   assert old['outputs']['tutnt/'+v['stem']+suffix]==g['outputs']['tutnt/'+g['variants'][n]['stem']+suffix],n
 r=dict(ok=True,materials=len(NAMES),landmarks=len(LANDMARKS),unchanged_variants=len(old['variants']) if before.exists() else None,data=data)
 out=ROOT/'tutnt/.codex/validation/material-support-pass';out.mkdir(exist_ok=True)
 (out/'data.json').write_text(json.dumps(r,indent=2));return r

if __name__=='__main__':
 r=check();print(json.dumps({k:v for k,v in r.items() if k!='data'}))
