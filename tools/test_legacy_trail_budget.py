"""Native lifecycle/quality tests for cosmetic trail admission; all outputs in .codex."""
import argparse,json,zipfile
from pathlib import Path
from check_engine import ROOT,run_case
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--engine',default='F:/DoomDev/uzdoom.exe');p.add_argument('--iwad',default='F:/DoomDev/DOOM2.WAD')
p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3');p.add_argument('--renderer',default='0',choices=['0','1']);a=p.parse_args()
addon=ROOT/'tutnt/.codex/builds/legacy-trail-budget-test.pk3'
with zipfile.ZipFile(addon,'w') as z:
 for f in (ROOT/'tools/fixtures/legacy-trail-budget').iterdir():z.write(f,f.name)
 z.write(ROOT/'tools/fixtures/voxels/maps/VXLAB.wad','maps/VXLAB.wad')
cmd=['wait 70']
for q,n in [(3,768),(2,384),(1,192),(0,0)]:cmd += [f'UTNT_fxquality {q}','wait 3',f'netevent trailbudget 1 {n}','wait 3']
cmd += ['netevent trailbudget 5','wait 3','UTNT_fxquality 3','UTNT_reducedfx true','wait 3','netevent trailbudget 1 192','wait 3','UTNT_reducedfx false','wait 3','netevent trailbudget 2','wait 160','netevent trailbudget 3','wait 3','netevent trailbudget 4','wait 3','save trail-budget','wait 3','load trail-budget','wait 70','netevent trailbudget 3','wait 3','netevent trailbudget 1 768','wait 3','echo UTNT_TEST_END','quit']
r=run_case(a.engine,a.iwad,mod=a.mod,addon=addon,mapname='VXLAB',renderer=a.renderer,label='legacy-trail-budget',timeout=70,commands='; '.join(cmd),settings=[('vid_activeinbackground','true'),('i_pauseinbackground','false')])
r['ok'] &= r['assertions']==61
(ROOT/'tutnt/.codex/validation/legacy-trail-budget.json').write_text(json.dumps(r,indent=2))
if not r['ok']:print(Path(r['log']).read_text()[-6000:])
raise SystemExit(0 if r['ok'] else 1)
