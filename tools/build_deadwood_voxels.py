"""Build the approved stationary deadwood KVX models from native sprite patches.

Called by build_voxels.py, including its non-mutating --check workflow.
The 24 bindings cover 18 designs and six original frozen size variants.
"""
from pathlib import Path
import re, json, hashlib

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
  key=source.stem
  if key not in cache:
   cache[key]=organic(p,w,h,left,key,PAL)
  vox,dims,pivot=cache[key]
  scale=1/float(yscale)
  if abs(scale-1)>1e-6:
   # Existing IceyStub and frozen BigTree views have 33/124-unit grids.
   # Bake their authored dimensions into integer cells; runtime Scale stays 1.
   dims=tuple(round(n*scale) for n in dims);pivot=tuple(round(n*scale) for n in pivot)
   vox={tuple(min(dims[i]-1,round(k[i]*scale)) for i in range(3)):c for k,c in vox.items()}
  name='DV'+sprite[:-1];data=encode(vox,dims,pivot,PAL);inspect_kvx(data)
  output(out/(name+'.kvx'),data)
  defs.append(f'{sprite[:-1]} = "{name}" {{ OverridePalette Spin = 0 }}')
  records.append({'sprite':sprite,'source':rel,'source_sha256':hashlib.sha256(raw).hexdigest(),'model':name+'.kvx','size':dims,'pivot':pivot,'solid_voxels':len(vox),'runtime_scale':1,'spin':0,'sha256':hashlib.sha256(data).hexdigest()})
  print(sprite,dims,len(vox),flush=True)
 output(R/'tools/artwork/deadwood/voxel-manifest.json',(json.dumps(records,indent=2)+'\n').encode())
 return defs
