"""TNT04A shared chapter, original timeline, skip and save regressions. Set UTNT_ENGINE/IWAD."""
from pathlib import Path
import sys, json, argparse
import os
R=Path(__file__).resolve().parent.parent;W=R
from check_engine import run_case
p=argparse.ArgumentParser();p.add_argument('--case',choices=['compile','early','saved','held','normal'],default='compile');p.add_argument('--mod',type=Path,default=R/'tutnt');a=p.parse_args()
cases={
'early': 'wait 40; netevent introstage 0; event introview; screenshot logs/intro-en.png; +use; wait 5; -use; wait 35; netevent introstage 1; netevent introvoice; wait 175; netevent introobjectives; save intro-done; wait 35; load intro-done; wait 70; netevent introstage 1',
'saved': 'wait 80; netevent utnt_chapter 0 4; wait 10; netevent utnt_chapter 1 4; wait 10; netevent introstate; save intro-reader; wait 35; load intro-reader; wait 70; netevent introstate; netevent introstage 0; event introview; screenshot logs/intro-de.png; netevent utnt_chapter 2 4; wait 10; +use; wait 5; -use; wait 35; netevent introstage 1',
'held': '+use; wait 70; netevent introstage 0; -use; wait 15; +use; wait 5; -use; wait 35; netevent introstage 1',
'normal': 'wait 290; netevent introstage 0; netevent intronarration 38; wait 800; netevent intronarration 39; wait 800; netevent introstage 1; wait 175; netevent introobjectives; +use; wait 5; -use; wait 10; netevent introstage 1',
}
name=a.case
result=run_case(Path(os.environ['UTNT_ENGINE']),Path(os.environ['UTNT_IWAD']),root=W,mod=a.mod,addon=R/'tools/intro-chapter-tests',mapname=None if name=='compile' else 'TNT04A',label='intro-'+name,timeout=120,commands=None if name=='compile' else cases[name]+'; wait 10; echo UTNT_TEST_END; wait 5; quit',settings=[('language','deu' if name=='saved' else 'enu'),('win_w',658 if name=='saved' else 1298),('win_h',527 if name=='saved' else 767),('UTNT_uiscale',1.5 if name=='saved' else 1),('con_notifytime',0),('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_maxfps',60)])
(W/'logs'/('intro-result-'+name+'.json')).write_text(json.dumps(result,indent=2))
if not result['ok']:print(Path(result['log']).read_text(encoding='utf-8')[-3500:])
sys.exit(not result['ok'])
