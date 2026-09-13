"""Exercise grass placement, material/moving-floor safety, quality and save/load in UZDoom."""
from pathlib import Path
import argparse,json
from check_engine import run_case,ROOT

def run(engine,iwad,mod,mapname='TNTLE',renderer='1',addon=None):
    label=f'grass-{mapname}-{renderer}'
    commands=['unbindall','god','notarget','vid_setsize 1280 720','wait 220','netevent grasscheck','netevent grassinvalid',
      'netevent grasshide 1','wait 12',f'screenshot logs/{label}-before.png','netevent grasshide 0','wait 15',f'screenshot logs/{label}-after.png',
      f'save {label}','wait 15',f'load {label}','wait 160','netevent grasscheck 1',
      'UTNT_fxquality 0','wait 20','netevent grassoff','UTNT_fxquality 3','wait 160','netevent grasscheck 1',
      f'screenshot logs/{label}-restored.png','echo UTNT_TEST_END','wait 5','quit']
    if mapname.upper()=='TNT02':
        commands=['unbindall','god','notarget','vid_setsize 1280 720','con_notifytime 0','wait 20',
          'netevent grasscamera -5056 672 370','netevent grassturn -90 10','wait 220','netevent grassmario',
          f'screenshot logs/{label}-excluded.png',f'save {label}','wait 15',f'load {label}','wait 160',
          'netevent grassmario','UTNT_fxquality 0','wait 20','netevent grassoff','UTNT_fxquality 3','wait 160',
          'netevent grassmario','echo UTNT_TEST_END','wait 5','quit']
    return run_case(engine,iwad,mod=mod,mapname=mapname,renderer=renderer,addon=addon or ROOT/'tools/fixtures/grass',label=label,
      commands='; '.join(commands)+'\n',timeout=90,settings=[('UTNT_fxquality',3),('UTNT_lod',2048),('UTNT_reducedfx','false'),('UTNT_distanceblur',0)])
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--engine',type=Path,default=Path('F:/DoomDev/uzdoom.exe'));p.add_argument('--iwad',type=Path,default=Path('F:/DoomDev/DOOM2.WAD'))
    p.add_argument('--addon',type=Path);p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3');p.add_argument('--map',default='TNTLE');p.add_argument('--renderer',default='1')
    a=p.parse_args();r=run(a.engine,a.iwad,a.mod,a.map,a.renderer,a.addon)
    if not r['ok']:print(Path(r['log']).read_text()[-6500:])
    raise SystemExit(not r['ok'])
