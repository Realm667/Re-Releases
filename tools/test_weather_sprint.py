from pathlib import Path
import sys,json,os,argparse
R=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(R/'tools'))
from check_engine import run_case
parser=argparse.ArgumentParser(description='Verify weather coverage during a sprint and reversal.')
parser.add_argument('--mod',type=Path)
a=parser.parse_args()
results=[]
for backend in ['0','1']:
    for name in ['WXRAIN','WXSNOW']:
        label=f'weather-sprint-{name}-{backend}'
        swatch=f'event swatches; wait 3; screenshot logs/weather-gray-{backend}.png;' if name=='WXRAIN' else ''
        r=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],root=R,mod=a.mod,addon=R/'tools/weather-sprint-tests',mapname=name,renderer=backend,label=label,regression=True,timeout=65,
            commands=f'wait 480; event sprintcheck; screenshot logs/{label}.png; {swatch} echo UTNT_TEST_END; wait 5; quit\n',
            settings=[('weatherfx',True),('UTNT_fxquality',3),('UTNT_lod',2048),('UTNT_reducedfx',False),('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_lowerinbackground',False),('vid_maxfps',120),('con_notifytime',0)])
        results.append(r)
        if not r['ok']:
            print(Path(r['log']).read_text(encoding='utf-8')[-3500:]);break
(R/'logs/weather-sprint-results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
assert len(results)==4 and all(r['ok'] for r in results),results
