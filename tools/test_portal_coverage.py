"""Check every UTNT portal wall and local automatic effects, including save/load."""
from pathlib import Path
import argparse,json,os
from check_engine import run_case
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
p.add_argument('--out',type=Path,default=ROOT/'logs/portal-coverage')
p.add_argument('--engine',type=Path,default=os.environ.get('UTNT_ENGINE',ROOT/'engine/uzdoom.exe'))
p.add_argument('--iwad',type=Path,default=os.environ.get('UTNT_IWAD','F:/DoomDev/DOOM2.WAD'))
p.add_argument('--renderer',choices=['0','1','both'],default='1')
a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
fixtures=ROOT/'tools/portal-tests';results=[]
maps={'ENDMAP01':(30,1),'TNT03B':(5,0),'TNT04A':(5,0),'TNT04B':(15,1),'TNT04C':(32,1),'TNT04CN':(30,1),'TNT03A1':(0,0),'TNT03A2':(0,0),'TNTLE':(0,0)}
settings=[('vid_maxfps',60),('i_pauseinbackground',False),('use_mouse',False),('use_joystick',False),('gl_bloom',False),('gl_texture_filter',0)]
for renderer in ['0','1'] if a.renderer=='both' else [a.renderer]:
 for name,(count,autos) in maps.items():
  label='coverage-'+name+'-'+renderer
  r=run_case(a.engine,a.iwad,root=a.out,mod=a.mod,addon=fixtures/'coverage',mapname=name,renderer=renderer,label=label,timeout=60,settings=settings,
   commands=f'unbindall; god; notarget; wait 70; netevent portalcoverage {count} {autos}; wait 80; screenshot logs/{label}.png; save portalcoverage; wait 15; load portalcoverage; wait 70; netevent portalcoverage -1; wait 20; echo UTNT_TEST_END; quit\n')
  if r['assertions']<7:r['ok']=False;r['errors'].append('missing coverage assertions')
  results.append(r)
 label='automatic-'+renderer
 r=run_case(a.engine,a.iwad,root=a.out,mod=a.mod,addon=fixtures/'automatic',mapname='TNT04CN',renderer=renderer,label=label,timeout=65,settings=settings,
  commands=f'unbindall; god; notarget; wait 70; netevent portalcoverage 30 1; wait 80; netevent portalautostate 1; wait 1; screenshot logs/{label}.png; UTNT_fxquality 0; wait 70; netevent portalautostate 0; UTNT_fxquality 3; wait 70; save portal-auto; wait 15; load portal-auto; wait 75; netevent portalcoverage -1; wait 70; netevent portalautostate 1; wait 5; screenshot logs/{label}-restored.png; echo UTNT_TEST_END; quit\n')
 if r['assertions']<14:r['ok']=False;r['errors'].append('missing automatic-effect assertions')
 results.append(r)
(a.out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
assert all(r['ok'] for r in results),results
