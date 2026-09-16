"""Runtime regression for UTNT secondary fire; all generated files stay in .codex."""
from pathlib import Path
import argparse, json, os, sys, zipfile
from build_utnt import write_wad
from check_engine import run_case
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--engine',default=os.environ.get('UTNT_ENGINE',str(ROOT/'engine/uzdoom.exe')))
p.add_argument('--iwad',default=os.environ.get('UTNT_IWAD','F:/DoomDev/DOOM2.WAD'))
p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
p.add_argument('--overlay',action='store_true',help='Test local weapon sources over the previous integration PK3')
p.add_argument('--compile-only',action='store_true')
p.add_argument('--class',dest='playerclass',default='Marine')
p.add_argument('--mode',default='logic',choices=['logic','rate','chain','visual','grenade'])
a=p.parse_args()
local=ROOT/'tutnt/.codex'
logs=local/'logs/secondary-fire';logs.mkdir(parents=True,exist_ok=True)
reports=local/'validation/secondary-fire';reports.mkdir(parents=True,exist_ok=True)
addon=local/('builds/utnt-secondary-tests-'+a.playerclass.lower()+'-'+a.mode+'.pk3')
text='namespace="ZDoom";\n'
for x,y in [(-1536,-1536),(-1536,1536),(1536,1536),(1536,-1536)]:text+=f'vertex {{ x={x}.0; y={y}.0; }}\n'
text+='sector { heightfloor=0; heightceiling=256; texturefloor="FLAT5_4"; textureceiling="CEIL1_1"; lightlevel=192; }\n'
for i in range(4):text+=f'sidedef {{ sector=0; texturemiddle="METAL2"; }}\nlinedef {{ v1={i}; v2={(i+1)%4}; sidefront={i}; blocking=true; }}\n'
# Solid central pillar for line-of-sight and collision tests (counterclockwise hole).
for x,y in [(400,600),(600,600),(600,1000),(400,1000)]:text+=f'vertex {{ x={x}.0; y={y}.0; }}\n'
for i in range(4):text+=f'sidedef {{ sector=0; texturemiddle="METAL2"; }}\nlinedef {{ v1={i+4}; v2={(i+1)%4+4}; sidefront={i+4}; blocking=true; }}\n'
for i in range(4):text+=f'thing {{ x=0.0; y={-i*64}.0; angle=0; type={i+1}; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; coop=true; }}\n'
with zipfile.ZipFile(addon,'w',zipfile.ZIP_DEFLATED) as z:
 entry='version "5.0.0"\n'
 if a.overlay:
  with zipfile.ZipFile(a.mod) as base:
   if "zscript/utnt_secondaryfire.zc" not in {n.lower() for n in base.namelist()}:
    entry+='#include "zscript/UTNT_SecondaryFire.zc"\n'
  for f in ['zscript/UTNT_SecondaryFire.zc','actors/weapons.txt','VOXELDEF.txt','voxels/UVUGRNA.kvx','sprites/UGRNA0.lmp']:z.write(ROOT/'tutnt'/f,f)
 entry+='#include "secondary-tests.zc"\n'
 z.writestr('ZSCRIPT',entry)
 z.write(ROOT/'tools/fixtures/secondary-fire/tests.zc','secondary-tests.zc')
 z.writestr('MAPINFO','gameinfo { AddEventHandlers = "SecondaryTestHandler" }\nmap SECTEST "Secondary fire proving ground" { next="SECTEST2" NoIntermission }\nmap SECTEST2 "Secondary travel" { next="SECTEST" NoIntermission }\n')
 for name in ['SECTEST','SECTEST2']:z.writestr('maps/'+name+'.wad',write_wad(b'PWAD',[(name.encode(),b''),(b'TEXTMAP',text.encode()),(b'ENDMAP',b'')]))
