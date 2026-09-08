"""Verify that TNT02's sky update preserves gameplay outside its explicit lighting/ACS scope."""
import argparse,re,json,hashlib,subprocess,tempfile
from pathlib import Path
from test_caldera_structure import parse
def verify(before,after):
 old,a=parse(before);new,b=parse(after)
 for kind,extra in [('vertex',4),('linedef',4),('sidedef',4),('sector',1),('thing',0)]:assert len(b[kind])==len(a[kind])+extra,kind
 for kind in ['vertex','linedef','sidedef']:assert a[kind]==b[kind][:len(a[kind])],kind
 changed=[]
 for i,(x,y) in enumerate(zip(a['sector'],b['sector'])):
  outside=x.get('textureceiling')=='"F_SKY1"'
  if not outside:assert x==y,('interior',i);continue
  changed.append(i)
  assert int(y['lightcolor'])==0xb9c9dc and float(y['desaturation'])==.16
  assert int(y['lightlevel'])==max(160,int(x.get('lightlevel','160')))
  assert {k:v for k,v in x.items() if k not in ['lightcolor','desaturation','lightlevel']}=={k:v for k,v in y.items() if k not in ['lightcolor','desaturation','lightlevel']}
 assert len(changed)==551
 for i,(x,y) in enumerate(zip(a['thing'],b['thing'])):
  if i==0:
   assert x['type']==y['type']=='9080'
   assert float(y['x'])==28000 and float(y['y'])==-28000 and float(y['height'])==128
   assert {k:v for k,v in x.items() if k not in ['x','y','height']}=={k:v for k,v in y.items() if k not in ['x','y','height']}
  else:assert x==y,('actor',i)
 for name in old:
  if name not in ['TEXTMAP','SCRIPTS','BEHAVIOR','ZNODES','BLOCKMAP','REJECT']:assert old[name]==new[name],name
 def without_thunder(s):
  s=s.decode();start=s.index('// Thunder and Storm');end=s.index('//Ambient Sounds',start);return s[:start]+s[end:]
 assert without_thunder(old['SCRIPTS'])==without_thunder(new['SCRIPTS'])
 assert b'script 2 OPEN { terminate; }' in new['SCRIPTS'] and 'ZNODES' in new
 for l in b['linedef'][len(a['linedef']):]:
  assert int(l['v1'])>=len(a['vertex']) and int(l['v2'])>=len(a['vertex']) and int(l['sidefront'])>=len(a['sidedef'])
  assert not any(k in l for k in ['special','sideback','id'])
 return dict(ok=True,exterior_sectors=len(changed),gameplay_geometry_preserved=True,interior_sectors_unchanged=True,secondary_sky_cameras_preserved=True,all_other_acs_unchanged=True,counts={k:len(v) for k,v in b.items()},sha256=hashlib.sha256(after.read_bytes()).hexdigest())
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--before',type=Path,required=True);p.add_argument('--after',type=Path,required=True);p.add_argument('--output',type=Path)
 a=p.parse_args();r=verify(a.before,a.after);text=json.dumps(r,indent=2)
 if a.output:a.output.write_text(text,encoding='utf-8')
 print(text)
