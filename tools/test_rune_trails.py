"""Trail ownership, fade, cleanup and save/load in actual portal/teleporter maps."""
from pathlib import Path
import argparse,json,sys,os
R=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--root',type=Path,default=R);p.add_argument('--out',type=Path,required=True)
p.add_argument('--fixture',type=Path,default=Path(__file__).with_name('rune-trail-tests'))
p.add_argument('--mod',type=Path);p.add_argument('--renderer',choices=['0','1','both'],default='both')
p.add_argument('--engine',default=os.environ.get('UTNT_ENGINE','F:/DoomDev/uzdoom.exe'))
p.add_argument('--iwad',default=os.environ.get('UTNT_IWAD','F:/DoomDev/DOOM2.WAD'))
a=p.parse_args();sys.path.insert(0,str(a.root/'tools'));from check_engine import run_case
W=a.out.resolve();W.mkdir(parents=True,exist_ok=True);results=[]
for renderer in (['0','1'] if a.renderer=='both' else [a.renderer]):
 for mapname in ['TNT03B','TNT01']:
  label='trail-'+mapname+'-'+renderer
  cmd='god; notarget; noclip; fly; wait 220; netevent runetrail 1; wait 10; screenshot logs/'+label+'.png; save rune-trails; wait 15; load rune-trails; wait 100; netevent runetrail 1; wait 10; UTNT_fxquality 0; wait 15; netevent runetrail 0; wait 10; echo UTNT_TEST_END; quit\n'
  r=run_case(a.engine,a.iwad,root=W,mod=a.mod or a.root/'tutnt',addon=a.fixture,mapname=mapname,label=label,renderer=renderer,timeout=120,commands=cmd,settings=[('vid_maxfps',60),('i_pauseinbackground',False),('use_mouse',False),('use_joystick',False),('con_notifytime',0)])
  log=Path(r['log']).read_text(encoding='utf-8');r['ok']=r['ok'] and log.count('TRAIL_COUNTS')==3 and 'shader compilation failed' not in log.lower()
  results.append(r);(W/'results.json').write_text(json.dumps(results,indent=2))
  assert r['ok'],r
