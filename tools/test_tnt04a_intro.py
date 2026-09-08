from pathlib import Path
import sys,json,argparse,os
from check_engine import run_case,ROOT
p=argparse.ArgumentParser(description="Exercise real Use input, hold prevention, saved intro, and natural completion.")
p.add_argument('--engine',type=Path,default=os.environ.get('UTNT_ENGINE'))
p.add_argument('--iwad',type=Path,default=os.environ.get('UTNT_IWAD'))
p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
p.add_argument('--work',type=Path,default=ROOT)
p.add_argument('--case',choices=['early','held','saved','normal'],action='append')
a=p.parse_args()
if not a.engine or not a.iwad:p.error('Configure engine and IWAD')
R=ROOT;W=a.work;W.mkdir(parents=True,exist_ok=True)

cases={
'early':['wait 35','netevent introstage 0','wait 10','screenshot logs/intro-early-hint.png','+use','wait 5','-use','wait 35','netevent introstage 1','netevent introvoice','wait 175','netevent introobjectives','screenshot logs/intro-early-skipped.png','save intro-complete','wait 70','load intro-complete','wait 70','netevent introstage 1'],
'held':['+use','wait 70','netevent introstage 0','-use','wait 15','+use','wait 5','-use','wait 35','netevent introstage 1','netevent introvoice'],
'saved':['wait 300','netevent introstage 0','save intro-pending','wait 70','load intro-pending','wait 70','netevent introstage 0','+use','wait 5','-use','wait 35','netevent introstage 1','netevent introvoice','wait 175','netevent introobjectives'],
'normal':['wait 35','netevent introstage 0','wait 1950','netevent introstage 1','wait 175','netevent introobjectives','+use','wait 5','-use','wait 35','netevent introstage 1']}
results=[]
for name,cmd in cases.items():
 if a.case and name not in a.case:continue
 r=run_case(a.engine,a.iwad,root=W,mod=a.mod,addon=ROOT/'tools/intro-skip-tests',mapname='TNT04A',renderer='1',label='intro-'+name,timeout=120,commands='; '.join(cmd+['wait 10','echo UTNT_TEST_END','wait 5','quit']),settings=[('language','deu'),('win_w',1298),('win_h',767),('con_notifytime',0),('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_maxfps',60)])
 results.append(r);(W/'results.json').write_text(json.dumps(results,indent=2))
 if not r['ok']:print(Path(r['log']).read_text(encoding='utf-8')[-5000:]);break

raise SystemExit(0 if results and all(r["ok"] for r in results) else 1)
