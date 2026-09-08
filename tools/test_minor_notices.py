"""Focused native notice delivery, key-use, layout and recipient regressions."""
from pathlib import Path
import os,json,argparse
from check_engine import run_case
R=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('--lang',default='enu');p.add_argument('--renderer',default='1')
p.add_argument('--mode',choices=['notices','locks'],default='notices');p.add_argument('--mod',type=Path,default=R/'tutnt')
a=p.parse_args();label=f'minor-notices-{a.mode}-{a.lang}-{a.renderer}'
cmd=['wait 230','event ntresources','event ntreset']
if a.mode=='notices':
 cmd += ['puke 10','wait 3','event ntactive 200 0','event ntfade 1','wait 6','event ntfade 0',f'screenshot logs/{label}-door.png',
    'puke 10','wait 2','event ntactive 200 0','netevent ntsend 198 0 -1','wait 2','event ntactive 200 1',
    'netevent ntsend 198 0 -1','wait 2','event ntactive 200 1','wait 175','event ntactive 198 0',f'screenshot logs/{label}-dungeons.png',
    'event ntreset','netevent ntsend 198 1 -1','wait 3','event ntactive 0','netevent ntsend 198 -1 -1','wait 3','event ntactive 0',
    'netevent ntsend 198 -2 -1','wait 9','event ntactive 198 0',
    'event ntreset','puke 136','wait 9','event ntactive 226 0','event ntvalue 24','puke 136','wait 9','event ntactive 226 0','event ntvalue 23',f'screenshot logs/{label}-coins.png',
    '+utnt_objectives','wait 15',f'screenshot logs/{label}-objectives.png','-utnt_objectives','wait 10','event ntactive 226 0',
    f'save {label}','wait 3',f'load {label}','wait 35','event ntactive 0',
    'event ntpreview 328','wait 9','event ntactive 328 0',f'screenshot logs/{label}-long.png','wait 190','event ntactive 0']
else:
 for lock in range(1,7):
  cmd+=['event ntreset',f'netevent ntlock {lock} 13 0','wait 3','netevent ntuse','wait 2','wait 8',
        f'event ntactive {1000+lock*2} 0','event ntdenied',f'screenshot logs/{label}-key{lock}.png',
        'event ntreset',f'netevent ntlock {lock} 13 {lock}','wait 3','netevent ntuse','wait 2','wait 5','event ntaccepted','event ntactive 0']
 for lock,special,owned in [(5,83,0),(4,85,0),(2,12,0),(5,13,2),(133,13,2),(129,13,4)]:
  remote=int(special==83);deny=owned==0 or lock==5
  cmd+=['event ntreset',f'netevent ntlock {lock} {special} {owned}','wait 3','netevent ntuse','wait 2','wait 8']
  cmd+=[f'event ntactive {1000+lock*2+remote} 0','event ntdenied'] if deny else ['event ntaccepted','event ntactive 0']
cmd+=['echo UTNT_TEST_END','wait 3','quit']
cmd=[step for c in cmd for step in ([c,'wait 3'] if c.startswith('screenshot ') else [c])]
r=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],root=R,mod=a.mod,mapname='TNT02',addon=R/'tools/minor-notice-tests',
 label=label,renderer=a.renderer,commands='; '.join(cmd)+'\n',timeout=80,regression=True,
 settings=[('language',a.lang),('win_w',1306),('win_h',791),('con_notifytime',0),('i_pauseinbackground',False),('vid_activeinbackground',True)])
if not r['ok']:print(Path(r['log']).read_text(encoding='utf-8')[-5500:])
(R/'logs'/f'{label}-results.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
raise SystemExit(0 if r['ok'] else 1)
