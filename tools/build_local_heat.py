"""Derive local lava heat volumes from rendered UDMF floors and wall pieces.
No WAD edits. Runtime uses a bounded pool of invisible cosmetic anchors.
"""
from pathlib import Path
import json, math, hashlib
from build_lava_lips import parse, tex, height, FLOORS, FALLS
from build_environment_fx import geometry, bounds, inside, center
ROOT=Path(__file__).resolve().parent.parent
LAVA=set(FLOORS+FALLS+('QLAVA3','LAVA1','FIRELAVA','FIRELAV2'))

def distance_edge(p,a,b):
 dx,dy=b[0]-a[0],b[1]-a[1];d=dx*dx+dy*dy
 t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/d)) if d else 0
 return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)

def detect(b):
 edges=geometry(b);rows=[]
 controls={int(b['sidedef'][int(l['sidefront'])]['sector']) for l in b['linedef'] if int(l.get('special',0)) in (160,209) and int(l.get('sidefront',-1))>=0}
 def add(kind,si,part,texture,p,r):
  rows.append([kind,si,part,texture,*[round(v,3) for v in (*p,*r)]])
 # Resolve 3D-floor control sectors to the actual tagged receiver polygons.
 # Their top texture and ceiling plane describe the visible lava surface.
 tops={}
 for l in b['linedef']:
  if int(l.get('special',0))!=160 or int(l.get('sidefront',-1))<0:continue
  control=int(b['sidedef'][int(l['sidefront'])]['sector']);s=b['sector'][control]
  texture=tex(s,'textureceiling')
  if texture not in LAVA:continue
  if int(l.get('arg3',0))<=0 or int(l.get('arg1',0))&3==0:continue
  tag=int(l.get('arg0',0))
  for si,receiver in enumerate(b['sector']):
   tags={int(receiver.get('id',0)),*[int(v) for v in str(receiver.get('moreids','')).strip('"').split() if v.lstrip('-').isdigit()]}
   if tag and tag in tags:tops.setdefault(si,set()).add((control,texture))
 def floor_sources(si,es,kind,part,texture):
  x0,y0,x1,y1=bounds(es);nx=max(1,math.ceil((x1-x0)/160));ny=max(1,math.ceil((y1-y0)/160))
  points=[(x0+(x+.5)*(x1-x0)/nx,y0+(y+.5)*(y1-y0)/ny) for y in range(ny) for x in range(nx)]+[center(es)]
  candidates=[]
  for p in points:
   if not inside(p,es):continue
   radius=min(384,min(distance_edge(p,a,c) for a,c,*_ in es))
   if radius>=8:candidates.append((radius,p))
  # Prefer broad interior plumes; retain small volumes along irregular shores.
  placed=[]
  for radius,p in sorted(candidates,reverse=True):
   if any(math.dist(p,q)<max(radius,r)*.72 for r,q in placed):continue
   placed.append((radius,p));vertical=min(96,max(30,radius*.30))
   add(kind,si,part,texture,(*p,vertical),(radius,radius,vertical))
 for si,s in enumerate(b['sector']):
  if si not in edges or si in controls:continue
  floor=tex(s,'texturefloor');es=edges[si]
  if floor in LAVA:floor_sources(si,es,0,0,floor)
  # Coincident decorative/liquid tops must not duplicate a whole lake.
  seen=set()
  for control,texture in sorted(tops.get(si,())):
   plane=tuple((k,v) for k,v in sorted(b['sector'][control].items()) if k=='heightceiling' or k.startswith('ceilingplane_'))
   if (plane,texture) in seen:continue
   seen.add((plane,texture));floor_sources(si,es,2,control,texture)
  for a,c,li,side in es:
   length=math.dist(a,c)
   if length<8:continue
   sd=b['sidedef'][side];l=b['linedef'][li]
   otherid=int(l.get('sideback' if int(l.get('sidefront',-1))==side else 'sidefront',-1))
   other=b['sector'][int(b['sidedef'][otherid]['sector'])] if otherid>=0 else None
   tangent=((c[0]-a[0])/length,(c[1]-a[1])/length);normal=(tangent[1],-tangent[0])
   for part,key in [(0,'texturetop'),(1,'texturemiddle'),(2,'texturebottom')]:
    texture=tex(sd,key)
    if texture not in LAVA:continue
    for x in range(max(1,math.ceil(length/160))):
     n=max(1,math.ceil(length/160));p=(a[0]+(x+.5)*(c[0]-a[0])/n,a[1]+(x+.5)*(c[1]-a[1])/n)
     f=height(s,p);ceiling=float(s.get('heightceiling',128))
     if part==0:
      if other is None:continue
      low,high=float(other.get('heightceiling',128)),ceiling
     elif part==2:
      if other is None:continue
      low,high=f,height(other,p)
     else:low,high=(max(f,height(other,p)),min(ceiling,float(other.get('heightceiling',128)))) if other else (f,ceiling)
     if high-low<12:continue
     depth=min(32,length/4);q=(p[0]+normal[0]*depth,p[1]+normal[1]*depth)
     if not inside(q,es):continue
     nz=max(1,math.ceil((high-low)/128));width=min(112,length/n*.65)
     radius=(max(12,abs(tangent[0])*width+abs(normal[0])*depth),max(12,abs(tangent[1])*width+abs(normal[1])*depth),min(80,(high-low)/nz*.55))
     for z in range(nz):add(1,side,part,texture,(*q,low+(z+.5)*(high-low)/nz-f),radius)
 return rows

def generate(root=ROOT,check=False):
 root=Path(root);manifest={};outputs={}
 for path in sorted((root/'tutnt/maps').glob('*.wad')):
  b=parse(path)
  if not b['sector']:continue
  rows=detect(b);name=path.stem.upper()
  outputs[f'tutnt/environment/{name}-heat.txt']=''.join('|'.join(map(str,r))+'\n' for r in rows)
  manifest[name]={'floor_volumes':sum(r[0]==0 for r in rows),'wall_volumes':sum(r[0]==1 for r in rows),'lava_3d_floor_volumes':sum(r[0]==2 for r in rows),'geometry_sha256':hashlib.sha256(json.dumps(b,sort_keys=True).encode()).hexdigest()}
 outputs['tools/local-heat-manifest.json']=json.dumps(manifest,indent=2)+'\n'
 uniforms='Uniform vec4 sourceDelta Uniform vec4 sourceRadius Uniform vec3 rayForward Uniform vec3 rayRight Uniform vec3 rayUp Uniform vec4 viewRect Uniform vec4 depthA Uniform vec4 depthB'
 outputs['tutnt/environment/local-heat.gldefs']=''.join('HardwareShader PostProcess scene { Name "UTNTLocalHeat%d" Shader "shaders/environment/local-heat.fp" 330 %s }\n'%(i,uniforms) for i in range(6))
 for name,data in outputs.items():
  path=root/name
  if path.exists() and path.read_bytes()==data.encode():continue
  if check:raise RuntimeError('Stale local heat data: '+name)
  path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data.encode())
 return manifest

if __name__=='__main__':
 import sys
 print(json.dumps(generate(check='--check' in sys.argv),indent=2))
