"""Alternating immutable-package TNT04A bridge benchmark. Never runs alongside another benchmark."""
import argparse,json,re,statistics,hashlib
from pathlib import Path
from check_engine import ROOT,run_case
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--engine',default='F:/DoomDev/uzdoom.exe');p.add_argument('--iwad',default='F:/DoomDev/DOOM2.WAD')
p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3');p.add_argument('--compare',type=Path)
p.add_argument('--renderer',default='0',choices=['0','1']);p.add_argument('--repeats',type=int,default=3)
p.add_argument('--label',default='bridge-performance');a=p.parse_args()
if not re.fullmatch(r'[a-zA-Z0-9_-]+',a.label):p.error('label must be a simple filename')
w=ROOT/'tutnt/.codex/work/performance-audit-oct';w.mkdir(parents=True,exist_ok=True)
results=[]
packages=[('before',a.compare),('after',a.mod)] if a.compare else [('current',a.mod)]
hashes={name:hashlib.sha256(file.read_bytes()).hexdigest() for name,file in packages}
for repeat in range(a.repeats):
 for version,package in (packages if repeat%2==0 else list(reversed(packages))):
  label=f'{a.label}-{repeat}-{version}';shot=w/(label+'.png')
  r=run_case(a.engine,a.iwad,mod=package,addon=ROOT/'tools/fixtures/bridge-performance',mapname='TNT04A',renderer=a.renderer,label=label,timeout=90,commands=f'stat rendertimes; stat renderstats; wait 500; profilethinkers -t 20; profilecsthinkers -t 20; wait 5; screenshot {shot.as_posix()}; echo UTNT_TEST_END; quit',settings=[('vid_maxfps',0),('vid_vsync','false'),('vid_activeinbackground','true'),('i_pauseinbackground','false'),('vid_lowerinbackground','false'),('con_notifytime',0)])
  text=Path(r['log']).read_text();m=re.search(r'UTNT_FRAME_MS ([0-9.,]+)',text)
  values=sorted(map(float,m[1].split(','))) if m else []
  counts=re.search(r'BRIDGE_COUNTS actors=(\d+) client=(\d+) kills=(\d+)',text)
  if counts:r['counts']=dict(zip(('actors','client','kills'),map(int,counts.groups())))
  r.update(version=version,repeat=repeat,sha256=hashes[version],renderer=a.renderer)
  r['ok'] &= len(values)>=100 and bool(counts)
  if values:r['frame_ms']={'samples':len(values),'median':statistics.median(values),'p95':values[int(len(values)*.95)],'p99':values[int(len(values)*.99)]}
  results.append(r);print(json.dumps(r),flush=True)
  (ROOT/'tutnt/.codex/validation'/(a.label+'.json')).write_text(json.dumps(results,indent=2))
  if not r['ok']:print(text[-4000:]);raise SystemExit(1)
