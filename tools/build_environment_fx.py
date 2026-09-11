"""Generate map-derived surface bindings without rewriting any WAD.

Per-face metadata shares shader programs across textures. Rain exposure remains
a runtime trace against the actual geometry, including solid 3D floors.
"""
from pathlib import Path
import collections, hashlib, json, math, re, struct
from PIL import Image
from build_lava_lips import parse,tex,point,height
ROOT=Path(__file__).resolve().parent.parent
MOD=ROOT/'tutnt'

def blocks(text,pattern):
 for m in re.finditer(pattern,text,re.I):
  a=text.find('{',m.end());depth=1;b=a+1
  while depth and b<len(text):
   if text[b]=='{':depth+=1
   if text[b]=='}':depth-=1
   b+=1
  yield m,text[a+1:b-1]

def things(path):
 d=path.read_bytes();_,n,o=struct.unpack_from('<4sII',d)
 for i in range(n):
  a,s,k=struct.unpack_from('<II8s',d,o+i*16)
  if k.rstrip(b'\0')==b'TEXTMAP':t=d[a:a+s].decode();break
 return [dict(re.findall(r'(\w+)\s*=\s*([^;]+);',x)) for x in re.findall(r'\bthing\s*(?://[^\n]*\n\s*)?\{([^}]+)\}',t)]

def material_library():
 materials={};textures={};terrain={};files={}
 for p in MOD.glob('GLDEFS*'):
  if p.name=='GLDEFS.environment':continue
  for m,body in blocks(p.read_text(),r'\bmaterial\s+(?:flat|texture)\s+"?([\w.-]+)"?'):
   materials[m[1].upper()]=body
 for p in MOD.glob('TEXTURES*'):
  if not p.is_file():continue
  if p.name in ('TEXTURES.environment-generated','TEXTURES.environment'):continue
  for m,body in blocks(p.read_text(),r'\b(?:texture|flat|graphic)\s+"?([\w.-]+)"?\s*,\s*(\d+)\s*,\s*(\d+)'):
   textures[m[1].upper()]=(int(m[2]),int(m[3]),body)
 for folder in ['flats','textures','patches','graphics']:
  for p in (MOD/folder).rglob('*'):
   if p.is_file() and p.suffix.lower() in ('.png','.lmp'):files.setdefault(p.stem.upper(),p)
 for p in MOD.glob('TERRAIN*'):
  if p.name=='TERRAIN.environment':continue
  for a,b in re.findall(r'^\s*floor\s+(\S+)\s+(\S+)',p.read_text(),re.M):terrain[a.strip('"').upper()]=b
 return materials,textures,terrain,files

def geometry(b):
 edges=collections.defaultdict(list)
 for i,l in enumerate(b['linedef']):
  a,c=[point(b['vertex'][int(l[k])]) for k in ('v1','v2')]
  for face,key in enumerate(('sidefront','sideback')):
   side=int(l.get(key,-1))
   if side>=0:edges[int(b['sidedef'][side]['sector'])].append((c,a,i,side) if face else (a,c,i,side))
 return edges

def bounds(edges):
 pts=[p for e in edges for p in e[:2]]
 return (min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts))

def inside(p,edges):
 x,y=p;result=False
 for a,b,*_ in edges:
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:result=not result
 return result

def center(edges):
 x0,y0,x1,y1=bounds(edges);p=((x0+x1)/2,(y0+y1)/2)
 if inside(p,edges):return p
 for a,b,*_ in sorted(edges,key=lambda e:-math.dist(e[0],e[1])):
  d=math.dist(a,b)
  if d>0:
   p=((a[0]+b[0])/2+(b[1]-a[1])/d*8,(a[1]+b[1])/2-(b[0]-a[0])/d*8)
   if inside(p,edges):return p
 return p

def movement_tags(path):
 data=path.read_bytes();_,count,directory=struct.unpack_from('<4sII',data)
 result=set()
 for entry in range(count):
  offset,size,key=struct.unpack_from('<II8s',data,directory+entry*16)
  if key.rstrip(b'\0')!=b'SCRIPTS':continue
  script=data[offset:offset+size].decode('utf-8',errors='replace')
  script=re.sub(r'/\*.*?\*/|//[^\n]*','',script,flags=re.S)
  result.update(int(t) for t in re.findall(r'\b(?:Floor|Ceiling|Door|Plat|Stairs|Pillar)_[A-Za-z0-9_]+\s*\(\s*(\d+)\s*,',script) if int(t))
 return sorted(result)

