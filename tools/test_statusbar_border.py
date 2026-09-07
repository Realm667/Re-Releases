"""Capture native reduced-view borders on both renderers and three aspect ratios.
Set UTNT_ENGINE and UTNT_IWAD; optionally pass --mod for a release PK3.
"""
from pathlib import Path
import sys, json, argparse, os, struct

root=Path(__file__).resolve().parent.parent
from check_engine import run_case

parser=argparse.ArgumentParser()
parser.add_argument('--mod',type=Path)
parser.add_argument('--renderer',choices=['0','1','both'],default='both')
parser.add_argument('--label',default='statusbar-border')
args=parser.parse_args()
results=[]
for renderer in ['0','1'] if args.renderer=='both' else [args.renderer]:
    label=f'{args.label}-{renderer}'
    cmds=['wait 400','god','give all','fullhud_stats 0']
    for w,h,sizes in [(1920,1080,[9,7,3,10,11]),(1024,768,[8]),(2560,1080,[8])]:
        cmds.append(f'vid_setsize {w} {h}')
        for size in sizes:
            cmds.extend([f'screenblocks {size}','wait 15',f'screenshot logs/{label}-{w}x{h}-s{size}.png'])
    cmds+=['echo UTNT_TEST_END','wait 5','quit']
    result=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],
        mod=args.mod,mapname='TNT01',renderer=renderer,label=label,timeout=45,commands='; '.join(cmds)+'\n',
        settings=[('i_pauseinbackground',False),('vid_activeinbackground',True),('con_notifytime',0)])
    for w,h,sizes in [(1920,1080,[9,7,3,10,11]),(1024,768,[8]),(2560,1080,[8])]:
        for size in sizes:
            shot=root/'logs'/f'{label}-{w}x{h}-s{size}.png'
            actual=struct.unpack('>II',shot.read_bytes()[16:24]) if shot.exists() else None
            if actual!=(w,h): result['errors'].append(f'Missing or incorrectly sized capture: {shot.name}')
    result['ok']=result['ok'] and not result['errors']
    results.append(result)
(root/'logs'/f'{args.label}-results.json').write_text(json.dumps(results,indent=2)+'\n')
raise SystemExit(0 if all(r['ok'] for r in results) else 1)
