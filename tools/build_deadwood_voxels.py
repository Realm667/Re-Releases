"""Build the approved stationary deadwood KVX models from native sprite patches.

Called by build_voxels.py, including its non-mutating --check workflow.
The 24 bindings cover 18 designs and six original frozen size variants.
"""
from pathlib import Path
import re, json, hashlib, struct
import numpy as np

def generate(root, output):
 from build_voxels import patch, encode, inspect_kvx
 from deadwood_voxel_geometry import geometry as organic
 R=Path(root);PAL=(R/"tutnt/PLAYPAL.pal").read_bytes()[:768]
 out=R/'tutnt/voxels';records=[];defs=[]
 text=(R/'tutnt/textures/definitions/TEXTURES.deadwood').read_text()
 matches=re.findall(r'Sprite (DW\w+), (\d+), (\d+)\s*\{\s*Offset (\d+), (\d+)\s*XScale ([\d.]+)\s*YScale ([\d.]+)\s*Patch "([^"]+)"',text)
 expected={prefix+frame+"0" for prefix in ("DWDT","DWDS","DWCT","DWCS","DWFT","DWFS","DWIT","DWIS") for frame in "ABC"}
 if len(matches)!=24 or {m[0] for m in matches}!=expected:
  raise ValueError("Deadwood TEXTURES must cover all 24 approved sprite views")
 cache={}
 for sprite,ww,hh,ll,tt,xscale,yscale,rel in matches:
  if float(xscale)!=float(yscale):raise ValueError("Expected uniform deadwood sprite scale: "+sprite)
  source=R/'tutnt'/rel;raw=source.read_bytes();w,h,left,top,p=patch(raw)
  if (w,h,left,top)!=(int(ww),int(hh),int(ll),int(tt)):
   raise ValueError('Deadwood sprite dimensions or anchors differ from patch: '+sprite)
  key=source.stem
  if key not in cache:
   cache[key]=organic(p,w,h,left,key,PAL,root=R)
  vox,dims,pivot=cache[key]
  scale=1/float(yscale)
  expected_front=p
  if abs(scale-1)>1e-6:
   # Resample occupied integer cells, including transparency, at cell centers.
   # This preserves the authored frozen view dimensions with unit runtime scale.
   original_dims=dims;dims=tuple(round(n*scale) for n in dims)
   pivot=tuple(round(n*scale) for n in pivot)
   source_grid=np.full(original_dims,-1,np.int16)
   for q,c in vox.items():source_grid[q]=c
   maps=[np.clip(np.floor((np.arange(n)+.5)/scale).astype(int),0,original_dims[i]-1) for i,n in enumerate(dims)]
   target=source_grid[np.ix_(*maps)];occupied=np.argwhere(target>=0)
   vox={tuple(map(int,q)):int(target[tuple(q)]) for q in occupied}
   expected_front={(x,z):p[int(sx),int(sz)] for x,sx in enumerate(maps[0]) for z,sz in enumerate(maps[2]) if (int(sx),int(sz)) in p}
   rays={}
   for x,y,z in vox:rays[x,z]=max(rays.get((x,z),y),y)
   for (x,z),c in expected_front.items():
    if (x,z) in rays:y=rays[x,z]
    else:
     source_y=int(np.flatnonzero(source_grid[maps[0][x],:,maps[2][z]]>=0)[-1])
     y=int(np.clip(round((source_y+.5)*scale-.5),0,dims[1]-1))
    vox[x,y,z]=c
  name='DV'+sprite[:-1];data=encode(vox,dims,pivot,PAL);inspect_kvx(data)
  front=decode_front(data)
  missing=set(expected_front)-set(front);extra=set(front)-set(expected_front)
  wrong=sum(front[k]!=c for k,c in expected_front.items() if k in front)
  if missing or extra or wrong:raise ValueError('Exported KVX front mismatch: '+sprite)
  output(out/(name+'.kvx'),data)
  defs.append(f'{sprite[:-1]} = "{name}" {{ OverridePalette Spin = 0 }}')
  records.append({'sprite':sprite,'source':rel,'source_sha256':hashlib.sha256(raw).hexdigest(),'model':name+'.kvx','size':dims,'pivot':pivot,'solid_voxels':len(vox),'runtime_scale':1,'spin':0,'sha256':hashlib.sha256(data).hexdigest(),'front_missing_pixels':len(missing),'front_extra_pixels':len(extra),'front_wrong_indices':wrong,'front_reference':'native patch' if abs(scale-1)<1e-6 else 'cell-center resampled authored view','palette_sha256':hashlib.sha256(PAL).hexdigest()})
  print(sprite,dims,len(vox),flush=True)
 output(R/'tools/artwork/deadwood/voxel-manifest.json',(json.dumps(records,indent=2)+'\n').encode())
 return defs


def decode_front(data):
 """Independently project actual exported KVX slabs, not the authoring grid."""
 _,xs,ys,zs,*_=struct.unpack_from('<7i',data);start=28
 xo=struct.unpack_from('<'+'I'*(xs+1),data,start);front={}
 for x in range(xs):
  yo=struct.unpack_from('<'+'H'*(ys+1),data,start+(xs+1)*4+x*(ys+1)*2)
  for y in reversed(range(ys)):
   at=start+xo[x]+yo[y];stop=start+xo[x]+yo[y+1]
   while at<stop:
    z,n,flags=data[at:at+3]
    for i,c in enumerate(data[at+3:at+3+n]):front.setdefault((x,z+i),c)
    at+=3+n
 return front
