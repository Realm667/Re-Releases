"""Class ability runtime, save/travel/respawn, weapon cadence and HUD checks."""
from pathlib import Path
import sys,json,struct,argparse,os,shutil
repo=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(repo/'tools'))
from check_engine import run_case
from build_utnt import write_wad
p=argparse.ArgumentParser();p.add_argument('--class',dest='cls',default='Marine');p.add_argument('--mode',default='logic');p.add_argument('--renderer',default='1');p.add_argument('--map',default='ABTEST');p.add_argument('--mod',default=str(repo/'tutnt'));p.add_argument('--engine',default=os.environ.get('UTNT_ENGINE'));p.add_argument('--iwad',default=os.environ.get('UTNT_IWAD'));p.add_argument('--output',type=Path,default=repo/'logs/class-abilities');args=p.parse_args()
if not args.engine or not args.iwad:p.error('Set UTNT_ENGINE and UTNT_IWAD, or pass --engine and --iwad')
w=args.output.resolve();w.mkdir(parents=True,exist_ok=True)
shutil.copytree(repo/'tools/ability-tests',w/'tests',dirs_exist_ok=True)
(w/'tests/maps').mkdir(exist_ok=True)
s='namespace="ZDoom";\n'
for x,y in [(-1024,-1024),(-1024,1024),(1024,1024),(1024,-1024)]:s+=f'vertex {{ x={x}.0; y={y}.0; }}\n'
s+='sector { heightfloor=0; heightceiling=192; texturefloor="FLAT5_4"; textureceiling="CEIL1_1"; lightlevel=176; }\n'
for i in range(4):s+=f'sidedef {{ sector=0; texturemiddle="METAL2"; }}\nlinedef {{ v1={i}; v2={(i+1)%4}; sidefront={i}; blocking=true; }}\n'
for i in range(4):s+=f'thing {{ x={-200+i*64}.0; y=-64.0; angle=0; type={i+1}; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; coop=true; }}\n'
for name in ['ABTEST','ABTEST2']:(w/'tests/maps'/f'{name}.wad').write_bytes(write_wad(b'PWAD',[(name.encode(),b''),(b'TEXTMAP',s.encode()),(b'ENDMAP',b'')]))
label=args.cls.lower()+'-'+args.mode+'-'+args.renderer+('' if args.map=='ABTEST' else '-'+args.map.lower())
commands=['wait 45']
if args.mode=='logic':
    commands+=['netevent abcheck','wait 3','netevent absave','save ability-save','wait 35','load ability-save','wait 20','netevent abloadcheck','netevent abcooldown','wait 2','netevent abtiming','wait 530']
    if args.cls=='Scout':commands+=['netevent absearch','wait 50','+attack','wait 15','-attack','netevent absearchcheck']
elif args.mode=='hud':
    for slot in [0,1,2]:commands += [f'netevent abview {slot}','wait 8',f'screenshot logs/{label}-{slot}.png']
    commands+=['netevent abview 0 1','wait 8',f'screenshot logs/{label}-cooldown.png']
    for width,height in [(640,480),(1024,768),(1920,1080),(2560,1080)]:
        commands += [f'vid_setsize {width} {height}','wait 25',f'screenshot logs/{label}-{width}.png']
    commands+=['screenblocks 12','wait 3',f'screenshot logs/{label}-hidden.png']
elif args.mode=='travel':commands+=['netevent abtravel','wait 2','changemap ABTEST2','wait 45','netevent abtravelcheck','echo UTNT_REGRESSION_COMPLETE']
elif args.mode=='cloaktravel':commands+=['netevent abcloaktravel','wait 2','changemap ABTEST2','wait 45','netevent abcloaktravelcheck','echo UTNT_REGRESSION_COMPLETE']
elif args.mode=='respawn':commands+=['netevent abrespawn','wait 45','+use','wait 4','-use','wait 45','netevent abrespawncheck','echo UTNT_REGRESSION_COMPLETE']
elif args.mode=='boss':commands+=['netevent abboss','wait 3']
elif args.mode=='rate':
    weapons=['UTNTPistol','UTNTShotgun','UTNTSuperShotgun','UTNTChaingun','UTNTMinigun','UTNTRocketLauncher','UTNTPlasmaRifle','UTNTBFG9000','UTNTPyroCannon','UTNTFlamer','UTNTFist','UTNTChainsaw']
    for weapon in weapons:
        commands += [f'give {weapon}','give ammo',f'use {weapon}','wait 55']
        for boost in [0,1]:
            commands += [f'netevent abratebegin {boost}','+attack','wait 140','-attack','wait 100',f'netevent abrateend {boost}','wait 2']
    commands+=['echo UTNT_REGRESSION_COMPLETE']
commands+=['wait 3','echo UTNT_TEST_END','quit']
r=run_case(args.engine,args.iwad,root=w,mod=args.mod,addon=w/'tests',mapname=args.map,playerclass=args.cls,renderer=args.renderer,label=label,commands='; '.join(commands).replace('ability-save',label+'-save')+'\n',regression=args.mode in ['logic','travel','respawn','rate'],timeout=250 if args.mode=='rate' else 70,settings=[('use_mouse',False),('i_pauseinbackground',False),('screenblocks',11),('language','deu'),('motionblur',False),('con_notifytime',0),('sv_singleplayerrespawn',True)])
minimum={'logic':39 if args.cls=='Scout' else 22,'rate':12,'boss':3,'travel':1,'cloaktravel':2,'respawn':1}.get(args.mode,0)
if r['assertions']<minimum:r['ok']=False
(w/'logs'/f'{label}.json').write_text(json.dumps(r,indent=2))
if not r['ok']:print(Path(r['log']).read_text()[-7000:]);sys.exit(1)