commands=['wait 45','netevent secdefaults','give UTNTSuperShotgun','give UTNTPistol','give UTNTRocketLauncher','give UTNTPlasmaRifle','give UTNTBFG9000','give ammo','wait 10','use UTNTSuperShotgun','wait 60']
if a.mode=='logic':
 commands+=['netevent secsetup 0','+altattack','wait 1','-altattack','wait 20','netevent secverify 1','save secondary-barrel','wait 4','load secondary-barrel','wait 20','netevent secverify 1','use UTNTPistol','wait 50','use UTNTSuperShotgun','wait 50','netevent secverify 1','+attack','wait 1','-attack','wait 100','netevent secverify 2','netevent secone','+altattack','wait 1','-altattack','wait 100','netevent secverify 3','use UTNTRocketLauncher','give ammo','wait 60','netevent secsetup 1','+altattack','wait 1','-altattack','wait 100','netevent secverify 4','netevent secsetup 4','+altattack','wait 1','-altattack','wait 50','netevent secverify 5','netevent secdirect','wait 3','netevent secdirectcheck']
elif a.mode=='rate':
 for weapon,mode in [('UTNTPlasmaRifle',2),('UTNTSuperShotgun',0),('UTNTRocketLauncher',1),('UTNTBFG9000',3)]:
  commands += ['netevent secclear','give ammo','use '+weapon,'wait 60']
  for boost in [0,1] if a.playerclass=='Commando' else [0]:
   commands += [f'netevent secratebegin {mode} {boost}','+altattack','wait 210','-altattack','wait 100',f'netevent secrateend {mode} {boost}']
 commands+=['netevent secclear','give ammo','use UTNTPlasmaRifle','wait 60','netevent secprimary','+attack','wait 210','-attack','wait 50','netevent secprimaryend']
elif a.mode=='chain':
 commands+=['use UTNTBFG9000','wait 60','netevent secsetup 3','+altattack','wait 1','-altattack','wait 48','save secondary-chain','wait 4','load secondary-chain','wait 270','netevent secverify 6','netevent secsetup 5','+altattack','wait 1','-altattack','wait 160','netevent secverify 7','netevent secsetup 6','+altattack','wait 1','-altattack','wait 160','netevent secverify 8']
elif a.mode=='grenade':
 commands+=['UTNT_fxquality 3','wait 100','netevent secgrenade 0','wait 8','netevent secgrenade 1','screenshot logs/grenade-flight.png','save grenade-tumble','wait 4','load grenade-tumble','wait 6','netevent secgrenade 1','netevent secgrenade 2','wait 8','screenshot logs/grenade-voxel-detail.png']
elif a.mode=='visual':
 for weapon,mode in [('UTNTSuperShotgun',0),('UTNTRocketLauncher',1),('UTNTPlasmaRifle',2),('UTNTBFG9000',3)]:
  commands+=['give ammo','use '+weapon,'wait 60',f'netevent secsetup {mode}','+altattack','wait 1','-altattack','wait 42' if weapon=='UTNTBFG9000' else 'wait 12',f'screenshot logs/{weapon}-secondary.png','wait 120']
commands+=['wait 3','echo UTNT_REGRESSION_COMPLETE','echo UTNT_TEST_END','quit']
label=a.playerclass.lower()+'-'+a.mode+('-compile' if a.compile_only else '')
result=run_case(a.engine,a.iwad,root=logs,mod=a.mod,addon=addon,mapname=None if a.compile_only else 'SECTEST',playerclass=a.playerclass,label=label,commands='; '.join(commands)+'\n',timeout=170,regression=not a.compile_only,settings=[('use_mouse',False),('i_pauseinbackground',False),('vid_maxfps',200),('screenblocks',11),('motionblur',False),('con_notifytime',0)])
if not a.compile_only and result['assertions']<{'logic':24,'rate':13,'chain':11,'visual':6,'grenade':15}[a.mode]:result['ok']=False
(reports/(label+'.json')).write_text(json.dumps(result,indent=2))
if not result['ok']:print(Path(result['log']).read_text()[-9000:])
sys.exit(0 if result['ok'] else 1)
