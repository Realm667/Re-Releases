"""Native secret discovery and full-screen/overlay automap acceptance."""
from pathlib import Path
import argparse, os, json
from check_engine import run_case
R=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--lang',default='enu');p.add_argument('--renderer',default='1')
p.add_argument('--class',dest='playerclass',default='Marine')
p.add_argument('--width',type=int,default=1920);p.add_argument('--height',type=int,default=1080)
p.add_argument('--map',default='TNT01');p.add_argument('--tag',default='')
p.add_argument('--mod',type=Path,default=R/'tutnt');a=p.parse_args()
label=f'exploration-{a.lang}-{a.playerclass}-{a.width}-{a.renderer}'+('-'+a.tag if a.tag else '')
cmd=['wait 180','event exresources','event exclear','netevent exreset','wait 3',
     'netevent exgive 3','wait 10','event excount 1 9001',f'screenshot logs/{label}-secret.png',
     'netevent exgive 3','netevent exgive 3','wait 10','event excount 3 9001',
     'netevent exsector','wait 10','event excount 4 9001','event exsectorcheck','wait 10','event excount 4 9001',
     'event exclear','netevent exgive 0','wait 3','event excount 5 0',
     'cl_showsecretmessage false','netevent exgive 3','wait 3','event excount 6 0','cl_showsecretmessage true',
     'netevent exgive 1','wait 10','event excount 7 9001',
     f'save {label}','wait 3',f'load {label}','wait 35','event excount 7 0',
     'event exremember','netevent exreveal','wait 3','togglemap','am_gobig','wait 10','event exmap 0','event exprefs',
     f'screenshot logs/{label}-map.png','togglemap','wait 3','event exprefs',
     'am_overlay 1','togglemap','wait 10','event exmap 1','event exprefs',f'screenshot logs/{label}-overlay.png',
     'togglemap','wait 3','am_overlay 0','event exprefs','echo UTNT_TEST_END','wait 2','quit']
cmd=[step for c in cmd for step in ([c,'wait 4'] if c.startswith('screenshot ') else [c])]
r=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],root=R,mod=a.mod,mapname=a.map,
    addon=R/'tools/exploration-tests',label=label,renderer=a.renderer,playerclass=a.playerclass,
    commands='; '.join(cmd)+'\n',timeout=70,regression=True,settings=[('language',a.lang),
    ('win_w',a.width+18),('win_h',a.height+47),('con_notifytime',0),('am_overlay',0),
    ('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_lowerinbackground',False)])
log=Path(r['log']).read_text(encoding='utf-8')
if 'Unknown command' in log:r['ok']=False;r['errors'].append('unknown console command')
(R/'logs'/f'{label}-results.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
if not r['ok']:print(log[-5500:])
raise SystemExit(0 if r['ok'] else 1)
