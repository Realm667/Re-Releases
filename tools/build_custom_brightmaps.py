"""Build selective, native-pixel brightmaps for UTNT's remaining emissive art.

No resampling, blur, painted diffuse pixels or changes to release masks.
Requires Pillow and NumPy. --check reproduces outputs without writing.
"""
from pathlib import Path
from functools import lru_cache
import argparse,hashlib,io,json,re,struct
import numpy as np
from PIL import Image
from build_organic_materials import texture_defs

ROOT=Path(__file__).resolve().parents[1]
PREFIXES='DRKI APYT SLHV SLHW HWAR TORT RSPI TROX HFRY PLEM TRO2 MNTR MNTS CYCL MPOS HLGD ENCD REGN PHRT'.split()
SURFACES='NEUESDI IKLITF01 IKLITF07 TLITE6_1 TLITE6_5 QRUNT62 QRUNT63 TELETOP COMPBLUE COMPRED SW1NEW1 SW2NEW1 SW1NEW3 SW2NEW3 XA40TEX XB40TEX'.split()
MODULE='gldefs/GLDEFS.brightmaps-custom'
OUT='materials/brightmaps/custom'
def sha(data):return hashlib.sha256(data).hexdigest()
def png(image):
 b=io.BytesIO();image.save(b,format='PNG',optimize=True);return b.getvalue()

class Artwork:
 def __init__(self,root,iwad):
  self.root=Path(root);self.mod=self.root/'tutnt';self.iwad=Path(iwad);self.inputs={}
  self.palette=np.frombuffer(self.read(self.mod/'PLAYPAL.pal')[:768],np.uint8).reshape(256,3)
  self.paths={}
  for folder in ('sprites','patches','flats','textures'):
   for p in sorted((self.mod/folder).rglob('*')):
    if p.is_file() and p.suffix.lower() in ('.png','.lmp'):self.paths.setdefault(p.stem.upper(),p)
  self.defs=texture_defs(self.mod)
  for p in [self.mod/'TEXTURES.txt',*sorted((self.mod/'textures/definitions').glob('TEXTURES*'))]:
   if p.is_file():self.read(p)
  data=self.iwad.read_bytes();count,off=struct.unpack_from('<II',data,4)
  self.lumps={}
  for i in range(count):
   pos,size,name=struct.unpack_from('<II8s',data,off+16*i);self.lumps[name.rstrip(b'\0').decode().upper()]=data[pos:pos+size]
  pn=self.lump('PNAMES');names=[pn[4+i*8:12+i*8].rstrip(b'\0').decode() for i in range(struct.unpack_from('<I',pn)[0])]
  for ln in ('TEXTURE1','TEXTURE2'):
   if ln not in self.lumps:continue
   tx=self.lump(ln)
   for i in range(struct.unpack_from('<I',tx)[0]):
    pos=struct.unpack_from('<I',tx,4+4*i)[0];name=tx[pos:pos+8].rstrip(b'\0').decode();w,h=struct.unpack_from('<HH',tx,pos+12);n=struct.unpack_from('<H',tx,pos+20)[0];parts=[]
    for j in range(n):
     x,y,idx=struct.unpack_from('<hhH',tx,pos+22+10*j);parts.append((names[idx],x,y))
    self.defs.setdefault(name,(w,h,[1,1],parts))
 def read(self,path):
  data=path.read_bytes();self.inputs[path.relative_to(self.root).as_posix()]=sha(data);return data
 def lump(self,name):
  data=self.lumps[name];self.inputs['DOOM2.WAD:'+name]=sha(data);return data
 def decode(self,data,flat=False):
  if data.startswith(b'\x89PNG'):return Image.open(io.BytesIO(data)).convert('RGBA')
  if flat:
   n=int(len(data)**.5);return Image.fromarray(self.palette[np.frombuffer(data,np.uint8).reshape(n,n)]).convert('RGBA')
  w,h=struct.unpack_from('<HH',data);a=np.zeros((h,w,4),np.uint8)
  for x in range(w):
   off=struct.unpack_from('<I',data,8+4*x)[0];last=-1
   while data[off]!=255:
    top,n=data[off:off+2]
    if top<=last:top+=last
    a[top:top+n,x,:3]=self.palette[np.frombuffer(data[off+3:off+3+n],np.uint8)];a[top:top+n,x,3]=255;last=top;off+=n+4
  return Image.fromarray(a)
 @lru_cache(None)
 def image(self,name,flat=False,patch=False):
  direct=self.mod/name
  if direct.is_file():return self.decode(self.read(direct),flat)
  if name in self.defs and not patch:
   w,h,_,parts=self.defs[name];im=Image.new('RGBA',(w,h))
   for n,x,y in parts:im.alpha_composite(self.image(n,patch=True),(int(x),int(y)))
   return im
  p=self.paths.get(name)
  if p:return self.decode(self.read(p),'flats' in p.parts)
  return self.decode(self.lump(name),flat)

