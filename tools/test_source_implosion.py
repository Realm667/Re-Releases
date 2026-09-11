"""Verify inward rune motion, saved singularity, single collapse and empty centre."""
from pathlib import Path
import argparse,json
from check_engine import ROOT,run_case

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--map',dest='mapname',choices=['TNT04CN','TNT04C'],default='TNT04CN')
 for n in ('engine','iwad','mod','work'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--renderer',choices=['0','1'],default='1');a=p.parse_args()
 W=a.work.resolve();W.mkdir(parents=True,exist_ok=True)
 cmd=['wait 450','netevent sourcematerialcheck','netevent sourceview 4','wait 10','netevent sourcekill','wait 55','screenshot logs/01-core-forms.png',
  'wait 45','netevent sourceimplosioncheck 0','screenshot logs/02-suction.png','save source-implosion','wait 10','load source-implosion',
  'wait 25','netevent sourceimplosioncheck 1','screenshot logs/03-restored-core.png',
  'wait 14','netevent sourceimplosioncheck 2','screenshot logs/04-tight-orbits.png',
  'wait 15','screenshot logs/05-collapse.png','wait 5','netevent sourceimplosioncheck 3',
  'wait 2','screenshot logs/05b-light-break.png','wait 5','screenshot logs/06-shockwave.png','wait 38','screenshot logs/07-tail.png',
  'wait 58','netevent sourceimplosioncheck 4','netevent sourcematerialcheck','netevent sourcedeathcheck 257 270','wait 5','screenshot logs/08-empty.png',
  'echo UTNT_TEST_END','wait 3','quit']
 r=run_case(a.engine,a.iwad,root=W,mod=a.mod,addon=ROOT/'tools/source-tests',mapname=a.mapname,renderer=a.renderer,timeout=220,label='source-implosion',commands='; '.join(cmd),
  settings=[('win_w',1298),('win_h',767),('screenblocks',12),('con_notifytime',0),('r_drawplayersprites','false'),('crosshair',0),('vid_maxfps',60),('i_pauseinbackground','false'),('vid_activeinbackground','true'),('UTNT_fxquality',3),('UTNT_reducedfx','false')])
 (W/'runtime.json').write_text(json.dumps(r,indent=2)+'\n')
 return 0 if r['ok'] and r['assertions']>=34 else 1
if __name__=='__main__':raise SystemExit(main())
