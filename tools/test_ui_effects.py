"""Targeted five-tic heat update, source cleanup and subtitle save/load on both renderers."""
from pathlib import Path
import argparse,json,os
from check_engine import ROOT,run_case
from compile_ui_fixture import compile_fixture
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mod',type=Path,default=ROOT/'tutnt');a=p.parse_args()
addon=compile_fixture();results=[]
for renderer in ('0','1'):
 label='ui-heat-runtime-'+renderer
 commands=f'wait 230; netevent uitheat; wait 20; save {label}; wait 5; load {label}; wait 50; profilethinkers -t 12; profilecsthinkers -t 12; netevent uitcomplete; wait 5; echo UTNT_TEST_END; wait 5; quit\n'
 r=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],mod=a.mod,mapname='TNT02',addon=addon,renderer=renderer,
    label=label,commands=commands,timeout=35,regression=True,settings=[('i_pauseinbackground',False),('vid_activeinbackground',True)])
 if 'UTNT_UI_HEAT_COMPLETE' not in Path(r['log']).read_text(encoding='utf-8'):r['ok']=False
 results.append(r)
 if not r['ok']:print(Path(r['log']).read_text(encoding='utf-8')[-4500:]);raise SystemExit(1)
label='ui-subtitle-persistence'
commands=f'wait 60; screenshot logs/{label}.png; save {label}; wait 10; load {label}; wait 350; echo UTNT_TEST_END; wait 5; quit\n'
r=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],mod=a.mod,mapname='TNT02',addon=ROOT/'tools/subtitle-review',label=label,commands=commands,timeout=40,
 settings=[('language','deu'),('UTNT_subtitlescale',1.5),('i_pauseinbackground',False),('vid_activeinbackground',True)])
if 'UTNT_SUBTITLE_COMPLETE' not in Path(r['log']).read_text(encoding='utf-8'):r['ok']=False
results.append(r)
(ROOT/'logs/ui-additional-results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
raise SystemExit(0 if r['ok'] else 1)
