"""Exercise ring occlusion views, animated energy and the longer saved-clock glare."""
from pathlib import Path
import argparse,json
from check_engine import ROOT,run_case

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('engine','iwad','mod','work'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--renderer',choices=['0','1'],default='1');a=p.parse_args()
 W=a.work.resolve();W.mkdir(parents=True,exist_ok=True)
 cmd=['wait 450','netevent sourceview 6','wait 30','netevent sourceenergycheck','screenshot logs/01-ring.png',
  'save source-energy','wait 4','load source-energy','wait 35','netevent sourceenergycheck','screenshot logs/02-restored-ring.png',
  'netevent sourceview 7','wait 70','screenshot logs/03-shaft.png','wait 12','screenshot logs/04-shaft-motion.png',
  'netevent sourceview 2','wait 30','screenshot logs/05-side.png',
  'netevent sourceview 4','wait 20','netevent sourcekill','wait 45','screenshot logs/06-glow-hold.png',
  'wait 55','netevent sourceimplosioncheck 0','screenshot logs/07-glow-100.png',
  'wait 35','screenshot logs/08-glow-135.png','wait 35','screenshot logs/09-collapse.png',
  'wait 90','netevent sourceimplosioncheck 4','netevent sourcematerialcheck','netevent sourceenergycheck','echo UTNT_TEST_END','wait 3','quit']
 r=run_case(a.engine,a.iwad,root=W,mod=a.mod,addon=ROOT/'tools/source-tests',mapname='TNT04CN',renderer=a.renderer,timeout=200,label='source-energy',commands='; '.join(cmd),
 settings=[('win_w',1298),('win_h',767),('screenblocks',12),('con_notifytime',0),('r_drawplayersprites','false'),('crosshair',0),('vid_maxfps',60),('i_pauseinbackground','false'),('vid_activeinbackground','true'),('UTNT_fxquality',3),('UTNT_reducedfx','false'),('UTNT_shaderoverlayswitch','true')])
 if r['assertions']<17:r['ok']=False;r['errors'].append('missing energy assertions')
 (W/'runtime.json').write_text(json.dumps(r,indent=2)+'\n');return 0 if r['ok'] else 1
if __name__=='__main__':raise SystemExit(main())
