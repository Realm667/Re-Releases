"""Validate legacy ray activation, map coverage, saved state and rendered views."""
import argparse
import json
import os
from pathlib import Path
from check_engine import run_case

ROOT=Path(__file__).resolve().parents[1]

def compare_size(output):
    """Measure one isolated shaft against the same scene with all rays hidden."""
    import numpy as np
    from PIL import Image
    frames={k:np.asarray(Image.open(output/'logs'/f'TNT01-size-{k}.png').convert('RGB'),dtype=float)
            for k in ('classic','modern','off')}
    h,w=frames['off'].shape[:2]
    crop=(slice(round(215*h/540),round(440*h/540)),slice(round(435*w/960),round(525*w/960)))
    measurements={}
    for k in ('classic','modern'):
        d=np.maximum(0,frames[k]-frames['off'])[crop].mean(2)
        if d.max()<8 or d.sum()<1:raise AssertionError(f'Missing {k} reference shaft')
        ys,xs=np.indices(d.shape);mass=d.sum();cx=(xs*d).sum()/mass;cy=(ys*d).sum()/mass
        measurements[k]={'width':float(np.sqrt(((xs-cx)**2*d).sum()/mass)),
                         'length':float(np.sqrt(((ys-cy)**2*d).sum()/mass)),
                         'center_x':float(cx),'center_y':float(cy)}
    ratios={axis:measurements['modern'][axis]/measurements['classic'][axis] for axis in ('width','length')}
    ok=all(.92<r<1.08 for r in ratios.values())
    report={'ok':ok,'profiles':measurements,'ratios':ratios}
    (output/'size-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--engine',default=os.environ.get('UTNT_ENGINE','F:/DoomDev/uzdoom.exe'))
    p.add_argument('--iwad',default=os.environ.get('UTNT_IWAD','F:/DoomDev/DOOM2.WAD'))
    p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
    p.add_argument('--output',type=Path,default=ROOT/'tutnt/.codex/validation/light-rays')
    p.add_argument('--renderer',default='1',choices=['0','1'])
    p.add_argument('--maps',nargs='+',default=['TNT01','TNT02'])
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    settings=[('vid_activeinbackground',True),('i_pauseinbackground',False),('con_notifytime',0),
              ('use_mouse',False),('use_joystick',False),('vid_maxfps',60),('screenblocks',10)]
    # Compile the fixture first: startup parse errors otherwise leave a modal
    # engine window waiting until the runtime timeout on Windows.
    compiled=run_case(a.engine,a.iwad,root=a.output,mod=a.mod,
        addon=ROOT/'tools/fixtures/light-rays',label='rays-fixture-compile')
    if not compiled['ok']:
        print(Path(compiled['log']).read_text()[-5000:]);return 1
    results=[]
    for name in a.maps:
        commands=['unbindall','god','wait 150','netevent raycheck 1','wait 15',
                  'netevent raybudget 0',f'screenshot logs/{name}-start.png']
        for i in range(3):
            commands += [f'netevent rayview {i}','wait 60',f'screenshot logs/{name}-view-{i}.png']
        if name=='TNT01':
            commands += ['UTNT_fxquality 0','netevent rayview 3','wait 35',
                         'netevent rayclassic','wait 3','screenshot logs/TNT01-size-classic.png',
                         'netevent raymodern','wait 3','screenshot logs/TNT01-size-modern.png',
                         'netevent rayoff','wait 3','screenshot logs/TNT01-size-off.png',
                         'netevent rayon','UTNT_fxquality 2','wait 20']
        commands += ['save rays-active','wait 5','load rays-active','wait 40','netevent raybudget 0',
                     'netevent rayoff','wait 30','save rays-off','wait 5','load rays-off','wait 25',
                     'netevent rayinactive','netevent rayon','wait 60','netevent raycheck 0','UTNT_reducedfx true','wait 35','netevent raybudget 1',
                     f'screenshot logs/{name}-reduced.png','echo UTNT_TEST_END','wait 3','quit']
        results.append(run_case(a.engine,a.iwad,root=a.output,mod=a.mod,
            addon=ROOT/'tools/fixtures/light-rays',mapname=name,renderer=a.renderer,
            label='rays-'+name,timeout=100,commands='; '.join(commands),settings=settings,regression=True))
    if 'TNT01' in a.maps and all(r['ok'] for r in results):
        comparison=compare_size(a.output)
        results.append({'label':'original-visible-size',**comparison})
    (a.output/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    for r in results:
        if not r['ok']:print(Path(r['log']).read_text()[-5000:] if 'log' in r else r)
    return int(any(not r['ok'] for r in results))

if __name__=='__main__':raise SystemExit(main())
