"""Verify TNT04B map preservation, sealed scenery, and shared comet programs."""
from pathlib import Path
import argparse,json,hashlib,math
from test_caldera_structure import parse
ROOT=Path(__file__).resolve().parent.parent

def verify(baseline,current,root=ROOT):
 old,a=parse(baseline);new,b=parse(current);checks=[]
 base={k:len(v) for k,v in a.items()}
 for k in ['vertex','linedef','sidedef','sector']:
  assert a[k]==b[k][:base[k]],k;checks.append('original '+k+' unchanged')
 assert len(a['thing'])==len(b['thing'])
 disabled=[]
 for i,t in enumerate(a['thing']):
  u=b['thing'][i]
  if i==34:
   assert u['type']=='9080' and 'id' not in u
   assert tuple(float(u[k]) for k in ['x','y','height'])==(18000,18000,640)
   assert {k:v for k,v in t.items() if k not in ['x','y','height']}=={k:v for k,v in u.items() if k not in ['x','y','height']}
  elif t.get('type')=='19020':
   assert t.get('id')=='40' and u['type']=='9001'
   assert {k:v for k,v in t.items() if k!='type'}=={k:v for k,v in u.items() if k!='type'};disabled.append(i)
  else:assert t==u,('thing',i)
 assert len(disabled)==96;checks.append('one default camera moved; 96 retired decorative spawners disabled; all other things unchanged')
 for name,data in old.items():
  if name not in ['TEXTMAP','ZNODES','BLOCKMAP','REJECT']:assert data==new[name],name
 checks.append('all ACS and unrelated map lumps unchanged')
 def z(sec,vi):
  s=b['sector'][sec];v=b['vertex'][vi]
  if 'floorplane_a' not in s:return float(s['heightfloor'])
  return -(float(s['floorplane_a'])*float(v['x'])+float(s['floorplane_b'])*float(v['y'])+float(s['floorplane_d']))/float(s['floorplane_c'])
 worst=0;boundary=0
 for i,line in enumerate(b['linedef'][base['linedef']:],base['linedef']):
  assert int(line['v1'])>=base['vertex'] and int(line['v2'])>=base['vertex']
  assert not any(k in line for k in ['special','arg0','id'])
  for side in ['sidefront','sideback']:
   if side in line:assert int(line[side])>=base['sidedef']
  sf=int(b['sidedef'][int(line['sidefront'])]['sector']);assert sf>=base['sector']
  if 'sideback' not in line:boundary+=1;continue
  sb=int(b['sidedef'][int(line['sideback'])]['sector']);assert sb>=base['sector']
  for key in ['v1','v2']:
   gap=abs(z(sf,int(line[key]))-z(sb,int(line[key])));worst=max(worst,gap);assert gap<.001,(i,gap)
 assert boundary==256
 assert all(10000<float(v[k])<26000 for v in b['vertex'][base['vertex']:] for k in ['x','y'])
 checks.append('scenery isolated from gameplay, with continuous shared edges and one outer boundary')
 assert 'ZNODES' in new
 source=(root/'tools/war-comets.glsl').read_text()
 for face in 'NESWUD':
  assert (root/f'tutnt/shaders/ash/sky-{face}.fp').read_text().startswith(source+'\n')
  assert (root/f'tutnt/shaders/caldera-war/sky-{face}.fp').read_text().startswith(source+'\n')
 checks.append('TNT04A and TNT04B embed the exact same comet source on all six faces')
 return dict(ok=True,checks=checks,maximum_shared_edge_error=worst,original_counts=base,final_counts={k:len(v) for k,v in b.items()},map_sha256=hashlib.sha256(Path(current).read_bytes()).hexdigest())

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--map',type=Path,default=ROOT/'tutnt/maps/tnt04b.wad');p.add_argument('--output',type=Path)
 a=p.parse_args();r=verify(a.baseline,a.map)
 if a.output:a.output.write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps(r,indent=2))
