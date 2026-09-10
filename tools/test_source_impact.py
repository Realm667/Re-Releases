"""Check Source light bursts and camera-local refraction, including saved pulses."""
from pathlib import Path
import argparse,json
from check_engine import ROOT,run_case

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('engine','iwad','mod','work'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--renderer',choices=['0','1'],default='1');a=p.parse_args()
 W=a.work.resolve();W.mkdir(parents=True,exist_ok=True)
 cmd=['wait 450','netevent sourceview 4','wait 10','netevent sourcekill','wait 95','save source-impact','wait 16',
  'netevent sourcedeathcheck 108 114','netevent sourcefxcheck 1 1','wait 5','screenshot logs/impact-on.png',
  'UTNT_shaderoverlayswitch false','wait 2','netevent sourcefxcheck 0 1','wait 12','screenshot logs/impact-shader-off.png',
  'load source-impact','wait 17','UTNT_shaderoverlayswitch true','wait 3','netevent sourcefxcheck 1 1','wait 5',
  'load source-impact','wait 17','UTNT_reducedfx true','wait 3','netevent sourcefxcheck 0 1','wait 5','screenshot logs/impact-reduced.png',
  'load source-impact','wait 17','UTNT_reducedfx false','UTNT_fxquality 0','wait 3','netevent sourcefxcheck 0 0','wait 5',
  'load source-impact','wait 17','UTNT_fxquality 3','netevent sourceview 5','wait 3','netevent sourcefxcheck 0 1','wait 5',
  'load source-impact','wait 17','netevent sourceview 4','wait 28','netevent sourcefxcheck 1 1','wait 5','screenshot logs/second-impact.png',
  'wait 17','netevent sourcefxcheck 1 0','wait 5','screenshot logs/final-impact.png',
  'wait 93','netevent sourcedeathcheck 257 263','netevent sourcefxcheck 0 0','wait 3','screenshot logs/impact-empty.png',
  'map TNT04C','wait 100','netevent sourcefxcheck 0 -1','wait 3','echo UTNT_TEST_END','wait 3','quit']
 result=run_case(a.engine,a.iwad,root=W,mod=a.mod,addon=ROOT/'tools/source-tests',mapname='TNT04CN',renderer=a.renderer,timeout=200,label='source-impact',commands='; '.join(cmd),
  settings=[('win_w',1298),('win_h',767),('screenblocks',11),('con_notifytime',0),('r_drawplayersprites','false'),('crosshair',0),('vid_maxfps',60),('i_pauseinbackground','false'),('vid_activeinbackground','true'),('UTNT_fxquality',3),('UTNT_reducedfx','false')])
 # Require every scheduled render check: a lost console event must not pass.
 result['impact_checks']=Path(result['log']).read_text().count('Source impact shader expected=')
 if result['impact_checks']!=10:
  result['ok']=False;result['errors'].append('missing impact render checks')
 (W/'runtime.json').write_text(json.dumps(result,indent=2)+'\n')
 return 0 if result['ok'] and result['assertions']>=35 else 1
if __name__=='__main__':raise SystemExit(main())
