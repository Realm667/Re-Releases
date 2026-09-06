"""German subtitle layout, menu captures and saved voice queue on two aspect ratios."""
import json,os,pathlib
from check_engine import ROOT,run_case
results=[]
for width,height in ((960,540),(1260,540)):
 label=f'subtitle-deu-{width}x{height}'
 cfg=f'wait 60; screenshot logs/{label}.png; save {label}; wait 10; load {label}; wait 350; openmenu UTNTOptions; wait 5; screenshot logs/{label}-menu.png; echo UTNT_TEST_END; wait 5; quit\n'
 r=run_case(pathlib.Path(os.environ['UTNT_ENGINE']),pathlib.Path(os.environ['UTNT_IWAD']),mapname='TNT02',addon=ROOT/'tools/subtitle-review',label=label,commands=cfg,timeout=60,settings=[('language','deu'),('UTNT_subtitlescale','1.5'),('win_w',str(width+18)),('win_h',str(height+47))])
 if 'UTNT_SUBTITLE_COMPLETE' not in pathlib.Path(r['log']).read_text(): r['ok']=False;r['errors'].append('missing subtitle queue completion')
 results.append(r)
(ROOT/'logs/subtitle-results.json').write_text(json.dumps(results,indent=2))
raise SystemExit(0 if all(r['ok'] for r in results) else 1)
