"""Paired outdoor screenshots and reversible atmosphere save/load regression."""
import json,os,pathlib
from check_engine import ROOT,run_case
results=[]
for backend in ('0','1'):
 for name in ('TNT03A1','TNT03A2','TNTLE'):
  label=f'atmosphere-{name}-{backend}'
  cfg=f'wait 70; screenshot logs/{label}-off.png; UTNT_atmosphere true; wait 110; screenshot logs/{label}-on.png; save {label}; wait 10; load {label}; wait 30; UTNT_atmosphere false; wait 40; echo UTNT_TEST_END; wait 5; quit\n'
  r=run_case(pathlib.Path(os.environ['UTNT_ENGINE']),pathlib.Path(os.environ['UTNT_IWAD']),mapname=name,renderer=backend,addon=ROOT/'tools/visual-review',label=label,commands=cfg,timeout=40)
  if 'UTNT_VISUAL_REVIEW_COMPLETE' not in pathlib.Path(r['log']).read_text():r['ok']=False
  results.append(r)
(ROOT/'logs/visual-review-results.json').write_text(json.dumps(results,indent=2))
raise SystemExit(0 if all(r['ok'] for r in results) else 1)
