from pathlib import Path
import sys,json
r=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(r/'tools'))
from check_engine import run_case
import argparse,os
p=argparse.ArgumentParser();p.add_argument('--mod',type=Path,default=r/'tutnt.pk3');p.add_argument('--renderer',choices=['0','1'],default='0');args=p.parse_args()
renderer=args.renderer
label='ambientwater-v2-'+renderer
commands=f'''unbindall;wait 150;vid_setsize 1600 1000;wait 35;event awcheck 1;screenshot logs/{label}-water.png;netevent awsplash;wait 6;screenshot logs/{label}-splash.png;netevent awoff;wait 150;event awcheck 0;netevent awon;wait 140;event awcheck 1;netevent awsmoke;wait 190;event awcheck 1;screenshot logs/{label}-smoke.png;save {label};wait 10;UTNT_ambientsmoke false;wait 40;event awcheck 0;UTNT_ambientsmoke true;wait 160;event awcheck 1;UTNT_fxquality 0;wait 40;event awcheck 0;UTNT_fxquality 1;wait 170;event awcheck 1;UTNT_fxquality 3;netevent awoff;wait 210;event awcheck 0;netevent awon;wait 160;event awcheck 1;netevent awremove;wait 40;event awcheck 0;load {label};wait 190;event awcheck 1;netevent awremove;wait 45;netevent awland;wait 14;screenshot logs/{label}-landing-14.png;wait 4;screenshot logs/{label}-landing-18.png;wait 4;screenshot logs/{label}-landing-22.png;wait 25;event awlandingcheck;netevent awsmall;wait 3;event awsmallcheck;echo UTNT_REGRESSION_COMPLETE;echo UTNT_TEST_END;quit\n'''
result=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],mod=args.mod,addon=r/'tools/ambientwater-tests',mapname='UTNTFIRE',renderer=renderer,label=label,timeout=180,commands=commands,regression=True,settings=[('vid_activeinbackground',True),('vid_lowerinbackground',False),('use_mouse',False),('use_joystick',False),('i_pauseinbackground',False),('UTNT_fxquality',3),('UTNT_reducedfx',False),('UTNT_lod',2400),('r_drawplayersprites',False)])
if not result['ok']: print(Path(result['log']).read_text()[-7000:])
(r/'logs'/f'{label}-results.json').write_text(json.dumps(result,indent=2))
sys.exit(0 if result['ok'] else 1)
