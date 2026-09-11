"""Check black collapse smoke onset, save restoration and bounded quality budgets."""
from pathlib import Path
import argparse,json
from check_engine import ROOT,run_case

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('engine','iwad','mod','work'):p.add_argument('--'+name,type=Path,required=True)
 p.add_argument('--maps',nargs='+',choices=['TNT04CN','TNT04C'],default=['TNT04CN','TNT04C'])
 p.add_argument('--renderers',nargs='+',choices=['0','1'],default=['0','1'])
 a=p.parse_args();W=a.work.resolve();W.mkdir(parents=True,exist_ok=True);results=[]
 cmd=['wait 450','netevent sourceview 4','wait 10','netevent sourcekill','wait 90',
  'save before-black','wait 3','load before-black','wait 35','wait 20','netevent sourceblackcheck 0','screenshot logs/01-before.png',
  'wait 16','netevent sourceblackcheck 6 1','screenshot logs/02-birth.png',
  'wait 10','netevent sourceblackcheck 6','screenshot logs/03-burst.png','save black-cloud',
  'wait 3','load black-cloud','wait 20','netevent sourceblackcheck 6','screenshot logs/04-restored.png',
  'UTNT_reducedfx true','wait 5','netevent sourceblackcheck 2','UTNT_fxquality 0','wait 5','netevent sourceblackcheck 0',
  'UTNT_reducedfx false','UTNT_fxquality 1','wait 5','netevent sourceblackcheck 3','UTNT_fxquality 3','wait 5','netevent sourceblackcheck 6',
  'wait 5','netevent sourceblackcheck 6','screenshot logs/05-fade.png',
  'wait 20','netevent sourceblackcheck 0','wait 15','netevent sourceblackcheck 0','screenshot logs/06-empty.png',
  'echo UTNT_TEST_END','wait 3','quit']
 for mapname in a.maps:
  for renderer in a.renderers:
   out=W/f'{mapname.lower()}-{renderer}';out.mkdir(exist_ok=True)
   r=run_case(a.engine,a.iwad,root=out,mod=a.mod,addon=ROOT/'tools/source-tests',mapname=mapname,renderer=renderer,
    timeout=120,label='black-burst',commands='; '.join(cmd),settings=[('win_w',1298),('win_h',767),('screenblocks',12),('con_notifytime',0),('r_drawplayersprites',False),('crosshair',0),('vid_maxfps',60),('i_pauseinbackground',False),('vid_activeinbackground',True),('use_mouse',False),('UTNT_fxquality',3),('UTNT_reducedfx',False)])
   r.update(map=mapname,renderer=renderer);results.append(r)
   (W/'runtime.json').write_text(json.dumps(results,indent=2)+'\n')
   if not r['ok'] or r['assertions']<40:return 1
 return 0
if __name__=='__main__':raise SystemExit(main())
