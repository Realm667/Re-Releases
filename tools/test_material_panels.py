"""Validate source landmarks, family construction and all pre-existing assets."""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from build_organic_materials import ROOT,height_depth,relief
from material_panel_geometry import NAMES

# Independently read native artwork coordinates: front surface then recess.
LANDMARKS=[('IKWALL73',(64,64),(78,64)),('IKWALL75',(102,64),(117,64)),
 ('IKFLAT2',(33,32),(41,32)),('IKFLAT4',(52,48),(59,48)),
 ('IKWALL76',(50,2),(50,5)),('IKWALL78',(50,126),(50,123)),
 ('NMTRC1',(28,16),(20.5,16)),('N_MTRC1',(28,80),(20.5,80)),
 ('NMTRC1',(7.5,11.5),(9.5,15)),('ADEL_F09',(23.5,19.5),(26,45)),
 ('ADEL_F36',(26,12),(30,12)),('ADEL_F36',(48,44),(51,44)),
 ('QDOOR1',(60,40),(20,40)),('QDOOR3',(60,90),(20,90)),
 ('QDOOR2',(30,22),(14,15)),('QDOOR4',(30,42),(14,34)),
 ('QDOOR5',(58,19),(55,19)),('QDOOR5',(30,30),(63.5,30)),
 ('QDOOR6',(8,50),(30,50)),('QDOOR7',(23,40),(14,40)),
 ('QDOOR8',(55,70),(64,70)),('QDOOR9',(65,42),(65,30)),
 ('QDOOR9',(62,80),(105,90)),('OIDOOR2',(40,35),(20,35)),
 ('OIDOOR2',(85,80),(103,80)),('OIDOOR2',(70,70),(64,64)),
 ('OSNOW2',(40,35),(20,35)),('OSNOW2',(21,71),(21,50))]


def check():
 g=json.loads((ROOT/'tools/organic-materials/generated.json').read_text());fields={};data=[]
 for n in sorted(NAMES):
  v=g['variants'][n];a=np.array(Image.open(ROOT/'tutnt'/(v['stem']+'-height.png')))
  z=-height_depth(a)*v['depth'];fields[n]=z
  assert -1.65<=z.min()<=0 and 0<=z.max()<=.85,n
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
 for a,b in [('IKWALL73','IKWALL74'),('IKWALL73','IKWALL75'),('IKWALL76','IKWALL78'),('IKFLAT2','IKFLAT4'),('QDOOR1','QDOOR3')]:
  assert np.array_equal(fields[a],fields[b]),(a,b)
 assert np.array_equal(fields['NMTRC2'],np.rot90(fields['NMTRC1']))
 assert np.array_equal(fields['N_MTRC1'][:128],fields['NMTRC1'])
 assert np.array_equal(fields['IKWALL73'][18:238],fields['IKWALL76'][18:238])
 a,b=fields['OIDOOR2'],fields['OSNOW2']
 assert np.all(b>=a-1e-5),'Snow must not erode its substrate'
 assert np.mean(a==b)>.92,'Winter variant changes unrelated metal'
 before=ROOT/'tutnt/.codex/work/material-panel-pass/before-manifest.json'
 old=json.loads(before.read_text()) if before.exists() else {'variants':{}}
 for n,v in old['variants'].items():
  for suffix in ('-height.png','-normal.png'):
   assert old['outputs']['tutnt/'+v['stem']+suffix]==g['outputs']['tutnt/'+g['variants'][n]['stem']+suffix],n
 r=dict(ok=True,materials=len(NAMES),landmarks=len(LANDMARKS),unchanged_variants=len(old['variants']) if before.exists() else None,data=data)
 out=ROOT/'tutnt/.codex/validation/material-panel-pass';out.mkdir(exist_ok=True)
 (out/'data.json').write_text(json.dumps(r,indent=2));return r

if __name__=='__main__':
 r=check();print(json.dumps({k:v for k,v in r.items() if k!='data'}))
