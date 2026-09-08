"""Portal lifecycle and campaign smoke checks in isolated UZDoom profiles."""
from pathlib import Path
import argparse,json,os
from check_engine import run_case
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
p.add_argument('--out',type=Path,default=ROOT/'logs/portal-tests')
p.add_argument('--engine',type=Path,default=os.environ.get('UTNT_ENGINE',ROOT/'engine/uzdoom.exe'))
p.add_argument('--iwad',type=Path,default=os.environ.get('UTNT_IWAD','F:/DoomDev/DOOM2.WAD'))
p.add_argument('--renderer',choices=['0','1','both'],default='both')
p.add_argument('--campaign',action='store_true')
a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
fixture=ROOT/'tools/portal-tests';results=[]
commands='; '.join(['unbindall','wait 70','netevent portest 0','wait 30','netevent portest 1','wait 30','netevent portest 2','wait 60','UTNT_fxquality 0','wait 60','netevent portest 3','wait 25','UTNT_fxquality 3','UTNT_reducedfx true','wait 70','netevent portest 4','wait 25','UTNT_reducedfx false','wait 70','save portal-regression','wait 20','load portal-regression','wait 90','netevent portest 5','wait 30','netevent portest 7','wait 60','echo UTNT_TEST_END','quit'])+'\n'
for renderer in ['0','1'] if a.renderer=='both' else [a.renderer]:
 r=run_case(a.engine,a.iwad,root=a.out,mod=a.mod,mapname='PORTEST',addon=fixture/'regression',renderer=renderer,label='portal-lifecycle-'+renderer,timeout=65,commands=commands,settings=[('vid_maxfps',60),('i_pauseinbackground',False),('use_mouse',False),('use_joystick',False)])
 if r['assertions']<50:r['ok']=False;r['errors'].append('missing lifecycle assertions')
 results.append(r)
 if a.campaign:
  for name in ['TNT03B','TNT04A','TNT04B']:
   label='portal-'+name+'-'+renderer
   r=run_case(a.engine,a.iwad,root=a.out,mod=a.mod,mapname=name,addon=fixture/'campaign',renderer=renderer,label=label,timeout=50,commands=f'wait 100; netevent portalprobe; wait 100; screenshot logs/{label}.png; echo UTNT_TEST_END; quit\n',settings=[('vid_maxfps',60),('i_pauseinbackground',False),('use_mouse',False),('use_joystick',False),('gl_bloom',False)])
   results.append(r)
for r in results:
 s=Path(r['log']).read_text()
 if any(x in s.lower() for x in ['shader compilation failed','failed to compile','unable to load shader']):r['ok']=False;r['errors'].append('shader compilation')
(a.out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
assert all(r['ok'] for r in results),results
