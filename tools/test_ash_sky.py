"""Real UZDoom TNT04B sky views, natural lightning, motion, save/load and TNT04A guard."""
from pathlib import Path
import argparse,os,json
from check_engine import run_case,ROOT

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--engine',type=Path,default=os.environ.get('UTNT_ENGINE'));p.add_argument('--iwad',type=Path,default=os.environ.get('UTNT_IWAD'))
 p.add_argument('--mod',type=Path,default=ROOT/'tutnt');p.add_argument('--work',type=Path,required=True)
 p.add_argument('--renderer',choices=['0','1','both'],default='both');a=p.parse_args()
 if not a.engine or not a.iwad:p.error('Configure engine and IWAD')
 W=a.work.resolve();W.mkdir(parents=True,exist_ok=True);results=[]
 for renderer in ['0','1'] if a.renderer=='both' else [a.renderer]:
  label='ash-sky-'+renderer;cmd=['wait 350','screenblocks 12']
  for view in [1,2,3,4,5,6,7,8,9]:cmd += [f'netevent ashview {view}','wait 40',f'screenshot "{(W/f"{label}-view{view}.png").as_posix()}"']
  cmd+=['netevent ashview 8','wait 35',f'screenshot "{(W/f"{label}-motion-a.png").as_posix()}"','wait 175',f'screenshot "{(W/f"{label}-motion-b.png").as_posix()}"','netevent ashcheck','netevent ashweather',f'save {label}','wait 70',f'load {label}','wait 140','netevent ashcheck','netevent ashview 1','wait 35',f'screenshot "{(W/f"{label}-loaded.png").as_posix()}"','map TNT04A','wait 35','+use','wait 5','-use','wait 70','netevent ashother','echo UTNT_TEST_END','wait 5','quit']
  r=run_case(a.engine,a.iwad,root=W,mod=a.mod,addon=ROOT/'tools/ash-tests',mapname='TNT04B',renderer=renderer,label=label,timeout=85,commands='; '.join(cmd),settings=[('win_w',1298),('win_h',767),('screenblocks',12),('i_pauseinbackground','false'),('vid_activeinbackground','true'),('vid_maxfps',60),('con_notifytime',0),('r_drawplayersprites','false'),('crosshair',0)])
  log=Path(r['log']).read_text(encoding='utf-8')
  if r['assertions']<18 or 'requires these files' in log or 'Dieser Spielstand ben' in log:r['ok']=False;r['errors'].append('missing assertions or save dependency failure')
  results.append(r);(W/'runtime.json').write_text(json.dumps(results,indent=2)+'\n')
  if not r['ok']:print(log[-5000:]);return 1
 return 0
if __name__=='__main__':raise SystemExit(main())
