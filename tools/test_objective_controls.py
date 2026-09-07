"""Real TNTLE combat, hold/release, menu and save/load regression. Set UTNT_ENGINE / UTNT_IWAD."""
from pathlib import Path
import sys,os,json,argparse
R=Path(__file__).resolve().parent.parent;W=R
sys.path.insert(0,str(R/'tools'))
from check_engine import run_case
p=argparse.ArgumentParser();p.add_argument('--map',default='TNTLE');p.add_argument('--lang',default='deu');p.add_argument('--renderer',default='1');p.add_argument('--mod',type=Path,default=R/'tutnt');p.add_argument('--width',type=int,default=1280);p.add_argument('--height',type=int,default=720)
a=p.parse_args();label=f'objectives-compact-{a.map}-{a.lang}-{a.width}-{a.renderer}'
cmd=['wait 10','event objearly','+utnt_objectives','wait 2','event objheld 1','-utnt_objectives','wait 1','event objheld 0','wait 217','event objshort','event objresources',f'screenshot logs/{label}-auto.png','netevent objammo','wait 2','+attack','wait 20','-attack','event objfired',
     'netevent objremember','wait 2',f'save {label}','wait 5','+utnt_objectives','wait 3','event objheld 1',f'screenshot logs/{label}-held.png',
     '-utnt_objectives','wait 1','event objheld 0',f'screenshot logs/{label}-released.png',
     '+utnt_objectives','wait 2',f'load {label}','wait 4','event objrestored','wait 100','event objexpired',f'screenshot logs/{label}-expired.png',
     '+utnt_objectives','wait 5','event objheld 1',f'screenshot logs/{label}-recall.png','netevent objammo','wait 2','+attack','wait 20','-attack','event objfired',
     'wait 150','event objheld 1','-utnt_objectives','wait 1','event objheld 0',
     'netevent objoldtimer','wait 2','event objexpired',f'screenshot logs/{label}-old-save-expired.png',
     '+utnt_objectives','wait 2','openmenu UTNTOptions','wait 3','event objheld 0',f'screenshot logs/{label}-controls.png',
     'echo UTNT_TEST_END','wait 2','quit']
# Screenshots are captured at frame end; keep the requested view alive until then.
cmd=[step for command in cmd for step in ([command,'wait 3'] if command.startswith('screenshot ') else [command])]
r=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],root=W,mod=a.mod,mapname=a.map,
    addon=R/'tools/objective-controls-tests',label=label,renderer=a.renderer,commands='; '.join(cmd)+'\n',timeout=90,regression=True,
    settings=[('language',a.lang),('con_notifytime',0),('win_w',a.width+18),('win_h',a.height+47),('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_lowerinbackground',False)])
log=Path(r['log']).read_text(encoding='utf-8')
if 'Unknown command' in log:r['ok']=False;r['errors'].append('unknown command')
(W/'logs'/f'{label}-results.json').write_text(json.dumps(r,indent=2)+'\n')
if not r['ok']:print(log[-4500:])
raise SystemExit(0 if r['ok'] else 1)
