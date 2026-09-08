"""Combined live UI regressions: notices, objectives, boss, subtitles and chapter reading.
Set UTNT_ENGINE / UTNT_IWAD. Screenshots and machine-readable results go to logs/.
"""
from pathlib import Path
import argparse,json,os
from check_engine import ROOT,run_case
from compile_ui_fixture import compile_fixture
compile_fixture()
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--mod',type=Path,default=ROOT/'tutnt')
p.add_argument('--mode',choices=['hud','chapter','build'],default='hud')
p.add_argument('--width',type=int,default=960);p.add_argument('--height',type=int,default=540)
p.add_argument('--scale',type=float,default=1.0);p.add_argument('--language',default='deu')
p.add_argument('--renderer',default='1');p.add_argument('--episode',type=int,default=5)
a=p.parse_args();label=f'ui-{a.mode}-{a.episode}-{a.language}-{a.width}-{a.scale}-{a.renderer}'
cmd=['wait 230']
if a.mode=='hud':
 cmd+=['event uitnotices','netevent uitmix','wait 25','event uitlayout',f'screenshot logs/{label}-combined.png',
       '+utnt_objectives','wait 10',f'screenshot logs/{label}-objectives.png','-utnt_objectives','wait 10',
       'event uitsecret','wait 15',f'screenshot logs/{label}-secret.png',
       'togglemap','wait 10',f'screenshot logs/{label}-automap.png','togglemap',
       f'save {label}','wait 4',f'load {label}','wait 15','event uitlayout',
       'openmenu UTNTHUDOptions','wait 5',f'screenshot logs/{label}-menu.png','closemenu',
       'netevent uitdeath','wait 3','kill','wait 15',f'screenshot logs/{label}-death.png']
elif a.mode=='chapter':
 cmd+=['netevent uitdestinations',f'netevent uitchapter {a.episode}','wait 10','event uitchapterview',
       '+use','wait 30','-use','wait 10','netevent uitchapterstate 0 1 0',f'screenshot logs/{label}-page1.png',
       f'save {label}','wait 3',f'load {label}','wait 12','netevent uitchapterstate 0 1 0','event uitchapterview',
       'netevent utnt_chapter 1 3','wait 10','netevent uitchapterstate 1 0 0',
       'event uitadvance 1','wait 10','netevent uitchapterstate 0 1 0',
       'UTNT_uiscale 1.5','wait 8','event uitchapterview',f'screenshot logs/{label}-resized.png']
else: cmd+=['event uitbuild','openmenu UTNTHUDOptions','wait 5',f'screenshot logs/{label}-menu.png','closemenu']
cmd+=['netevent uitcomplete','wait 3','echo UTNT_TEST_END','wait 3','quit']
cmd=[step for c in cmd for step in ([c,'wait 3'] if c.startswith('screenshot ') else [c])]
r=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],root=ROOT,mod=a.mod,
 mapname='INTERMAP' if a.mode=='chapter' else 'TNT02',addon=ROOT/'tools/ui-regression-tests',
 label=label,renderer=a.renderer,commands='; '.join(cmd)+'\n',timeout=65,regression=True,
 settings=[('language',a.language),('UTNT_uiscale',a.scale),('UTNT_subtitles',True),('UTNT_subtitlescale',1.5),
 ('win_w',a.width+18),('win_h',a.height+47),('con_notifytime',0),('i_pauseinbackground',False),('vid_activeinbackground',True)])
log=Path(r['log']).read_text(encoding='utf-8')
if 'Unknown command' in log:r['ok']=False;r['errors'].append('unknown command')
(ROOT/'logs'/f'{label}-results.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
if not r['ok']:print(log[-6000:])
raise SystemExit(0 if r['ok'] else 1)
