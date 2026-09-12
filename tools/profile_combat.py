"""Repeated frame-interval measurements in three original maps; run without other engine processes."""
import argparse,json,os,pathlib,re,statistics
from check_engine import ROOT,run_case
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--mod',type=pathlib.Path,default=ROOT/'tutnt.pk3')
p.add_argument('--compare',type=pathlib.Path,help='Alternate AB/BA against this immutable baseline package')
p.add_argument('--maps',nargs='+',default=['TNT02','TNTLE','TNT04CN'])
p.add_argument('--renderers',nargs='+',choices=['0','1'],default=['0','1'])
p.add_argument('--repeats',type=int,default=2);p.add_argument('--gore',nargs='+',type=int,default=[0,1024]);p.add_argument('--prefix',default='combat');a=p.parse_args()
results=[]
for renderer in a.renderers:
 for mapname in a.maps:
  for gore in a.gore:
   for repeat in range(a.repeats):
    packages=[('after',a.mod)] if not a.compare else [('before',a.compare),('after',a.mod)]
    if repeat%2:packages.reverse()
    for version,package in packages:
     label=f'{a.prefix}-{mapname}-{renderer}-{gore}-{repeat}-{version}'
     commands='+attack; wait 585; -attack; profilethinkers -t 12; profilecsthinkers -t 12; echo UTNT_TEST_END; screenshot logs/'+label+'.png; wait 5; quit\n'
     r=run_case(pathlib.Path(os.environ['UTNT_ENGINE']),pathlib.Path(os.environ['UTNT_IWAD']),mod=package,mapname=mapname,renderer=renderer,addon=ROOT/'tools/combat-profile',label=label,commands=commands,timeout=45,settings=[('vid_maxfps',0),('vid_vsync','false'),('i_pauseinbackground','false'),('vid_activeinbackground','true'),('UTNT_fxquality',3),('UTNT_reducedfx','false'),('nashgore_maxgore',gore)])
     out=pathlib.Path(r['log']).read_text();m=re.search(r'UTNT_FRAME_MS ([0-9.,]+)',out)
     samples=sorted(float(x) for x in m[1].split(',')) if m else []
     if len(samples)<100:r['ok']=False;r['errors'].append('missing frame samples')
     if samples:
      r['frame_ms']={'count':len(samples),'mean':statistics.mean(samples),'median':statistics.median(samples),'p95':samples[int((len(samples)-1)*.95)],'p99':samples[int((len(samples)-1)*.99)]}
     r.update(map=mapname,renderer=renderer,gore_limit=gore,repeat=repeat,version=version,package=str(package.resolve()))
     counts=re.search(r'UTNT_COMBAT_COUNTS actors=(\d+) visuals=(\d+) kills=(\d+)',out)
     if counts:r['counts']=dict(zip(('actors','visuals','kills'),map(int,counts.groups())))
     results.append(r);(ROOT/('tutnt/.codex/validation/'+a.prefix+'-profile-results.json')).write_text(json.dumps(results,indent=2))
     if not r['ok']:raise SystemExit(1)
raise SystemExit(0)
