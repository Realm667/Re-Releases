"""Lost Soul spark lifecycle regression. Requires UTNT_ENGINE and UTNT_IWAD."""
import sys,json,os,argparse
from pathlib import Path
from check_engine import ROOT,run_case
w=ROOT
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
p.add_argument('--renderer',choices=['0','1','both'],default='both')
a=p.parse_args()
results=[]
for backend in (['0','1'] if a.renderer=='both' else [a.renderer]):
    label='lostsoul-'+backend
    commands='; '.join(['unbindall','wait 100','netevent soulgeometry','wait 2','netevent soulview','wait 10','event soulcheck 1',
        f'screenshot logs/{label}-idle.png','netevent soulangle 180','wait 28',
        f'screenshot logs/{label}-side.png','netevent soulangle 90','wait 28',
        f'screenshot logs/{label}-rear.png','netevent soulangle 270','wait 28',
        f'save {label}','wait 5',
        'netevent soulmove 1','wait 12','event soulcheck 1',
        'netevent soulmove 2','wait 14','event soulcheck 1',
        f'screenshot logs/{label}-charge.png','wait 8',
        f'load {label}','wait 40','event soulcheck 1',
        'UTNT_fxquality 0','wait 50','event soulcheck 0',
        'UTNT_fxquality 3','UTNT_reducedfx true','wait 60','event soulcheck 1',
        'UTNT_reducedfx false','UTNT_lod 1','wait 50','event soulcheck 0',
        'UTNT_lod 2000','wait 50','event soulcheck 1',
        'netevent soulkill','wait 55','event soulcheck 0',
        'echo UTNT_REGRESSION_COMPLETE','echo UTNT_TEST_END','quit'])+'\n'
    r=run_case(os.environ['UTNT_ENGINE'],
        os.environ['UTNT_IWAD'],root=w,mod=a.mod,
        addon=ROOT/'tools/lostsoul-tests',mapname='UTNTFIRE',renderer=backend,label=label,
        commands=commands,regression=True,timeout=60,
        settings=[('use_mouse',False),('i_pauseinbackground',False),('screenblocks',12),
          ('UTNT_fxquality',3),('UTNT_reducedfx',False),('UTNT_lod',2000),
          ('gl_texture_filter',0),('con_notifytime',0),('gl_bloom',True),('crosshair',0),('r_drawplayersprites',False)])
    results.append(r)
(w/'logs/lostsoul-results.json').write_text(json.dumps(results,indent=2))
if not all(r['ok'] for r in results):
    for r in results:
        if not r['ok']: print(Path(r['log']).read_text()[-5000:])
    sys.exit(1)
