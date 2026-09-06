"""Real-map key/lock contracts before and after save/load; no route reachability claim."""
import json,os,pathlib
from check_engine import ROOT,run_case
results=[]
for name in ('TNT02','TNT03A1','TNT03A2','TNT04B','TNTLE'):
 label='keys-'+name
 cfg=f'wait 80; save {label}; wait 10; load {label}; wait 70; echo UTNT_TEST_END; wait 5; quit\n'
 r=run_case(pathlib.Path(os.environ['UTNT_ENGINE']),pathlib.Path(os.environ['UTNT_IWAD']),mapname=name,addon=ROOT/'tools/key-tests',label=label,commands=cfg,timeout=40)
 if 'UTNT_KEYS_COMPLETE' not in pathlib.Path(r['log']).read_text():r['ok']=False;r['errors'].append('missing key completion')
 results.append(r)
(ROOT/'logs/key-results.json').write_text(json.dumps(results,indent=2))
raise SystemExit(0 if all(r['ok'] for r in results) else 1)
