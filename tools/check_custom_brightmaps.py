"""Check native-pixel alignment, emissive coverage and unique brightmap ownership."""
from pathlib import Path
from collections import Counter
import argparse,json,re
import numpy as np
from PIL import Image
from build_custom_brightmaps import ROOT,Artwork,generate,sha,OUT
from check_brightmaps import uncomment

def check(root=ROOT,iwad='F:/DoomDev/DOOM2.WAD'):
 root=Path(root);mod=root/'tutnt';manifest=generate(root,iwad,check=True);art=Artwork(root,iwad);owners=Counter();materials=set();errors=[]
 def expand(path,stack=()):
  if path in stack:raise ValueError('Cyclic GLDEFS include')
  text=uncomment(path.read_text())
  for m in re.finditer(r'\bbrightmap\s+(sprite|texture|flat)\s+("[^"]+"|\S+)\s*\{',text,re.I):owners[m[1].lower(),m[2].strip('"').upper()]+=1
  for m in re.finditer(r'\bMaterial\s+(?:(?:Texture|Flat|Sprite)\s+)?"([^"]+)"\s*\{([^}]+)\}',text,re.I):
   if re.search(r'\bBrightmap\s+"',m[2],re.I) or 'ritual-frame.fp' in m[2]:materials.add(m[1].upper())
  for m in re.finditer(r'#include\s+(?:"([^"]+)"|(\S+))',text,re.I):expand(mod/(m[1] or m[2]),(*stack,path))
 expand(mod/'GLDEFS.txt');auto={p.stem.upper() for p in (mod/'materials/brightmaps/auto').glob('*.png')};records={r['target'].strip('"'):r for r in manifest['bindings']}
 mapped=[r for r in manifest['bindings'] if r['status']=='mapped']
 for r in mapped:
  name=r['target'].strip('"');token=r['kind'],name.upper()
  if owners[token]!=1:errors.append(f'{token}: {owners[token]} owners')
  if name.upper() in auto|materials:errors.append('Duplicate auto/material owner: '+name)
  im=Image.open(mod/r['map']).convert('RGB');pixels=np.array(im)
  if list(im.size)!=r['size'] or sha(im.tobytes())!=r['mask_pixels']:errors.append('Alignment/hash mismatch: '+name)
  if not np.array_equal(pixels[:,:,0],pixels[:,:,1]) or not np.array_equal(pixels[:,:,1],pixels[:,:,2]):errors.append('Non-grayscale mask: '+name)
  if r['kind']=='sprite':
   source=art.image(art.paths[name].relative_to(mod).as_posix());opaque=np.array(source)[:,:,3]>0
   if np.any((pixels[:,:,0]>0)&~opaque):errors.append('Mask leaks into transparent space: '+name)
 # Approved Nami regression: no teeth, claws, horns or brown reflection pixels.
 n=records['DRKIA1'];im=Image.open(mod/n['map']).convert('L');expected=Image.new('L',(41,57))
 for x,y,v in [(17,6,128),(18,6,255),(23,6,255),(24,6,128)]:expected.putpixel((x,y),v)
 if im.tobytes()!=expected.tobytes():errors.append('Approved four-pixel Nami mask changed')
 for name in ('SW1NEW1','SW1NEW3','DRKIM0','MNTSA0','HLGDN0','MPOSV0'):
  if records[name]['status']!='no emissive pixels':errors.append('Unlit switch/corpse unexpectedly emits: '+name)
 for name in ('APYTG0','APYTH0','APYTI0','APYTJ0','MNTRK0','MNTRM0','HWARF1','SLHVH1','ENCDB1','REGNA0','PHRTA0','SW2NEW1','SW2NEW3'):
  if records[name]['status']!='mapped':errors.append('Missing requested emissive phase: '+name)
 # Brightmaps do not introduce a per-pixel shader cost or alter the KVX shape.
 model=(mod/'modeldef/MODELDEF.brightmaps-custom').read_text()
 if model.count('AngleOffset 90')!=4 or model.count('NoPerPixelLighting')!=6:errors.append('Native voxel presentation flags missing')
 # Do not let a future color-rule change make the metal glow again.
 barrel=np.array(Image.open(mod/records['voxels/barrel-palette.png']['map']).convert('L')).reshape(-1)
 if set(np.flatnonzero(barrel))!=set(range(112,124)):errors.append('Barrel mask includes metal or omits slime')
 for frame in 'AB':
  if f'Model 0 "CVBAR1{frame}.kvx"' not in model or f'FrameIndex BAR1 {frame} 0 0' not in model:errors.append('Missing original barrel idle voxel')
 light=re.search(r'pulselight BARREL\s*\{([^}]+)\}',(mod/'GLDEFS.txt').read_text())
 if not light or not re.search(r'DontLightSelf\s+1',light[1]):errors.append('Barrel self-light exclusion missing')
 result={'ok':not errors,'new_bindings':len(mapped),'by_kind':dict(Counter(r['kind'] for r in mapped)),'new_mask_images':len(list((mod/OUT).glob('*.png'))),'preserved_candidate_frames':sum(r['status']=='reference preserved' for r in manifest['bindings']),'reviewed_non_emissive_frames_or_states':sum(r['status']=='no emissive pixels' for r in manifest['bindings']),'errors':errors}
 print(json.dumps(result,indent=2));return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--iwad',default='F:/DoomDev/DOOM2.WAD');a=p.parse_args();raise SystemExit(0 if check(iwad=a.iwad)['ok'] else 1)
