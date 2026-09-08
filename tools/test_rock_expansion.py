"""Verify the integrated main package, with test-only mapping checks and cameras."""
import argparse,json
from pathlib import Path
from check_engine import run_case
ROOT=Path(__file__).resolve().parent.parent

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--engine',required=True);p.add_argument('--iwad',required=True)
    p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
    p.add_argument('--work-dir',type=Path,required=True)
    p.add_argument('--renderer',choices=['0','1','both'],default='both')
    a=p.parse_args();a.work_dir.mkdir(parents=True,exist_ok=True)
    results=[]
    for renderer in (['0','1'] if a.renderer=='both' else [a.renderer]):
        label='rock-integrated-'+renderer
        commands=['notarget','god','wait 350','screenblocks 10','netevent rockcheck','wait 5']
        for view in [3,1,5]:
            commands += [f'netevent rockview {view}','wait 35',f'screenshot logs/{label}-view{view}.png']
        commands += [f'save {label}','wait 35',f'load {label}','wait 70','netevent rockcheck','wait 5','echo UTNT_TEST_END','wait 5','quit']
        result=run_case(a.engine,a.iwad,root=a.work_dir,mod=a.mod,
            addon=ROOT/'tools/rock-expansion-tests',mapname='TNT04B',renderer=renderer,
            label=label,timeout=90,commands='; '.join(commands),settings=[
                ('win_w',1618),('win_h',947),('vid_maxfps',60),('gl_texture_filter',0),
                ('con_notifytime',0),('screenblocks',10),('r_drawplayersprites',False),
                ('crosshair',0),('UTNT_subtitles',False),('fullhud_fullstats',False),
                ('i_pauseinbackground',False),('vid_activeinbackground',True),
                ('vid_lowerinbackground',False),('use_mouse',False),('use_joystick',False)])
        if result['assertions']!=4:
            result['ok']=False;result['errors'].append('Expected four mapping/size assertions across save/load')
        results.append(result)
    (a.work_dir/'results.json').write_text(json.dumps(results,indent=2))
    return 0 if all(r['ok'] for r in results) else 1

if __name__=='__main__':raise SystemExit(main())
