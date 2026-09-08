from pathlib import Path
import json
import os
R=Path(__file__).resolve().parent.parent
addon=R/'tools/usability-tests'
from check_engine import run_case
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--engine',default=os.environ.get('UTNT_ENGINE',str(R/'engine/uzdoom.exe')))
parser.add_argument('--iwad',default=os.environ.get('UTNT_IWAD',r'F:\DoomDev\DOOM2.WAD'))
parser.add_argument('--mod',type=Path,default=R/'tutnt')
parser.add_argument('--label',default='usability-first')
parser.add_argument('--language',default='enu')
parser.add_argument('--class',dest='playerclass',default='Marine')
parser.add_argument('--dungeon',action='store_true')
parser.add_argument('--width',type=int,default=1920)
parser.add_argument('--height',type=int,default=1080)
a=parser.parse_args()
label=a.label
compiled=run_case(a.engine,a.iwad,root=R,mod=a.mod,addon=addon,label=label+'-compile')
if not compiled['ok']:
 print(Path(compiled['log']).read_text()[-3000:]);raise SystemExit(1)
cmd=['wait 180','netevent usreset','wait 5','event usclear',
 'netevent uspick 0','netevent uspick 0','wait 9','event usgain 0 20',
 'netevent uspick 1','netevent uspick 1','wait 9','event usgain 2 20',
 'netevent uspick 2','wait 10','event usitem 1',f'screenshot logs/{label}-pickups.png','wait 3',
 'event usclear','netevent uscap','netevent uspick 0','wait 3','event usgain 0 1',
 'event usclear','netevent usfull','netevent uspick 0','wait 3','event usgain 0 0','netevent usasserthealth',
 'netevent usarmor','netevent uspick 4','wait 3','event usgain 1 1',
 'event usclear','netevent usammocap','netevent uspick 1','wait 3','event usgain 2 1',
 'event usclear','netevent uslock 2','wait 10','event usmarkers 1','netevent uslock 2','wait 3','event usmarkers 1',
 'togglemap','wait 5',f'screenshot logs/{label}-lock.png','wait 3','togglemap',
 f'save {label}','wait 3',f'load {label}','wait 15','event usmarkers 1','netevent ususe','wait 20','event usmarkers 0',
 'netevent uslock 130','wait 5','event usmarkers 1','event uscombined','netevent ususe','wait 5','event usmarkers 0',
 'netevent usshowgate','netevent ussignal 211','wait 10','event uspulses 1',f'screenshot logs/{label}-pulse.png','wait 110','event uspulses 0',
 'event usclass','wait 10','event usclasscheck',f'screenshot logs/{label}-classes.png','wait 3','event usclassnext','event usclasschoose','wait 5',f'screenshot logs/{label}-episode.png','wait 3','event usmenuclose','event usmenuclose',
 'event usclass','event usclassmouse','wait 3','event usmenuclose','event usmenuclose',
 'event usoptions','wait 5',f'screenshot logs/{label}-options.png','wait 3','event uspreset 0','event uspreset 1','event uspreset 2','event usmenuclose',
 'event usdone','echo UTNT_TEST_END','wait 3','quit']
if a.dungeon:
 cmd=['wait 180','netevent usdungeon','wait 350','event uspulses 1','wait 110','event uspulses 0','event usdone','echo UTNT_TEST_END','wait 3','quit']
r=run_case(a.engine,a.iwad,root=R,mod=a.mod,addon=addon,mapname='TNT01' if a.dungeon else 'TNT02',playerclass=a.playerclass,label=label,commands='; '.join(cmd),timeout=65,regression=True,settings=[('language',a.language),('win_w',a.width+18),('win_h',a.height+47),('vid_activeinbackground',True),('i_pauseinbackground',False),('con_notifytime',0)])
(R/'logs'/(label+'-results.json')).write_text(json.dumps(r,indent=2))
if not r['ok']:print(Path(r['log']).read_text()[-5000:])
raise SystemExit(0 if r['ok'] else 1)
