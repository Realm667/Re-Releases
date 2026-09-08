"""SteamSpawner lifecycle, local quality and wall/3D-floor checks on UZDoom.

Set UTNT_ENGINE / UTNT_IWAD. Run python tools/test_steam.py --mod tutnt.pk3.
"""
from pathlib import Path
import argparse,json,os
from check_engine import run_case

ROOT=Path(__file__).resolve().parent.parent
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
    p.add_argument('--renderer',choices=['0','1','both'],default='both')
    p.add_argument('--label',default='steam')
    p.add_argument('--root',type=Path,default=ROOT,help='Output root for logs/screenshots')
    p.add_argument('--fixture',type=Path,default=ROOT/'tools/steam-tests')
    a=p.parse_args();results=[]
    engine=os.environ['UTNT_ENGINE'];iwad=os.environ['UTNT_IWAD']
    checked=run_case(engine,iwad,root=a.root,mod=a.mod,addon=a.fixture,label=a.label+'-compile')
    if not checked['ok']:raise SystemExit('Compile failed: '+checked['log'])
    for backend in (['0','1'] if a.renderer=='both' else [a.renderer]):
        label=a.label+'-'+backend
        commands=f'''wait 160;vid_setsize 1440 900;wait 35;event steamcheck 3;screenshot logs/{label}-active.png;wait 12;screenshot logs/{label}-motion.png;save {label};wait 10;
netevent steamoff;wait 65;event steamcheck 0;netevent steamon;wait 85;event steamcheck 3;
netevent steamoff;wait 2;netevent steamon;wait 2;netevent steamoff;wait 2;netevent steamon;wait 85;event steamcheck 3;
UTNT_fxquality 0;wait 65;event steamcheck 0;UTNT_fxquality 1;wait 85;event steamcheck 3;screenshot logs/{label}-low.png;
UTNT_fxquality 2;wait 85;event steamcheck 3;UTNT_fxquality 3;UTNT_reducedfx true;wait 85;event steamcheck 3;
UTNT_reducedfx false;UTNT_lod 10;wait 65;event steamcheck 0;UTNT_lod 2000;wait 85;event steamcheck 3;
netevent steamremove;wait 65;event steamcheck 2;load {label};wait 85;event steamcheck 3;
netevent steamwall;wait 65;event steamcheck 3;screenshot logs/{label}-wall.png;
load {label};wait 65;netevent steammany;wait 100;event steamcheck 48;screenshot logs/{label}-many.png;
echo UTNT_REGRESSION_COMPLETE;echo UTNT_TEST_END;quit
'''
        commands=commands.replace('\n','')+'\n' # wait queues the remainder of one console line.
        settings=[('use_mouse',False),('use_joystick',False),('i_pauseinbackground',False),('UTNT_fxquality',3),('UTNT_lod',2000),('UTNT_reducedfx',False),('r_drawplayersprites',False),('gl_bloom',False)]
        res=run_case(engine,iwad,root=a.root,mod=a.mod,addon=a.fixture,mapname='UTNTSTM',renderer=backend,label=label,commands=commands,timeout=95,regression=True,settings=settings)
        res['ok']=res['ok'] and res['assertions']==65;results.append(res)
        slab=run_case(engine,iwad,root=a.root,mod=a.mod,addon=a.fixture,mapname='UTNTST3',renderer=backend,label=label+'-3dfloor',commands='wait 160;event steamcheck 3;event steam3dcheck;echo UTNT_REGRESSION_COMPLETE;echo UTNT_TEST_END;quit\n',timeout=35,regression=True,settings=settings)
        slab['ok']=slab['ok'] and slab['assertions']==6;results.append(slab)
    (a.root/'logs'/f'{a.label}-results.json').write_text(json.dumps(results,indent=2)+'\n')
    if not all(r['ok'] for r in results):raise SystemExit('Steam regression failed; see logs')
    print('Steam lifecycle and solid 3D-floor checks passed.')
if __name__=='__main__':main()
