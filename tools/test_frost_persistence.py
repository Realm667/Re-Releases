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
addon=Path(__file__).resolve().parent/'frost-persistence-tests'
engine=os.environ['UTNT_ENGINE'];iwad=os.environ['UTNT_IWAD']
cmd='wait 100; vid_setsize 1440 810; screenblocks 12; r_drawplayersprites false; crosshair 0; netevent visorphase 0; wait 175; netevent vcheck 10; '
if kind=='snow':cmd+='netevent vcheck 9; '
cmd+=f'screenshot logs/response-{kind}-{renderer}-light.png; netevent visorphase 1; wait 350; '
cmd+=f'netevent vcheck {0 if kind=="rain" else 1}; netevent visorstats; netevent vcheck 7; screenshot logs/response-{kind}-{renderer}-storm.png; '
if kind=='rain':cmd+='netevent vsnapshot; wait 45; netevent vcheck 6; netevent vcheck 11; '
if kind=='snow':cmd+='netevent frostmotion 1; wait 150; netevent frostmotioncheck; netevent frostmotion 0; wait 20; '
cmd+='freeze; wait 10; netevent vsnapshot; wait 35; netevent vcheck 4; freeze; wait 10; '
cmd+=f'netevent vsnapshot; wait 2; save response-{kind}-{renderer}; wait 15; netevent visorphase 2; wait 80; load response-{kind}-{renderer}; wait 3; netevent vcheck 5; '
cmd+='netevent captureshelter; netevent visorphase 2; wait 70; netevent checkshelter; netevent vcheck 2; '
cmd+=f'screenshot logs/response-{kind}-{renderer}-shelter.png; wait 245; netevent vcheck 3; listuniforms utnt_visor; echo UTNT_TEST_END; wait 3; quit;\n'
r=run_case(engine,iwad,root=H,mod=a.mod or H/'tutnt.pk3',addon=addon,label='response-'+kind+'-'+renderer,mapname='TNT02' if kind=='rain' else 'TNT03A1',renderer=renderer,commands=cmd,timeout=110,settings=[('weatherfx',True),('UTNT_fxquality',3),('UTNT_lod',2048),('UTNT_atmosphere',False),('motionblur',False),('con_notifytime',0),('vid_activeinbackground',True),('vid_lowerinbackground',False),('i_pauseinbackground',False)])
(H/'logs'/('response-result-'+kind+'-'+renderer+'.json')).write_text(json.dumps(r,indent=2))
if not r['ok']:print(Path(r['log']).read_text(encoding='utf-8')[-6000:])
assert r['ok']
