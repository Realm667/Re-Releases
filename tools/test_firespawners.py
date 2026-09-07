from pathlib import Path
import sys,os,json,subprocess
import argparse
r=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('--mod',type=Path,default=r/'tutnt.pk3');args=p.parse_args()
from check_engine import run_case
pak=args.mod;results=[]
for backend in ['0','1']:
    label='firespawner-final-'+backend
    commands=f'''unbindall;wait 150;vid_setsize 1920 1080;wait 30;event spawnercheck 3;screenshot logs/{label}-active.png;wait 10;save {label};wait 10;netevent spawneroff;wait 85;event spawnercheck 0;screenshot logs/{label}-off.png;wait 10;netevent spawneron;wait 85;event spawnercheck 3;UTNT_fxquality 0;wait 85;event spawnercheck 0;UTNT_fxquality 1;wait 85;event spawnercheck 3;UTNT_fxquality 2;wait 85;event spawnercheck 3;UTNT_fxquality 3;UTNT_reducedfx true;wait 85;event spawnercheck 3;UTNT_reducedfx false;UTNT_lod 10;wait 85;event spawnercheck 0;UTNT_lod 2000;wait 85;event spawnercheck 3;netevent spawnersound;wait 85;event spawnercheck 3;netevent spawnerremove;wait 85;event spawnercheck 2;load {label};wait 100;event spawnercheck 3;screenshot logs/{label}-restored.png;wait 20;echo UTNT_REGRESSION_COMPLETE;echo UTNT_TEST_END;quit\n'''
    res=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],mod=pak,mapname='UTNTFIRE',addon=r/'tools/firespawner-tests',renderer=backend,label=label,timeout=90,commands=commands,regression=True,settings=[('use_mouse',False),('use_joystick',False),('i_pauseinbackground',False),('UTNT_fxquality',3),('UTNT_reducedfx',False),('UTNT_lod',2000),('gl_bloom',True),('r_drawplayersprites',False)])
    results.append(res)
(r/'logs/firespawner-results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
assert all(x['ok'] and x['assertions']==48 for x in results),results
print('FireSpawner lifecycle passed both renderers',flush=True)
env=dict(os.environ)
subprocess.run([sys.executable,str(r/'tools/test_fire.py'),'--mod',str(pak),'--renderer','both','--label','firespawner-torches'],env=env,check=True)
