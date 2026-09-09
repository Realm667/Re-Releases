"""Validate the cosmic sky's shared comet source, registrations and all cube edges."""
from pathlib import Path
import argparse,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent

def verify(root):
 out=root/'tutnt';shared=(root/'tools/war-comets.glsl').read_text();edges={};counts=0
 for face in 'NESWUD':
  shader=(out/f'shaders/rift/sky-{face}.fp').read_text()
  assert shader.startswith(shared+'\n'),face+' uses a different comet implementation'
  assert '@RAY@' not in shader
  for other in ['caldera-war','ash']:
   assert (out/f'shaders/{other}/sky-{face}.fp').read_text().startswith(shared+'\n')
  im=np.asarray(Image.open(out/f'textures/URF{face}.png').convert('RGB'),dtype=int);n=im.shape[0];assert im.shape==(1024,1024,3)
  for row,col in [(0,i) for i in range(n)]+[(n-1,i) for i in range(n)]+[(i,0) for i in range(n)]+[(i,n-1) for i in range(n)]:
   s=1-2*col/(n-1);t=1-2*row/(n-1)
   rays={'N':(s,t,-1),'E':(-1,t,-s),'S':(-s,t,1),'W':(1,t,s),'U':(s,1,-t),'D':(s,-1,-t)}
   key=tuple(round(v,7) for v in rays[face]);edges.setdefault(key,[]).append(im[row,col]);counts+=1
 error=max(int(np.max(np.max(v,axis=0)-np.min(v,axis=0))) for v in edges.values())
 assert all(len(v)>=2 for v in edges.values());assert error<=1,error
 for f,line in [('GLDEFS.txt','#include "GLDEFS.rift"'),('zscript.zc','#include "zscript/UTNT_RiftSky.zc"'),('MAPINFO.txt','AddEventHandlers = "UTNTRiftSkyHandler"')]:assert (out/f).read_text().count(line)==1
 handler=(out/'zscript/UTNT_RiftSky.zc').read_text();assert 'level.MapName~=="TNT04CN"' in handler
 return dict(ok=True,cube_edges=12,maximum_edge_error=error,shared_comet_faces=18,edge_samples=counts)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);a=p.parse_args();print(json.dumps(verify(a.root),indent=2))
