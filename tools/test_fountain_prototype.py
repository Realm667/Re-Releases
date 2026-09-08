from pathlib import Path
import sys,json,argparse,os
r=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(r/'tools'))
from check_engine import run_case
p=argparse.ArgumentParser();p.add_argument('--renderer',default='0');p.add_argument('--capture',action='store_true');a=p.parse_args()
label='flow-prototype-'+a.renderer
cmd='wait 150;event flow_check 1;screenshot logs/'+label+'-still.png;'
if a.capture:
 for i in range(64):cmd+=f'wait 2;screenshot logs/fw{i:03d}.png;'
else:
 cmd+=f'netevent flow_off;wait 160;event flow_check 0;netevent flow_on;wait 150;event flow_check 1;save {label};wait 8;load {label};wait 100;event flow_check 1;netevent flow_old;wait 120;screenshot logs/{label}-old.png;netevent flow_new;wait 150;event flow_check 1;'
cmd+='echo UTNT_REGRESSION_COMPLETE;echo UTNT_TEST_END;quit\n'
assert len(cmd)<4096
result=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],mod=r/'tutnt.pk3',addon=r/'tools/fountain-prototype',mapname='UTNTFIRE',renderer=a.renderer,label=label,timeout=100,commands=cmd,regression=True,settings=[('win_w',960),('win_h',540),('vid_activeinbackground',True),('vid_lowerinbackground',False),('i_pauseinbackground',False),('use_mouse',False),('use_joystick',False),('vid_maxfps',60),('screenblocks',12),('r_drawplayersprites',False),('con_notifytime',0),('crosshair',0),('UTNT_fxquality',3),('UTNT_reducedfx',False),('UTNT_lod',2400)])
(r/'logs'/f'{label}-results.json').write_text(json.dumps(result,indent=2))
if not result['ok']:print(Path(result['log']).read_text()[-6000:])
sys.exit(0 if result['ok'] else 1)
