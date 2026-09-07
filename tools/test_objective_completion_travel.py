"""Focused real hub roundtrip and simultaneous-completion queue regression."""
from pathlib import Path
import os,argparse,json
from check_engine import run_case
R=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mode',choices=['hub','queue'],default='hub')
p.add_argument('--mod',type=Path,default=R/'tutnt');a=p.parse_args();label='objectives-completion-'+a.mode
if a.mode=='hub':
    mapname='TNT03A1'
    cmd=['wait 230','event objcompletionresources','puke 211','wait 14','event objprogress 3 1',
        'puke 250 4 1 0','wait 15','event objmap 4','event objprogress 3 3','wait 260','event objqueueempty 2',
        'netevent objreturnhub','wait 15','event objmap 3','event objprogress 3 3','event objqueueempty 1',
        'puke 213','wait 14','event objprogress 3 7','event objnotification 3 3 7',
        '+utnt_objectives','wait 10',f'screenshot logs/{label}.png','wait 3']
else:
    mapname='TNT02'
    cmd=['wait 230','event objcompletionresources','puke 211','wait 2','puke 212','wait 2','puke 213','wait 10',
        'event objprogress 2 7','event objnotification 2 1 1','puke 211','wait 108','event objnotification 2 2 3',
        'wait 119','event objnotification 2 3 7',f'screenshot logs/{label}.png','wait 125','event objqueueempty 3']
cmd+=['echo UTNT_TEST_END','wait 3','quit']
r=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],root=R,mod=a.mod,mapname=mapname,
    addon=R/'tools/objective-completion-tests',label=label,commands='; '.join(cmd)+'\n',timeout=65,regression=True,
    settings=[('language','enu'),('con_notifytime',0),('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_lowerinbackground',False)])
if not r['ok']:print(Path(r['log']).read_text(encoding='utf-8')[-4500:])
(R/'logs'/f'{label}-results.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
raise SystemExit(0 if r['ok'] else 1)
