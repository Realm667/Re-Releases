from pathlib import Path
import sys,json
import argparse,os
from weather_visor_engine import run_case
p=argparse.ArgumentParser(description="Production visor, shelter, save/load and skybox tests")
p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent.parent)
p.add_argument('--mod',type=Path)
p.add_argument('--kind',choices=['rain','snow'],default='snow')
p.add_argument('--renderer',choices=['0','1'],default='1')
a=p.parse_args();H=a.root.resolve();kind=a.kind;renderer=a.renderer
addon=Path(__file__).resolve().parent/'weather-visor-tests'
engine=os.environ['UTNT_ENGINE'];iwad=os.environ['UTNT_IWAD']
cmd='wait 100; vid_setsize 1440 810; screenblocks 12; r_drawplayersprites false; crosshair 0; netevent visorphase 1; wait 550; '
cmd+=f'netevent vcheck {0 if kind=="rain" else 1}; netevent visorstats; netevent vcheck 7; screenshot logs/visor-{kind}-{renderer}-storm.png; '
if kind=='rain':cmd+='netevent vsnapshot; wait 45; netevent vcheck 6; '
cmd+='freeze; wait 3; netevent vsnapshot; wait 35; netevent vcheck 4; freeze; wait 3; '
cmd+=f'netevent vsnapshot; wait 2; save visor-{kind}-{renderer}; wait 15; netevent visorphase 2; wait 80; load visor-{kind}-{renderer}; wait 3; netevent vcheck 5; '
cmd+='netevent visorphase 2; wait 20; netevent vsnapshot; netevent vcheck 8; wait 35; netevent vcheck 2; '
cmd+=f'screenshot logs/visor-{kind}-{renderer}-shelter.png; wait 245; netevent vcheck 3; listuniforms utnt_visor; echo UTNT_TEST_END; wait 3; quit;\n'
r=run_case(engine,iwad,root=H,mod=a.mod or H/'tutnt.pk3',addon=addon,label='visor-'+kind+'-'+renderer,mapname='TNT02' if kind=='rain' else 'TNT03A1',renderer=renderer,commands=cmd,timeout=95,settings=[('weatherfx',True),('UTNT_fxquality',3),('UTNT_lod',2048),('UTNT_atmosphere',False),('motionblur',False),('con_notifytime',0),('vid_activeinbackground',True),('vid_lowerinbackground',False),('i_pauseinbackground',False)])
(H/'logs'/('result-'+kind+'-'+renderer+'.json')).write_text(json.dumps(r,indent=2))
if not r['ok']:print(Path(r['log']).read_text(encoding='utf-8')[-6000:])
assert r['ok']
