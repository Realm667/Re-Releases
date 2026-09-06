"""Critical original boss scripts, save/load and both Source finale maps. Not a full playthrough."""
import argparse,json,os,pathlib
from check_engine import ROOT,run_case
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--retry-failed',action='store_true');args=parser.parse_args()
report=ROOT/'logs/campaign-results.json'
results=json.loads(report.read_text()) if args.retry_failed and report.exists() else []
for renderer in ('0','1'):
 for name in ('TNT01','TNT02','TNT03A1','TNT03A2','TNT03B','TNT04B','TNT04C','TNT04CN','TNTLE'):
  label=f'campaign-{name}-{renderer}'
  if args.retry_failed and any(r['label']==label and r['ok'] for r in results):continue
  results=[r for r in results if r['label']!=label]
  ending=name in ('TNT04C','TNT04CN','TNTLE')
  advance='wait 740; +use; wait 5; -use; wait 70; +use; wait 5; -use; wait 175' if ending else 'wait 330'
  cfg=f'wait 155; save {label}; wait 10; load {label}; {advance}; echo UTNT_TEST_END; screenshot logs/{label}.png; wait 5; quit\n'
  r=run_case(pathlib.Path(os.environ['UTNT_ENGINE']),pathlib.Path(os.environ['UTNT_IWAD']),mapname=name,renderer=renderer,addon=ROOT/'tools/campaign-tests',label=label,commands=cfg,timeout=65)
  text=pathlib.Path(r['log']).read_text()
  required=['UTNT_CAMPAIGN_SAVE_RESTORED','UTNT_CAMPAIGN_GATE_COMPLETE' if name in ('TNT01','TNT02','TNT03A1','TNT03A2','TNT03B','TNT04B') else 'UTNT_CAMPAIGN_ENDING_REACHED']
  missing=[s for s in required if s not in text]
  r['errors']+=missing;r['ok']=r['ok'] and not missing
  results.append(r)
  (ROOT/'logs/campaign-results.json').write_text(json.dumps(results,indent=2))
raise SystemExit(0 if all(r['ok'] for r in results) else 1)
