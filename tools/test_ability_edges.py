"""Render all class ability edges, pulse phases and view/lifecycle transitions."""
from pathlib import Path
import argparse,json,os,shutil,sys
repo=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(repo/'tools'))
from check_engine import run_case
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--engine',default=os.environ.get('UTNT_ENGINE'))
p.add_argument('--iwad',default=os.environ.get('UTNT_IWAD'))
p.add_argument('--mod',default=str(repo/'tutnt'))
p.add_argument('--output',type=Path,default=repo/'logs/ability-edges')
p.add_argument('--class',dest='cls',choices=['Marine','Scout','Commando'],default='Marine')
p.add_argument('--renderer',choices=['0','1'],default='1')
p.add_argument('--sizes',action='store_true')
p.add_argument('--cards',action='store_true')
a=p.parse_args()
if not a.engine or not a.iwad:p.error('Pass --engine/--iwad or set UTNT_ENGINE/UTNT_IWAD')
w=a.output.resolve();w.mkdir(parents=True,exist_ok=True)
fixture=w/(a.cls.lower()+'-'+a.renderer+'-fixture')
shutil.copytree(repo/'tools/ability-tests',fixture,dirs_exist_ok=True)
shutil.copyfile(repo/'tools/ability-edge-tests/edge-tests.zc',fixture/'edge-tests.zc')
with (fixture/'ZSCRIPT').open('a') as f:f.write('\n#include "edge-tests.zc"\n')
with (fixture/'MAPINFO').open('a') as f:f.write('\ngameinfo { AddEventHandlers="AbilityEdgeTest" }\n')
label=a.cls.lower()+'-edges-'+a.renderer
commands=['wait 220','r_drawplayersprites false','crosshair 0']
def shot(name,slot,phase=52,method=0):
    commands.extend([f'netevent edge {slot} {phase} {method}','wait 8',f'screenshot logs/{label}-{name}.png'])
shot('off',0)
for slot in [1,2]:
    shot(str(slot)+'-low',slot,35)
    shot(str(slot)+'-high',slot,52)
    shot(str(slot)+'-low-repeat',slot,70)
    commands+=['UTNT_reducedfx true']
    shot(str(slot)+'-reduced',slot)
    commands+=['UTNT_reducedfx false']
for name,method in [('cutscene',1),('camera',2),('frozen',4),('expired',5)]:shot(name,1,52,method)
shot('restored',2)
commands+=['save edge-save','wait 5','netevent edge 0','wait 5','load edge-save','wait 8',f'screenshot logs/{label}-loaded.png','netevent edgeexpect '+str({'Marine':2,'Scout':4,'Commando':6}[a.cls]),'wait 8']
commands+=['togglemap','wait 5','netevent edgeexpect 0','wait 8',f'screenshot logs/{label}-map.png','togglemap','wait 8']
commands+=['changemap ABTEST2','wait 30','netevent edgeexpect '+str({'Marine':2,'Scout':4,'Commando':6}[a.cls]),'wait 8',f'screenshot logs/{label}-travel.png']
if a.sizes:
    for width,height in [(640,480),(1920,1080),(2560,1080)]:
        commands += [f'vid_setsize {width} {height}','wait 25']
        shot(str(width),2)
commands+=['netevent edge 1 52 5','wait 8','netevent abrespawn','wait 45','+use','wait 4','-use','wait 45','netevent edgeexpect 0','wait 8',f'screenshot logs/{label}-respawn.png']
if a.cards:
    commands+=['vid_setsize 960 540','wait 25']
    for language in ['deu','enu']:
        commands += [f'language {language}','event edgecards','wait 8','event edgecardcheck',f'screenshot logs/{label}-cards-{language}.png','event edgecardkey','wait 4','event edgeclose']
    commands += ['language deu']
    for width,height in [(640,480),(1920,1080),(2560,1080)]:
        commands += [f'vid_setsize {width} {height}','wait 25','event edgecards','wait 8','event edgecardcheck',f'screenshot logs/{label}-cards-{width}.png','event edgecardmouse 1','wait 4','event edgeclose']
commands+=['echo UTNT_TEST_END','quit']
r=run_case(a.engine,a.iwad,root=w,mod=a.mod,addon=fixture,mapname='ABTEST',playerclass=a.cls,renderer=a.renderer,label=label,commands='; '.join(commands)+'\n',timeout=90,settings=[('use_mouse',False),('i_pauseinbackground',False),('screenblocks',11),('language','deu'),('motionblur',False),('con_notifytime',0),('sv_singleplayerrespawn',True),('gl_bloom',False),('UTNT_reducedfx',False)])
if r['assertions']<40+(6 if a.sizes else 0)+(45 if a.cards else 0):r['ok']=False
(w/'logs'/f'{label}.json').write_text(json.dumps(r,indent=2))
if not r['ok']:print(Path(r['log']).read_text()[-7000:])
sys.exit(0 if r['ok'] else 1)