def connected(allowed,seeds):
 result=seeds&allowed
 while True:
  padded=np.pad(result,1);grown=result.copy()
  for dy,dx in ((0,1),(1,0),(1,2),(2,1)):
   grown|=padded[dy:dy+result.shape[0],dx:dx+result.shape[1]]&allowed
  if np.array_equal(grown,result):return result
  result=grown

def fire_pixels(r,g,b):
 # Yellow seeds cannot be skin or the Harvester's orange joints. Keep a bounded
 # two-pixel ember fringe: connected skin-colored regions must never flood-fill.
 seed=(r>=220)&(g>=185)&(g>=r*.83)&(b<130)
 allowed=((r>=100)&(g>=45)&(r>g*.95)&(b<g*.48))|((r>=235)&(g>=220)&(b<235))
 near=seed.copy()
 for _ in range(2):
  padded=np.pad(near,1)
  near=np.logical_or.reduce([padded[dy:dy+r.shape[0],dx:dx+r.shape[1]] for dy in range(3) for dx in range(3)])
 return connected(allowed&near,seed)

def sprite_mask(name,image):
 a=np.array(image).astype(int);r,g,b,alpha=a.transpose(2,0,1);h,w=r.shape;y,x=np.mgrid[:h,:w];m=np.zeros((h,w),np.uint8);p=name[:4];f=name[4]
 red=(r>=90)&(r>g*2+12)&(r>b*2+12)
 green=(g>=45)&(g>r*1.25)&(g>b*1.4)
 yellow=(r>=160)&(g>=110)&(b<g*.65)
 def put(sel,value=255):m[sel&(alpha>0)]=value
 if p=='DRKI' and f in 'ABCDEFGH':
  core=(r>=160)&(g>=110)&(b<100)&(y<h*.25);put(core)
  # Only immediate horizontal amber eye edges, exactly the approved A1 pixels.
  edge=np.zeros_like(core);edge[:,1:]|=core[:,:-1];edge[:,:-1]|=core[:,1:]
  put(edge&(r>=110)&(g>=50)&(g<110)&(b<25),128)
  if f in 'EFG':put((b>60)&(g>40)&(r<g*.6))
 elif p in ('SLHV','TRO2'):
  live='ABCDEFGHIJKLMNO' if p=='SLHV' else 'ABCDEFGH'
  if f in live:put(red&(y<h*.25))
  if p=='SLHV' and f in 'EFGHIJKLM':put(fire_pixels(r,g,b)&(y>h*.20))
 elif p=='SLHW':pass # Separate puff, already a BRIGHT effect state.
 elif p=='TROX':
  if f in 'ABCDEFGHIJWX':put(red)
 elif p=='HFRY':
  if f in 'ABCDEFGHIPQ':put(red);put(yellow&(y<h*.28))
 elif p=='HWAR':
  if f in 'ABCDEFGHIJK':put(green)
  if f in 'ABCDEFGHIJKLMNOP':put(fire_pixels(r,g,b))
  if f in 'MNOP':put((y<h*.26)&(r>g*1.2)&(g>=70)&(b<g*.4),160)
 elif p=='TORT':
  if f in 'ABCDGH':put(green&(y<h*.5))
  elif f in 'EFJKLMN':put(green)
 elif p=='PLEM':put(green)
 elif p=='MNTR':
  if f in 'ABCDEFUWX':put(green,160);put(green&(g>=170),224)
  if f in 'KM':put(red,224);put(fire_pixels(r,g,b))
 elif p=='MNTS':pass # Gibs only.
 elif p=='APYT':
  if f in 'ABCDEF':
   put(red&(y<h*.48)) # Eyes; body trim is outside the face band.
   put(connected((r>100)&(r>g*1.15)&(b<70)&(y>h*.35), yellow&(r>200)&(b<70)&(y>h*.35)))
  elif f in 'GHIJ':
   # Arachnophyte death: the two thruster blasts, central blast and cooling rings.
   flame=(r>=28)&(r>g*1.25)&(r>b*1.5)
   core_area=(((x-29)**2+(y-30)**2<18**2)|((x-165)**2+(y-30)**2<18**2)) if f=='G' else ((x-99)**2+(y-18)**2<18**2)
   core=(r>180)&(g>150)&(b>80)&core_area&(f in 'GH')
   region=((x<w*.35)|(x>w*.65)) if f=='G' else np.ones_like(flame)
   put(flame&region,160 if f in 'IJ' else 224)
   put((yellow&region)|core)
 elif p=='RSPI':
  if f in 'ABCDEFGHI':put(red&(y<h*.50))
 elif p=='CYCL':
  if f in 'ABCDEFGHIJKL':put((r>=200)&(g<100)&(b<30)&(y<h*.36))
 elif p=='ENCD':
  if f in 'ABCDEF':put(red|yellow)
 elif p in ('MPOS','HLGD'):pass # All muzzle-flash rotations already covered by reference masks.
 elif p=='REGN':
  put(red,160);put(red&(r>=180),224)
 elif p=='PHRT':put(red,192)
 # Near-white cores belong to green energy, but unrelated grey horns/claws
 # do not. Only light pale pixels connected directly to an already masked region.
 if p in ('TORT','PLEM','MNTR','HWAR'):
  seeds=(m>0)&green
  pale=(r>=160)&(g>=160)&(b>=100)&(g>=r*.94)&(g>=b)
  put(connected(seeds|pale,seeds)&pale,224 if p=='MNTR' else 255)
 return Image.fromarray(m).convert('RGB')

