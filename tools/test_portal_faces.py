"""Verify every portal face owns its oriented effects, including crossing TNT04C."""
from pathlib import Path
import sys,json,argparse
R=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(R/'tools'))
from check_engine import run_case
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=R/'logs/portal-faces');p.add_argument('--engine',type=Path,default=R/'engine/uzdoom.exe');p.add_argument('--iwad',type=Path,default=Path('F:/DoomDev/DOOM2.WAD'));p.add_argument('--mod',type=Path,default=R/'tutnt');p.add_argument('--renderer',default='1');p.add_argument('--maps',nargs='+',default=['ENDMAP01','TNT03B','TNT04A','TNT04B','TNT04C','TNT04CN']);p.add_argument('--label',default='source');a=p.parse_args();W=a.out.resolve();W.mkdir(parents=True,exist_ok=True)
results=[]
for name in a.maps:
    commands=['unbindall','god','notarget','wait 100','netevent portalfaces 0','wait 10']
    if name=='TNT04C':
        for offset in [-72,-24,24,72]:
            commands += [f'netevent portalfaces 1 {offset}','wait 60','netevent portalfaces 2','wait 10',f'screenshot logs/{a.label}-{a.renderer}-{offset}.png']
        commands += ['save portal-faces','wait 15','load portal-faces','wait 100','netevent portalfaces 0','netevent portalfaces 1 -72','wait 60','netevent portalfaces 2','wait 10']
    commands+=['echo UTNT_TEST_END','quit']
    r=run_case(a.engine,a.iwad,root=W,mod=a.mod,addon=R/'tools/portal-tests/faces',mapname=name,renderer=a.renderer,label=a.label+'-'+name+'-'+a.renderer,timeout=80,commands='; '.join(commands)+'\n',settings=[('vid_maxfps',60),('i_pauseinbackground',False),('use_mouse',False),('use_joystick',False),('con_notifytime',0)])
    r['ok']=r['ok'] and r['assertions']>3
    results.append(r)
(W/(a.label+'-'+a.renderer+'-results.json')).write_text(json.dumps(results,indent=2),encoding='utf-8')
assert all(r['ok'] for r in results),results