def map_digest(path):
 # Hash only fields consumed by the environmental generator. In particular,
 # actor edits, bytecode and decorative midtextures on non-wet maps are unrelated.
 raw=parse(path);rain=[t for t in things(path) if t.get('type')=='19021']
 surfaces=bool(rain)
 geometry={
  'vertex':[{k:float(v.get(k,0)) for k in ('x','y')} for v in raw['vertex']],
  'sector':[{k:s[k] for k in s if k in ('heightfloor','heightceiling','texturefloor','textureceiling','lightlevel','id') or 'plane_' in k} for s in raw['sector']],
  'sidedef':[{k:s[k] for k in s if k=='sector' or surfaces and k.startswith('texture')} for s in raw['sidedef']],
  'linedef':[{k:int(l.get(k,-1 if k.startswith('side') else 0)) for k in ('v1','v2','sidefront','sideback','special','arg0','arg1','arg2','arg3','arg4')} for l in raw['linedef']]
 }
 data={'geometry':geometry,'movement_tags':movement_tags(path),
       'rain':[{k:t[k] for k in ('x','y','type')} for t in rain]}
 return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()

def dust_texture():
 from PIL.PngImagePlugin import PngInfo
 for variant in range(4):
  im=Image.new('RGBA',(96,96));pixels=[]
  for y in range(96):
   for x in range(96):
    dx=(x-47.5)/47.5;dy=(y-47.5)/47.5
    edge=max(0,1-dx*dx-dy*dy)**3
    cloud=.62+.18*math.sin(x*(.13+variant*.023)+math.sin(y*.19+variant))+.14*math.cos(y*.21+x*.11+variant*2)
    pixels.append((175,165,147,round(255*edge*cloud)))
  im.putdata(pixels);info=PngInfo();info.add(b'grAb',struct.pack('>ii',48,96))
  suffix='' if variant==0 else '-'+str(variant)
  path=MOD/f'graphics/environment/mechanism-dust{suffix}.png';path.parent.mkdir(parents=True,exist_ok=True)
  im.save(path,pnginfo=info)