def surface_mask(name,image):
 a=np.array(image).astype(int);r,g,b,alpha=a.transpose(2,0,1);h,w=r.shape;y,x=np.mgrid[:h,:w];m=np.zeros((h,w),np.uint8)
 def put(sel,v=255):m[sel&(alpha>0)]=v
 if name=='NEUESDI':
  put((r>55)&(g>20)&(r>g*1.15)&(g>b*1.6),153)
 elif name in ('COMPBLUE','XA40TEX','XB40TEX'):
  put((b>35)&(b>r*1.8)&(b>g*1.25),96)
 elif name=='COMPRED':put((r>65)&(r>g*1.8)&(r>b*1.8),112)
 elif name.startswith('QRUNT'):put((r>100)&(r>g*1.35)&(g>b*1.3),192)
 elif name=='TELETOP':put((r>95)&(g>60)&(g>b*1.7),224)
 elif name.startswith('IKLITF'):
  put((r>145)&(g>115)&(b>85))
 elif name=='TLITE6_1':put((r>160)&(g>150)&(b>120))
 elif name=='TLITE6_5':put((r>130)&(r>g*1.7)&(r>b*1.7))
 elif name=='SW1NEW1':pass # Skull eyes are unlit in the off state.
 elif name=='SW2NEW1':put((r>60)&(r>g*2)&(r>b*2)&(y>=101)&(y<=109))
 elif name=='SW1NEW3':pass # All three indicators are unlit.
 elif name=='SW2NEW3':
  red_area=((x-48)**2+(y-16)**2<110)|((x>=5)&(x<=27)&(y>=21)&(y<=28))
  put(red_area&(r>90)&(r>g*1.2)&(r>b*1.4),224)
  put((x>=34)&(y>=34)&(y<=62)&(b>55)&(b>r*1.8),224)
 return Image.fromarray(m).convert('RGB')

