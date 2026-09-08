"""Exercise every real INTERMAP destination, including both original finale timelines."""
from pathlib import Path
import argparse,json,os
from check_engine import ROOT,run_case
from compile_ui_fixture import compile_fixture
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--mod',type=Path,default=ROOT/'tutnt');p.add_argument('--episodes',type=int,nargs='+',default=list(range(1,11)))
p.add_argument('--renderer',default='1');a=p.parse_args();addon=compile_fixture();results=[]
routes={1:2,2:3,3:5,4:5,5:6,6:7,7:8,8:88,9:88,10:0}
for ep in a.episodes:
 for secret in ([0,1] if ep==7 else [0]):
  dest=9 if ep==7 and secret else routes[ep];label=f'chapter-route-{ep}-{secret}-{a.renderer}'
  cmd=['wait 20',f'netevent uitcampaign {ep} {secret}','wait 220',f'netevent uitactual {ep} {dest}',
       'event uitchapterview','netevent utnt_chapter 3 1','wait 10',f'netevent uitphase {2 if ep>=8 else 1}']
  if ep>=8:
   cmd+=['wait 150',f'screenshot logs/{label}-finale.png','wait 3']
   cmd+=['wait 1800' if ep==10 else 'wait 2240']
   if ep==10:cmd+=['netevent uitmap 99','netevent uitphase 2',f'screenshot logs/{label}-ending.png']
   else:cmd+=['netevent uitmap 88',f'screenshot logs/{label}-endmap.png']
  else:cmd+=['wait 105',f'netevent uitmap {dest}']
  cmd+=['netevent uitcomplete','wait 3','echo UTNT_TEST_END','wait 3','quit']
  r=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],mod=a.mod,mapname='INTERMAP',addon=addon,
      renderer=a.renderer,label=label,commands='; '.join(cmd)+'\n',timeout=115 if ep>=8 else 35,regression=True,
      settings=[('con_notifytime',0),('i_pauseinbackground',False),('vid_activeinbackground',True)])
  results.append(r);(ROOT/'logs/chapter-route-results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
  if not r['ok']:print(Path(r['log']).read_text(encoding='utf-8')[-5000:]);raise SystemExit(1)
