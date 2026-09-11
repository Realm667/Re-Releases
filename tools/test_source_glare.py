"""Verify the amber opening exposure, visibility gates and saved reconstruction."""
from pathlib import Path
import argparse,json
from check_engine import ROOT,run_case

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--map',dest='mapname',choices=['TNT04CN','TNT04C'],default='TNT04CN')
 for n in ('engine','iwad','mod','work'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--renderer',choices=['0','1'],default='1');a=p.parse_args()
 W=a.work.resolve();W.mkdir(parents=True,exist_ok=True)
 # Distinct restored ages prevent render-request timestamps from colliding.
 cmd=['wait 450','netevent sourceview 4','wait 10','netevent sourcefxcheck 0 -1','wait 3','netevent sourcefxreset','wait 3','netevent sourcekill','wait 20','save source-glare','wait 3','netevent sourcefxcheck 1 0','wait 3','screenshot logs/01-amber-opening.png',
  'UTNT_shaderoverlayswitch false','wait 3','netevent sourcefxcheck 0 0','wait 3','screenshot logs/02-overlay-off.png',
  'load source-glare','wait 20','UTNT_shaderoverlayswitch true','wait 5','netevent sourcefxcheck 1 0','wait 2','screenshot logs/03-restored-glare.png',
  'load source-glare','wait 22','UTNT_reducedfx true','wait 5','netevent sourcefxcheck 0 0','wait 2','screenshot logs/04-reduced.png',
  'load source-glare','wait 24','UTNT_reducedfx false','UTNT_fxquality 0','wait 5','netevent sourcefxcheck 0 0','wait 2',
  'load source-glare','wait 26','UTNT_fxquality 3','wait 5','netevent sourceview 5','wait 3','netevent sourcefxcheck 0 -1','wait 70','screenshot logs/away.png',
  'load source-glare','wait 20','netevent sourceview 4','wait 35','netevent sourcefxcheck 1 -1','wait 2','screenshot logs/05-gravity-transition.png',
  'wait 145','netevent sourcefxcheck 0 0','wait 2','echo UTNT_TEST_END','wait 3','quit']
 r=run_case(a.engine,a.iwad,root=W,mod=a.mod,addon=ROOT/'tools/source-tests',mapname=a.mapname,renderer=a.renderer,timeout=200,label='source-glare',commands='; '.join(cmd),
  settings=[('win_w',1298),('win_h',767),('screenblocks',12),('con_notifytime',0),('r_drawplayersprites','false'),('crosshair',0),('vid_maxfps',60),('i_pauseinbackground','false'),('vid_activeinbackground','true'),('UTNT_fxquality',3),('UTNT_reducedfx','false'),('UTNT_shaderoverlayswitch','true')])
 r['glare_checks']=Path(r['log']).read_text().count('Source impact shader expected=')
 if r['glare_checks']!=9:r['ok']=False;r['errors'].append('missing glare checks')
 (W/'runtime.json').write_text(json.dumps(r,indent=2)+'\n')
 return 0 if r['ok'] else 1
if __name__=='__main__':raise SystemExit(main())
