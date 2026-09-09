"""Campaign coverage, animation/script changes, save/load and rune cleanup."""
from pathlib import Path
import argparse,json,os,sys
R=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--root',type=Path,default=R)
p.add_argument('--fixture',type=Path,default=Path(__file__).with_name('ritual-tests'))
p.add_argument('--mod',type=Path)
p.add_argument('--out',type=Path,required=True)
p.add_argument('--engine',default=os.environ.get('UTNT_ENGINE','F:/DoomDev/uzdoom.exe'))
p.add_argument('--iwad',default=os.environ.get('UTNT_IWAD','F:/DoomDev/DOOM2.WAD'))
p.add_argument('--campaign',action='store_true')
p.add_argument('--renderer',choices=['0','1','both'],default='both')
a=p.parse_args();W=a.out.resolve();W.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(a.root/'tools'));from check_engine import run_case
results=[]
base='god; notarget; noclip; fly; wait 100; netevent ritualtest 0; wait 100; netevent ritualtest 3; '
full=('netevent ritualtest 1; wait 15; save ritual-active; wait 15; load ritual-active; wait 100; '
      'netevent ritualtest 2; netevent ritualtest 5; wait 80; netevent ritualtest 4; '
      'netevent ritualtest 6; wait 100; netevent ritualtest 3; '
      'UTNT_fxquality 0; wait 100; netevent ritualtest 4; ')
cases=[('TNT01',r,True) for r in (['0','1'] if a.renderer=='both' else [a.renderer])]
if a.campaign:cases += [(m,'1',False) for m in ['TNT02','TNT03A2','TNT04A','TNT04B','TNT04C','TNT04CN','TNTLE']]
for mapname,renderer,detailed in cases:
 commands=base+(full if detailed else '')+'wait 10; echo UTNT_TEST_END; quit\n'
 r=run_case(a.engine,a.iwad,root=W,mod=a.mod or a.root/'tutnt',addon=a.fixture,mapname=mapname,
  label='ritual-'+mapname+'-'+renderer,renderer=renderer,timeout=90,commands=commands,
  settings=[('vid_maxfps',60),('i_pauseinbackground',False),('use_mouse',False),('use_joystick',False)])
 log=Path(r['log']).read_text(encoding='utf-8')
 r['ok']=r['ok'] and r['assertions']>=(50 if detailed else 5) and 'runes emitted' in log
 if detailed:r['ok']=r['ok'] and log.count('runes disabled and cleaned up')==2
 results.append(r)
 (W/'results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
 assert r['ok'],r
