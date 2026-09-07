"""Real ACS completion triggers, saved progress, queue order and exit/hub travel.
Set UTNT_ENGINE / UTNT_IWAD. No test addon is included in the game package.
"""
from pathlib import Path
import os,json,argparse
from check_engine import run_case
R=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--map',default='TNT01');p.add_argument('--lang',default='enu')
p.add_argument('--renderer',default='1');p.add_argument('--mod',type=Path,default=R/'tutnt')
p.add_argument('--all',action='store_true')
a=p.parse_args()
episodes={'TNT01':1,'TNT02':2,'TNT03A1':3,'TNT03A2':3,'TNT03B':4,'TNT04A':5,'TNT04B':6,'TNT04CN':7,'TNT04C':8,'TNTLE':9}
triggers={'TNT01':[(110,1),(111,2)],'TNT02':[(211,1),(212,2),(213,3)],
    'TNT03A1':[(211,1),(212,2),(213,3)],'TNT03A2':[(211,1),(212,2),(213,3)],
    'TNT04B':[(25,1),(24,2)],'TNTLE':[(223,1),(224,2)]}
results=[]
for mapname in episodes if a.all else [a.map]:
    ep=episodes[mapname];label=f'objectives-completion-{mapname}-{a.lang}-{a.renderer}'
    cmd=['wait 230','event objcompletionresources']
    if mapname in triggers:
        mask=0
        for i,(script,row) in enumerate(triggers[mapname]):
            mask|=1<<(row-1)
            cmd += [f'puke {script}','wait 14',f'event objprogress {ep} {mask}',f'event objnotification {ep} {row} {mask}',f'screenshot logs/{label}-goal{row}.png']
            if i==0:
                cmd += ['+utnt_objectives','wait 10',f'screenshot logs/{label}-manual.png','-utnt_objectives','wait 10',
                    f'netevent objremembercompletion {ep}','wait 2',f'save {label}','wait 3',f'load {label}','wait 4',f'event objcompletionrestored {ep}',
                    f'puke {script}','wait 2']
            cmd += ['wait 125']
        cmd += [f'event objqueueempty {len(triggers[mapname])}']
    elif mapname=='TNT03B':
        cmd += ['puke 166','wait 10','netevent objkillboss','wait 20','event objprogress 4 1','event objnotification 4 1 1','wait 125',
            'puke 250 99 0 0','wait 16','event objmap 99','event objprogress 4 3','event objnotification 4 2 3',f'screenshot logs/{label}-exit.png']
    elif mapname=='TNT04A':
        cmd += ['puke 4','wait 14','event objprogress 5 1','wait 125','puke 11','wait 3','puke 11','wait 35',
            'event objprogress 5 3','event objnotification 5 2 3',f'screenshot logs/{label}-consequence.png','wait 125',
            'puke 250 99 0 0','wait 16','event objmap 99','event objprogress 5 7','event objnotification 5 3 7']
    else:
        cmd += ['puke 140','wait 14',f'event objprogress {ep} 1',f'event objnotification {ep} 1 1','wait 125',
            'netevent objkillboss','wait 20',f'event objprogress {ep} 3',f'event objnotification {ep} 2 3',f'screenshot logs/{label}-source.png']
    cmd += ['echo UTNT_TEST_END','wait 3','quit']
    cmd=[step for c in cmd for step in ([c,'wait 3'] if c.startswith('screenshot ') else [c])]
    r=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],root=R,mod=a.mod,mapname=mapname,
        addon=R/'tools/objective-completion-tests',renderer=a.renderer,label=label,commands='; '.join(cmd)+'\n',timeout=65,
        regression=True,settings=[('language',a.lang),('win_w',1298),('win_h',767),('con_notifytime',0),
        ('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_lowerinbackground',False)])
    log=Path(r['log']).read_text(encoding='utf-8')
    if 'Unknown command' in log or 'Objective Accomplished:' in log:
        r['ok']=False;r['errors'].append('legacy completion message or unknown command')
    if not r['ok']:print(log[-5000:])
    results.append(r)
    (R/'logs'/f'{label}-results.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    if not r['ok']:break
raise SystemExit(0 if all(r['ok'] for r in results) else 1)
