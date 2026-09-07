"""Real-engine objectives layout and save/load checks, using isolated configs."""
from pathlib import Path
import sys,json,os,argparse,struct
R=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(R/'tools'))
from check_engine import run_case
W=R
ENGINE=Path(os.environ['UTNT_ENGINE'])
IWAD=Path(os.environ['UTNT_IWAD'])

def run(lang,width,height,renderer='1',mod=None):
    label=f'objectives-{lang}-{width}x{height}-{renderer}'
    cmd=['wait 230','event objcheck 1','event objresources',f'screenshot logs/{label}-map1.png',
         'netevent objremember','wait 3',f'save {label}','wait 5','netevent objshow 2','wait 20',
         f'load {label}','wait 10','event objrestored','netevent objduplicate 1','wait 2','event objrestored',
         'wait 350','event objexpired',f'screenshot logs/{label}-expired.png']
    for mapnum,episode in [(2,2),(3,3),(5,4),(6,5),(7,6),(8,7),(9,8),(10,9)]:
        cmd += [f'netevent objshow {mapnum}','wait 18',f'event objcheck {episode}',f'screenshot logs/{label}-episode{episode}.png']
    cmd += ['UTNT_reducedfx true','netevent objshow 2','wait 20',f'screenshot logs/{label}-reduced.png',
            'echo UTNT_TEST_END','wait 3','quit']
    result=run_case(ENGINE,IWAD,root=W,mod=mod or R/'tutnt',mapname='TNT01',addon=R/'tools/objectives-tests',renderer=renderer,
                   label=label,commands='; '.join(cmd)+'\n',timeout=100,regression=True,
                   settings=[('language',lang),('win_w',width+18),('win_h',height+47),('con_notifytime',0),('screenblocks',11),
                             ('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_lowerinbackground',False)])
    shot=W/'logs'/f'{label}-map1.png'
    actual=struct.unpack('>II',shot.read_bytes()[16:24]) if shot.exists() else None
    if actual!=(width,height): result['errors'].append(f'wrong screenshot size: {actual}')
    if 'Unknown command' in Path(result['log']).read_text(): result['errors'].append('unknown command')
    result['ok']=result['ok'] and not result['errors']
    if not result['ok']: print(Path(result['log']).read_text()[-4500:])
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--lang',default='deu');p.add_argument('--width',type=int,default=1024)
    p.add_argument('--height',type=int,default=768);p.add_argument('--renderer',default='1')
    p.add_argument('--mod',type=Path)
    a=p.parse_args(); result=run(a.lang,a.width,a.height,a.renderer,a.mod)
    (W/'logs'/f"{result['label']}-result.json").write_text(json.dumps(result,indent=2)+'\n')
    raise SystemExit(0 if result['ok'] else 1)
