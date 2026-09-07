"""Verify real OPEN-script dispatch, including both Cursed Peak maps and TNT04A."""
from test_objectives import W,R,ENGINE,IWAD,run_case
import json,os,argparse
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mod',type=Path,default=R/'tutnt')
mod=p.parse_args().mod
results=[]
cases=[('TNT01',1),('TNT02',2),('TNT03A1',3),('TNT03A2',0),('TNT03B',4),('TNT04A',5),
       ('TNT04B',6),('TNT04C',8),('TNT04CN',7),('TNTLE',9)]
for mapname,episode in cases:
    label='objectives-natural-'+mapname
    cmds='wait 230; '
    if mapname=='TNT04A': cmds+='event objcheck 0; wait 1840; '
    cmds+=f'event objcheck {episode}; screenshot logs/{label}.png; echo UTNT_TEST_END; wait 3; quit\n'
    r=run_case(ENGINE,IWAD,root=W,mod=mod,addon=R/'tools/objectives-tests',mapname=mapname,label=label,
               commands=cmds,timeout=110,settings=[('language','deu'),('con_notifytime',0),
                 ('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_lowerinbackground',False)])
    results.append(r)
    (W/'logs/objective-mapstart-results.json').write_text(json.dumps(results,indent=2)+'\n')
raise SystemExit(0 if all(r['ok'] for r in results) else 1)
