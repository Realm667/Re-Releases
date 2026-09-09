"""Run real-engine expanded-rock checks on every modified map, including save/load."""
import argparse,json
from pathlib import Path
from check_engine import run_case
ROOT=Path(__file__).resolve().parent.parent
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--engine',required=True);p.add_argument('--iwad',required=True)
    p.add_argument('--work-dir',type=Path,required=True);p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
    p.add_argument('--renderer',choices=['0','1'],default='1')
    p.add_argument('--maps',default='TNT01,TNT02,TNT03A1,TNT03A2,TNT04A,TNT04B,TNT04C,TNT04CN,TNTLE')
    a=p.parse_args();a.work_dir.mkdir(parents=True,exist_ok=True)
    fixture=ROOT/'tools/rock-rollout-tests';views=json.loads((fixture/'views.json').read_text());results=[]
    for name in a.maps.split(','):
        label=f'rock-rollout-{name}-{a.renderer}';cmd=['notarget','god','wait 350','screenblocks 10']
        if name=='TNT04A':cmd+=['+use','wait 5','-use','wait 210']
        cmd+=['netevent rockcheck','wait 5']
        for v in [v for v in views if v['map']==name]:cmd += [f'netevent rockview {v["view"]}','wait 15',f'screenshot logs/{label}-{v["material"]}.png']
        cmd += [f'save {label}','wait 20',f'load {label}','wait 50','netevent rockcheck','wait 5','echo UTNT_TEST_END','wait 5','quit']
        r=run_case(a.engine,a.iwad,root=a.work_dir,mod=a.mod,addon=fixture,mapname=name,renderer=a.renderer,label=label,timeout=100,commands='; '.join(cmd),settings=[('win_w',1298),('win_h',787),('vid_maxfps',60),('gl_texture_filter',0),('con_notifytime',0),('screenblocks',10),('r_drawplayersprites',False),('crosshair',0),('UTNT_subtitles',False),('fullhud_fullstats',False),('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_lowerinbackground',False),('use_mouse',False),('use_joystick',False)])
        if r['assertions']!=4:r['ok']=False;r['errors'].append('Expected four mapping/size assertions')
        results.append(r);(a.work_dir/'logs'/f'{label}-result.json').write_text(json.dumps(r,indent=2))
        if not r['ok']:break
    (a.work_dir/f'results-{a.renderer}.json').write_text(json.dumps(results,indent=2))
    return 0 if all(r['ok'] for r in results) else 1
if __name__=='__main__':raise SystemExit(main())
