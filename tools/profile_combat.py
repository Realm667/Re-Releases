"""Repeated frame-interval measurements in three original maps; run without other engine processes."""
import argparse,json,os,pathlib,re,statistics
from check_engine import ROOT,run_case
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--repeats',type=int,default=2);p.add_argument('--gore',nargs='+',type=int,default=[0,1024]);p.add_argument('--prefix',default='combat');a=p.parse_args()
results=[]
for renderer in ('0','1'):
 for mapname in ('TNT02','TNTLE','TNT04CN'):
  for gore in a.gore:
   for repeat in range(a.repeats):
    label=f'{a.prefix}-{mapname}-{renderer}-{gore}-{repeat}'
    commands='+attack; wait 585; -attack; profilethinkers -t 12; profilecsthinkers -t 12; echo UTNT_TEST_END; screenshot logs/'+label+'.png; wait 5; quit\n'
    r=run_case(pathlib.Path(os.environ['UTNT_ENGINE']),pathlib.Path(os.environ['UTNT_IWAD']),mapname=mapname,renderer=renderer,addon=ROOT/'tools/combat-profile',label=label,commands=commands,timeout=45,settings=[('vid_maxfps',0),('vid_vsync','false'),('nashgore_maxgore',gore)])
    out=pathlib.Path(r['log']).read_text();m=re.search(r'UTNT_FRAME_MS ([0-9.,]+)',out)
    samples=sorted(float(x) for x in m[1].split(',')) if m else []
    if len(samples)<100:r['ok']=False;r['errors'].append('missing frame samples')
    if samples:
     r['frame_ms']={'count':len(samples),'mean':statistics.mean(samples),'median':statistics.median(samples),'p95':samples[int((len(samples)-1)*.95)],'p99':samples[int((len(samples)-1)*.99)]}
    r.update(map=mapname,renderer=renderer,gore_limit=gore,repeat=repeat)
    counts=re.search(r'UTNT_COMBAT_COUNTS actors=(\d+) visuals=(\d+) kills=(\d+)',out)
    if counts:r['counts']=dict(zip(('actors','visuals','kills'),map(int,counts.groups())))
    results.append(r);(ROOT/('logs/'+a.prefix+'-profile-results.json')).write_text(json.dumps(results,indent=2))
    if not r['ok']:raise SystemExit(1)
raise SystemExit(0)
