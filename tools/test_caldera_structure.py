import sys,re,json,hashlib,math
from pathlib import Path
R=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(R/'tools'))
from build_utnt import read_wad
def parse(path):
 lumps={n.rstrip(b'\0').decode():d for n,d in read_wad(path)[1]}
 groups={k:[] for k in ('vertex','linedef','sidedef','sector','thing')}
 for m in re.finditer(r'\b(vertex|linedef|sidedef|sector|thing)\s*(?://[^\n]*\n\s*)?\{([^}]*)\}',lumps['TEXTMAP'].decode()):
  groups[m[1]].append(dict(re.findall(r'(\w+)\s*=\s*([^;]+);',m[2])))
 return lumps,groups
def verify(before,after):
 old,a=parse(before);new,b=parse(after);checks=[]
 for name in old:
  if name not in ('TEXTMAP','ZNODES','BLOCKMAP','REJECT'):
   assert old[name]==new[name],name;checks.append(name+' unchanged')
 for name in ('vertex','linedef','sidedef','sector'):
  assert a[name]==b[name][:len(a[name])],name;checks.append('original '+name+' unchanged')
 assert len(a['thing'])==len(b['thing'])
 for i,(x,y) in enumerate(zip(a['thing'],b['thing'])):
  if i==5:
   assert x['type']==y['type']=='9080'
   assert {k:v for k,v in x.items() if k not in ('x','y','height')}=={k:v for k,v in y.items() if k not in ('x','y','height')}
  else:assert x==y,('thing',i)
 checks.append('all gameplay things and secondary viewpoint unchanged')
 nsec=len(a['sector']);nline=len(a['linedef']);max_delta=0
 def z(sec,vertex):
  s=b['sector'][sec];v=b['vertex'][vertex]
  if 'floorplane_a' not in s:return float(s['heightfloor'])
  return -(float(s['floorplane_a'])*float(v['x'])+float(s['floorplane_b'])*float(v['y'])+float(s['floorplane_d']))/float(s['floorplane_c'])
 for i,l in enumerate(b['linedef'][nline:],nline):
  sf=int(b['sidedef'][int(l['sidefront'])]['sector']);assert sf>=nsec
  assert not any(k in l for k in ('special','arg0','id'))
  if 'sideback' not in l:continue
  sb=int(b['sidedef'][int(l['sideback'])]['sector']);assert sb>=nsec
  for key in ('v1','v2'):
   v=int(l[key]);delta=abs(z(sf,v)-z(sb,v));max_delta=max(delta,max_delta)
   assert delta<.001,(i,delta)
 checks.append('scenery mesh sealed; no gameplay sector joins or specials')
 assert 'ZNODES' in new
 return dict(ok=True,checks=checks,maximum_shared_edge_height_error=max_delta,counts={k:len(v) for k,v in b.items()},map_sha256=hashlib.sha256(Path(after).read_bytes()).hexdigest())

if __name__=='__main__':
 import argparse,tempfile,subprocess
 p=argparse.ArgumentParser(description="Verify that caldera scenery preserves baseline gameplay geometry and scripts.")
 p.add_argument('--baseline',type=Path);p.add_argument('--baseline-ref');p.add_argument('--map',type=Path,default=R/'tutnt/maps/tnt03b.wad');p.add_argument('--output',type=Path)
 a=p.parse_args()
 if not a.baseline and not a.baseline_ref:p.error('Set --baseline WAD or --baseline-ref git-revision')
 with tempfile.TemporaryDirectory() as d:
  baseline=a.baseline
  if not baseline:
   baseline=Path(d)/'before.wad';baseline.write_bytes(subprocess.check_output(['git','-C',str(R),'show',a.baseline_ref+':tutnt/maps/tnt03b.wad']))
  result=verify(baseline,a.map)
 text=json.dumps(result,indent=2)
 if a.output:a.output.write_text(text)
 print(text)