def main():
 dust_texture()
 materials,textures,terrain,files=material_library();out=MOD/'environment';out.mkdir(exist_ok=True)
 shaders=MOD/'shaders/environment';shaders.mkdir(exist_ok=True)
 meta=MOD/'materials/environment';meta.mkdir(exist_ok=True)
 Image.new('RGB',(1,1),(128,128,255)).save(meta/'normal.png')
 Image.new('RGB',(1,1),(180,180,180)).save(meta/'specular.png')
 texdefs=[];gldefs=[];terraindefs=[];summary={};shader_cache={};snow_names=set();serial=0
 def shape(original):
  if original in textures:return textures[original]
  p=files.get(original)
  if not p:return None
  if p.suffix.lower()=='.png':
   with Image.open(p) as im:w,h=im.size
  else:
   raw=p.read_bytes()
   if len(raw)==4096:w=h=64
   else:w,h=struct.unpack_from('<HH',raw)
  return w,h,f'Patch "{p.relative_to(MOD).as_posix()}", 0, 0'
 def add(rows,kind,index,part,original,raw,origin,axis,w,h,base,nx,ny):
  nonlocal serial
  shp=shape(original)
  if not shp:return base
  if base+nx*ny>65000:raise RuntimeError('Environmental canvas capacity exceeded')
  alias=f'EV{serial:06d}';serial+=1
  tw,th,body=shp;texdefs.append(f'Texture "{alias}", {tw}, {th}\n{{\n{body}\n}}\n')
  terraindefs.append(f'floor {alias} {terrain.get(original,terrain.get(raw,"Solid"))}')
  if 'SNOW' in raw:snow_names.add(alias)
  original_material=materials.get(original,'')
  match=re.search(r'\bshader\s+"([^"]+)"',original_material,re.I)
  key=match[1] if match else ''
  if key not in shader_cache:
   src=(MOD/key).read_text() if key else ''
   if 'SetupMaterial' in src:
    src=src.replace('SetupMaterial','EnvironmentOriginal')+'\n'
    entry='EnvironmentOriginal(mat);'
   elif 'ProcessTexel' in src:
    src=src.replace('ProcessTexel','EnvironmentOriginalTexel')+'\n'
    entry='mat.Base=EnvironmentOriginalTexel();mat.Normal=normalize(vWorldNormal.xyz);'
   elif src:raise RuntimeError('Unsupported material entry '+key)
   else:entry='mat.Base=getTexel(vTexCoord.st);mat.Normal=normalize(vWorldNormal.xyz);'
   shared='combined-'+str(len(shader_cache))+'.fp';shader_cache[key]=shared
   common=(shaders/'surface.glsl').read_text()
   (shaders/shared).write_text(src+'\n'+common.replace('ENV_ORIGINAL_BODY',entry))
  residual=re.sub(r'\bshader\s+"[^"]+"','',original_material,flags=re.I)
  if not re.search(r'\bnormal\s',residual,re.I):residual+=' Normal "materials/environment/normal.png" Specular "materials/environment/specular.png" '
  gldefs.append(f'Material Texture "{alias}" {{ {residual}\n Shader "shaders/environment/{shader_cache[key]}" Texture envMeta "materials/environment/{alias}.png" Texture envState "UENVSTATE" }}')
  # Fixed-point data pixels, not artwork. NEAREST via texelFetch in the shader.
  values=[base,nx,ny,*[round((v+65536)*16) for v in origin],*[round((v+1)*32767) for v in axis],round(w*16),round(h*16),kind,0,0,1 if any(x in raw for x in ('METAL','PIPE','TEK','ECOP')) else 0,0]
  im=Image.new('RGB',(16,1));im.putdata([((v>>16)&255,(v>>8)&255,v&255) for v in values]);im.save(meta/(alias+'.png'))
  rows.append('|'.join(map(str,[kind,index,part,original,alias,base,*origin,*axis,w,h,nx,ny])))
  return base+nx*ny
 for path in sorted((MOD/'maps').glob('*.wad')):
  b=parse(path)
  if not b['sector']:continue
  name=path.stem.upper();edges=geometry(b);rows=[];base=0;mechanisms=[]
  aliases={}
  alignment=MOD/'areaalign'/f'{name}.txt'
  if alignment.exists():
   for line in alignment.read_text().splitlines():
    r=line.split('|')
    if r[0]=='F':aliases[(0,int(r[1]),int(r[2]))]=r[4]
    elif r[0] in ('W','P'):
     side=int(b['linedef'][int(r[1])].get('sidefront' if r[2]=='0' else 'sideback',-1));aliases[(1,side,int(r[3]))]=r[5]
  for i,s in enumerate(b['sector']):
   raw=tex(s,'texturefloor')
   if 'SNOW' in raw:snow_names.add(raw);snow_names.add(aliases.get((0,i,0),raw))
  anchors=[(float(t['x']),float(t['y'])) for t in things(path) if t.get('type')=='19021'] if name=='TNT02' else []
  def nearby(box):
   return any(max(box[0]-x,0,x-box[2])**2+max(box[1]-y,0,y-box[3])**2<240**2 for x,y in anchors)
  tags=collections.defaultdict(list)
  for i,s in enumerate(b['sector']):tags[int(s.get('id',0))].append(i)
  for li,l in enumerate(b['linedef']):
   special=int(l.get('special',0));tag=int(l.get('arg0',0));front=int(l.get('sidefront',-1));back=int(l.get('sideback',-1))
   if front<0:continue
   control=int(b['sidedef'][front]['sector']);ctrl=b['sector'][control]
   # Families: normal doors, floors, stairs, pillars, lifts and ceilings.
   if special in set(range(10,14))|set(range(20,41))|set(range(60,70))|set(range(200,208)):
    targets=tags[tag] if tag else ([int(b['sidedef'][back]['sector'])] if back>=0 else [])
    for si in targets:
     if si not in edges:continue
     p=center(edges[si]);raw=tex(b['sector'][si],'texturefloor')
     stone=not any(x in raw for x in ('METAL','TEK','PIPE','COMP'))
     mechanisms.append((si,*p,int(stone),tag if tag else 100000+si))
  # Discover ACS mechanisms as well as line actions.
  for tag in movement_tags(path):
   for si in tags[tag]:
    if si not in edges:continue
    p=center(edges[si]);raw=tex(b['sector'][si],'texturefloor')
    stone=not any(x in raw for x in ('METAL','TEK','PIPE','COMP'))
    mechanisms.append((si,*p,int(stone),tag))
  for si,s in enumerate(b['sector']):
   if si not in edges:continue
   box=bounds(edges[si]);raw=tex(s,'texturefloor');original=aliases.get((0,si,0),raw)
   wet=bool(anchors) and nearby(box)
   excluded=any(x in raw for x in ('LAVA','SLIME','WAT','SKY','TELE','LIGHT','TLITE','LITE','GRAS'))
   if wet and not excluded and box[2]>box[0] and box[3]>box[1]:
    nx=max(1,min(12,math.ceil((box[2]-box[0])/64)));ny=max(1,min(12,math.ceil((box[3]-box[1])/64)))
    base=add(rows,0,si,0,original,raw,(box[0],box[1],float(s.get('heightfloor',0))),(1,0,0),box[2]-box[0],box[3]-box[1],base,nx,ny)
   for a,c,li,side in edges[si]:
    # Wet bottom/mid/top pieces use actual per-side geometry, not texture-wide toggles.
    length=math.dist(a,c)
    if length<8:continue
    sd=b['sidedef'][side];l=b['linedef'][li];otherid=int(l.get('sideback' if int(l.get('sidefront',-1))==side else 'sidefront',-1));other=b['sector'][int(b['sidedef'][otherid]['sector'])] if otherid>=0 else None
    floor=float(s.get('heightfloor',0));ceiling=float(s.get('heightceiling',128))
    for part,key in [(0,'texturetop'),(1,'texturemiddle'),(2,'texturebottom')]:
     raw=tex(sd,key)
     if raw=='-' or any(x in raw for x in ('LAVA','SLIME','WAT','SKY','TELE','PORT','RUNE','RUNT','LIGHT','LITE','COMP','SW1','SW2')):continue
     if part==0:
      if other is None:continue
      z0=float(other.get('heightceiling',0));z1=ceiling
     elif part==2:
      if other is None:continue
      z0=floor;z1=float(other.get('heightfloor',0))
     else:
      z0=max(floor,float(other.get("heightfloor",floor))) if other else floor;z1=min(ceiling,float(other.get("heightceiling",ceiling))) if other else ceiling
     if z1-z0<4 or not wet:continue
     z1=min(z1,z0+512)
     if z1<=z0:continue
     nx=max(1,min(12,math.ceil(length/64)));ny=max(1,min(8,math.ceil((z1-z0)/64)))
     base=add(rows,1,side,part,aliases.get((1,side,part),raw),raw,(*a,z0),((c[0]-a[0])/length,(c[1]-a[1])/length,0),length,z1-z0,base,nx,ny)
  (out/f'{name}-surfaces.txt').write_text('\n'.join(rows)+'\n')
  (out/f'{name}-mechanisms.txt').write_text('\n'.join('|'.join(map(str,r)) for r in dict.fromkeys(mechanisms))+'\n')
  summary[name]={'surfaces':len(rows),'state_pixels':base,'mechanisms':len(set(mechanisms)),'geometry_sha256':map_digest(path)}
 for old in meta.glob('EV*.png'):
  if old.stem not in {f'EV{i:06d}' for i in range(serial)}:old.unlink()
 for old in shaders.glob('combined-*.fp'):
  if old.name not in shader_cache.values():old.unlink()
 (MOD/'TEXTURES.environment-generated').write_text('\n'.join(texdefs))
 (MOD/'TERRAIN.environment').write_text('// Alias terrain mappings are applied after all TERRAIN definitions.\n')
 (out/'terrain-aliases.txt').write_text('\n'.join(terraindefs)+'\n')
 (out/'material-bindings.gldefs').write_text('\n'.join(gldefs)+'\n')
 (out/'snowtextures.txt').write_text('|'+ '|'.join(sorted(snow_names))+'|')
 (ROOT/'tools/environment-manifest.json').write_text(json.dumps(summary,indent=2))
 # Keep generated text deterministic across platforms and clean in Git.
 for generated in [MOD/'TEXTURES.environment-generated',MOD/'TERRAIN.environment',*out.glob('*.txt'),*out.glob('*.gldefs'),*shaders.glob('combined-*.fp')]:
  text='\n'.join(line.rstrip() for line in generated.read_text().splitlines()).rstrip()
  generated.write_bytes((text+'\n' if text else '').encode('utf-8'))
 print(json.dumps({k:{a:b for a,b in v.items() if a!='geometry_sha256'} for k,v in summary.items()},indent=2))
def check(root=ROOT):
 manifest=json.loads((root/'tools/environment-manifest.json').read_text())
 for name,data in manifest.items():
  path=root/'tutnt/maps'/f'{name.lower()}.wad'
  if map_digest(path)!=data['geometry_sha256']:
   raise RuntimeError('Stale environmental bindings: run tools/build_environment_fx.py for '+name)
 return True

if __name__=='__main__':
 import sys
 if '--check' in sys.argv:check()
 else:main()
