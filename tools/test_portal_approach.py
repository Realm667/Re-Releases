from pathlib import Path
import sys,json,argparse,os
R=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description="Approach TNT03B via noclip/fly without invoking portal activation.")
p.add_argument('--mod',type=Path,default=R/'tutnt.pk3')
p.add_argument('--out',type=Path,default=R/'logs/portal-approach')
p.add_argument('--engine',type=Path,default=os.environ.get('UTNT_ENGINE',R/'engine/uzdoom.exe'))
p.add_argument('--iwad',type=Path,default=os.environ.get('UTNT_IWAD','F:/DoomDev/DOOM2.WAD'))
p.add_argument('--renderer',choices=['0','1'],default='1')
a=p.parse_args();W=a.out.resolve();W.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'tools'))
from check_engine import run_case
commands='god; notarget; noclip; fly; wait 150; netevent portalapproach 0 1; wait 70; screenshot logs/direct.png; netevent portalapproach 4 1; wait 70; netevent portalapproach 5 1; wait 70; netevent portalapproach 2 0; wait 70; netevent portalapproach 4 0; wait 70; save portal-manual-off; wait 15; load portal-manual-off; wait 70; netevent portalapproach 0 0; wait 70; netevent portalapproach 3 1; wait 70; UTNT_fxquality 0; wait 70; netevent portalapproach 0 0; wait 70; UTNT_fxquality 3; wait 70; netevent portalapproach 0 1; wait 70; save portal-local-on; wait 15; load portal-local-on; wait 70; netevent portalapproach 0 1; wait 70; echo UTNT_TEST_END; quit\n'
r=run_case(a.engine,a.iwad,root=W,mod=a.mod,addon=R/'tools/portal-tests/approach',mapname='TNT03B',renderer=a.renderer,label='direct-'+(a.renderer),timeout=100,commands=commands,settings=[('vid_maxfps',60),('i_pauseinbackground',False),('use_mouse',False),('use_joystick',False),('con_notifytime',0)])
s=Path(r['log']).read_text(encoding='utf-8')
assert 'benötigt diese Dateien' not in s and s.count('TNT03B - The Evil Heart')==3,s[-1200:]
assert r['ok'] and r['assertions']==10,r
(W/(r['label']+'-result.json')).write_text(json.dumps(r,indent=2),encoding='utf-8')
