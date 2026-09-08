"""Verify terrain replacement preserves gameplay and has watertight shared slopes."""
import sys,re,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent.parent;W=Path.cwd()
sys.path.insert(0,str(R/'tools'));from test_caldera_structure import parse
from refine_caldera_terrain import BASE
if len(sys.argv)<2:raise SystemExit('Usage: python tools/test_caldera_detail.py BASELINE.wad [UPDATED.wad]')
before=Path(sys.argv[1])
after=Path(sys.argv[2]) if len(sys.argv)>2 else R/'tutnt/maps/tnt03b.wad'
old,a=parse(before);new,b=parse(after)
for k in BASE:assert a[k][:BASE[k]]==b[k][:BASE[k]],k
assert a['thing']==b['thing'],'All things must remain intact'
for k in old:
 if k not in ('TEXTMAP','ZNODES','BLOCKMAP','REJECT'):assert old[k]==new[k],k
def z(s,v):
 s=b['sector'][s];v=b['vertex'][v]
 if 'floorplane_a' not in s:return float(s['heightfloor'])
 return -(float(s['floorplane_a'])*float(v['x'])+float(s['floorplane_b'])*float(v['y'])+float(s['floorplane_d']))/float(s['floorplane_c'])
maxdelta=0
for i,l in enumerate(b['linedef'][BASE['linedef']:],BASE['linedef']):
 assert not any(k in l for k in ['special','arg0','id'])
 front=int(b['sidedef'][int(l['sidefront'])]['sector']);assert front>=BASE['sector']
 if 'sideback' in l:
  back=int(b['sidedef'][int(l['sideback'])]['sector']);assert back>=BASE['sector']
  for k in ['v1','v2']:
   d=abs(z(front,int(l[k]))-z(back,int(l[k])));maxdelta=max(d,maxdelta);assert d<.001,(i,d)
assert 'ZNODES' in new
result={'ok':True,'gameplay_geometry_preserved':True,'all_actors_and_acs_preserved':True,'max_shared_edge_error':maxdelta,'counts':{k:len(v) for k,v in b.items()},'sha256':hashlib.sha256(after.read_bytes()).hexdigest()}
(W/'structure-results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
