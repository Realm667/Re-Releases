"""Runtime checks for TNT04C sky, map isolation, save/load and rendered views."""
import argparse,json,os
from pathlib import Path
from check_engine import run_case,ROOT
P=argparse.ArgumentParser(description=__doc__);P.add_argument('--engine',type=Path,default=os.environ.get('UTNT_ENGINE'));P.add_argument('--iwad',type=Path,default=os.environ.get('UTNT_IWAD'));P.add_argument('--work',type=Path,required=True);P.add_argument('--renderer',default='0');P.add_argument('--mod',type=Path,default=ROOT/'tutnt');a=P.parse_args()
if not a.engine or not a.iwad:P.error('Configure --engine/--iwad or UTNT_ENGINE/UTNT_IWAD')
W=a.work.resolve();W.mkdir(parents=True,exist_ok=True)
import subprocess
original_run=subprocess.run
def diagnostic_run(args,**kwargs):return original_run([*args,'-logfile','logs/live-engine.log'],**kwargs)
subprocess.run=diagnostic_run
cmd=['wait 350','netevent altcheck']
for v in range(1,9):cmd += [f'netevent altview {v}','wait 35',f'screenshot "{(W/f"view{v}.png").as_posix()}"']
cmd+=['netevent altview 1','wait 175',f'screenshot "{(W/"motion.png").as_posix()}"','save altsky','wait 35','load altsky','wait 70','netevent altcheck','map TNT04CN','wait 100','netevent altcheck','map TNT04C','wait 70','netevent altcheck','wait 35','echo UTNT_TEST_END','wait 5','quit']
r=run_case(a.engine,a.iwad,root=W,mod=a.mod,addon=ROOT/'tools/alternate-tests',mapname='TNT04C',renderer=a.renderer,label='alternate-'+a.renderer,timeout=150,commands='; '.join(cmd),settings=[('vid_maxfps',60),('use_mouse','false'),('use_joystick','false'),('i_pauseinbackground','false'),('vid_activeinbackground','true'),('win_w',1298),('win_h',767),('screenblocks',12),('r_drawplayersprites','false'),('con_notifytime',0),('crosshair',0)])
if r['assertions']<20 or "Can't find SkyViewpoint" in Path(r['log']).read_text(encoding='utf-8'):r['ok']=False
(W/'result.json').write_text(json.dumps(r,indent=2),encoding='utf-8')
if not r['ok']:print(Path(r['log']).read_text(encoding='utf-8')[-5000:])
raise SystemExit(0 if r['ok'] else 1)