def generate(root=ROOT,iwad='F:/DoomDev/DOOM2.WAD',check=False):
 root=Path(root);mod=root/'tutnt';prior_path=root/'tools/artwork/brightmaps/custom-manifest.json';prior=json.loads(prior_path.read_text()) if prior_path.exists() else {};art=Artwork(root,iwad);outputs={};records=[];seen={};lines=['// Generated by tools/build_custom_brightmaps.py. Original pixels only.']
 # UZDoom otherwise renames legacy MNTR F-K to U-Z, hiding the authored
 # F/K frames and overwriting U. A transparent unused Z marker preserves
 # this complete custom namespace without changing any original sprite.
 outputs['sprites/monsters/MNTRZ0.png']=png(Image.new('RGBA',(1,1)))
 refs=json.loads((root/'tools/brightmap-reference.json').read_text());covered={r['target'] for r in refs['bindings'] if r['kind']=='sprite'}
 # Reuse identical masks across frames AND reference/automatic/material banks.
 for path in sorted((mod/'materials').rglob('*.png')):
  if 'brightmap' not in path.as_posix() or path.parent==mod/OUT:continue
  im=Image.open(path).convert('RGB');seen.setdefault((im.size,sha(im.tobytes())),path.relative_to(mod).as_posix())
 def bind(kind,name,im,mask,flags=()):
  count=int(np.count_nonzero(np.array(mask)[:,:,0]));rec={'kind':kind,'target':name,'size':list(im.size),'source_pixels':sha(im.tobytes()),'pixels':count}
  if count==0:rec['status']='no emissive pixels';records.append(rec);return
  key=(mask.size,sha(mask.tobytes()));path=seen.get(key)
  if not path:safe_name=re.sub(r'[^a-z0-9_-]+','-',name.lower()).strip('-');path=f'{OUT}/{kind}-{safe_name}.png';seen[key]=path;outputs[path]=png(mask)
  lines.append(f'brightmap {kind} {name}\n{{\n    map "{path}"\n'+''.join('    '+f+'\n' for f in flags)+'}')
  rec.update(status='mapped',map=path,mask_pixels=key[1]);records.append(rec)
 for prefix in PREFIXES:
  for name,path in sorted(art.paths.items()):
   if not name.startswith(prefix) or 'sprites' not in path.parts or name=='MNTRZ0':continue
   im=art.image(path.relative_to(mod).as_posix())
   if name in covered:records.append({'kind':'sprite','target':name,'status':'reference preserved'});continue
   bind('sprite',name,im,sprite_mask(name,im),('thiswad',))
 for name in SURFACES:
  flat=name.startswith('TLITE') or name in ('IKLITF01','IKLITF07','TELETOP');im=art.image(name,flat=flat);mask=surface_mask(name,im)
  if name in ('QRUNT62','QRUNT63'):
   # Consolidate the previous ritual shader's exact mask into native GLDEFS.
   # This keeps its emissive pixels and intensity, with a single owner.
   rel=f'graphics/utnt-runes/{name}-mask.png';mask=art.decode(art.read(mod/rel)).convert('RGB')
   seen[mask.size,sha(mask.tobytes())]=rel
  bind('flat' if flat else 'texture',name,im,mask,('iwad',) if name.startswith('TLITE') or name=='COMPBLUE' else ('thiswad',))
 # The hardware voxel skin is an anonymous 16x16 palette texture. MODELDEF
 # binds the SAME KVX geometry to a named palette skin so GLDEFS can address it.
 # Keep native voxel angle, scale and uniform lighting; no geometry conversion.
 skin=Image.fromarray(art.palette.reshape(16,16,3)).convert('RGBA')
 outputs['voxels/heart-palette.png']=png(skin)
 rr,gg,bb=art.palette.astype(int).T
 levels=np.where((rr>=90)&(rr>gg*2+12)&(rr>bb*2+12),192,0).astype(np.uint8)
 mask=Image.fromarray(levels.reshape(16,16)).convert('RGB')
 bind('texture','"voxels/heart-palette.png"',skin,mask,('thiswad',))
 # Quoted full resource names must not become filenames.
 model=['// Generated native KVX material binding. Geometry and actor behavior unchanged.']
 for frame in 'ABCD':
  art.read(mod/f'voxels/UVPHRT{frame}.kvx')
  model.append(f'Model PortalCoreHeart\n{{\n Path "voxels"\n Model 0 "UVPHRT{frame}.kvx"\n Skin 0 "heart-palette.png"\n Scale 1 1 1\n AngleOffset 90\n NoInterpolation\n NoPerPixelLighting\n FrameIndex PHRT {frame} 0 0\n}}')
 outputs['modeldef/MODELDEF.brightmaps-custom']=('\n\n'.join(model)+'\n').encode()
 outputs[MODULE]=('\n\n'.join(lines)+'\n').encode()
 manifest={'version':1,'inputs':dict(sorted(art.inputs.items())),'families':PREFIXES,'surfaces':SURFACES,'bindings':records,'outputs':{p:sha(data) for p,data in outputs.items()}}
 outputs['../tools/artwork/brightmaps/custom-manifest.json']=(json.dumps(manifest,indent=2)+'\n').encode()
 for rel,data in outputs.items():
  path=mod/rel
  if check:
   if not path.is_file() or path.read_bytes()!=data:raise ValueError('Stale custom brightmap output: '+str(path))
  else:
   path.parent.mkdir(parents=True,exist_ok=True)
   if not path.is_file() or path.read_bytes()!=data:path.write_bytes(data)
 orphans=set((mod/OUT).glob('*.png'))-{mod/p for p in outputs}
 for path in orphans:
  rel=path.relative_to(mod).as_posix()
  if check or prior.get('outputs',{}).get(rel)!=sha(path.read_bytes()):raise ValueError('Unrecognized obsolete mask: '+str(path))
  assert path.resolve().parent==(mod/OUT).resolve()
  path.unlink()
 print(json.dumps({'mapped':sum(r['status']=='mapped' for r in records),'preserved':sum(r['status']=='reference preserved' for r in records),'non_emissive':sum(r['status']=='no emissive pixels' for r in records),'unique_new_images':sum(p.endswith('.png') for p in outputs)}))
 return manifest
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');p.add_argument('--iwad',default='F:/DoomDev/DOOM2.WAD');a=p.parse_args();generate(iwad=a.iwad,check=a.check)
