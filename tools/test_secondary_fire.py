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
p.add_argument('--renderer',choices=('0','1'),default='1',help='0: OpenGL, 1: Vulkan')
p.add_argument('--language',choices=('en','de','es','fr'),default='de')
p.add_argument('--class',dest='playerclass',default='Marine')
p.add_argument('--mode',default='logic',choices=['logic','rate','chain','visual','grenade','extended','pressure','burst','refined','hud','flashes','followup'])
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
  for f in ['zscript/UTNT_SecondaryFire.zc','actors/weapons.txt','actors/SFX.txt','graphics/weapons/grenade-muzzle-smoke.png','VOXELDEF.txt','voxels/UVUGRNA.kvx','sprites/UGRNA0.lmp','zscript/UTNT_Presentation.zc','zscript/UTNT_BurnDeath.zc','shaders/pressure-wave.fp','zscript/UTNT_PickupFeedback.zc','zscript/UTNT_EffectGlow.zc','LANGUAGE.txt','TEXTURES.txt','sounds/UGRBOUNC.ogg']:z.write(ROOT/'tutnt'/f,f)
  z.writestr('GLDEFS',(ROOT/'tutnt/gldefs/GLDEFS.secondary-fire').read_bytes())
  z.writestr('SNDINFO','weapons/grenadebounce UGRBOUNC\n')
 entry+='#include "secondary-tests.zc"\n'
 if a.mode in ('refined','hud','flashes','followup'):entry+='#include "refinements.zc"\n';z.write(ROOT/'tools/fixtures/secondary-fire/refinements.zc','refinements.zc')
 if a.mode in ('extended','pressure','burst'):entry+='#include "extended-tests.zc"\n';z.write(ROOT/'tools/fixtures/secondary-fire/extended.zc','extended-tests.zc')
 z.writestr('ZSCRIPT',entry)
 z.write(ROOT/'tools/fixtures/secondary-fire/tests.zc','secondary-tests.zc')
 z.writestr('MAPINFO','gameinfo { AddEventHandlers = "'+('SecondaryRefinementTest' if a.mode in ('refined','hud','flashes','followup') else 'ExtendedSecondaryTest' if a.mode in ('extended','pressure','burst') else 'SecondaryTestHandler')+'" }\nmap SECTEST "Secondary fire proving ground" { next="SECTEST2" NoIntermission }\nmap SECTEST2 "Secondary travel" { next="SECTEST" NoIntermission }\n')
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
elif a.mode=='refined':
 commands+=['netevent refshot 0','+altattack','wait 1','-altattack','wait 5','screenshot logs/ssg-left.png','wait 20','netevent refshotcheck 1','netevent refshot 1','+altattack','wait 1','-altattack','wait 5','screenshot logs/ssg-right.png','wait 100','netevent refshotcheck 2','netevent refshot 0','+attack','wait 1','-attack','wait 100','netevent refshotcheck 3','netevent refgrenade','wait 12','netevent refbounce','netevent refpyro','wait 7','netevent refpyrocheck','give UTNTFlamer','use UTNTFlamer','wait 90','netevent refpressure','+altattack','wait 1','-altattack','wait 1','netevent refpressurecheck','wait 45','netevent refprofiles','use UTNTPlasmaRifle','give ammo','wait 60','netevent secprimary','+attack','wait 420','-attack','wait 45','netevent refdps 0','netevent secratebegin 2 0','+altattack','wait 420','-altattack','wait 45','netevent secrateend 2 0','netevent refdps 1','netevent refpickup','wait 50','save secondary-hints','wait 3','load secondary-hints','wait 20','netevent refpickupagain','changelevel SECTEST2','wait 60','netevent refpickupagain']
elif a.mode=='followup':
 commands+=['UTNT_fxquality 3','use UTNTRocketLauncher','wait 60','netevent followflash','+altattack','wait 1','-altattack','wait 7','netevent followflashcheck','wait 4','screenshot logs/grenade-muzzle-smoke.png','wait 50','netevent followbounce 0','wait 12','netevent followbouncecheck','netevent followbounce 1','wait 8','netevent followbouncecheck','netevent followsmoke 0','wait 10','netevent followsmokecheck','screenshot logs/pyro-impact-smoke.png','wait 100','netevent followsmoke 1','wait 10','netevent followsmokecheck','wait 100']
 for scenario in range(6):
  commands += [f'netevent followroute {scenario}','wait 10']
  if scenario==0:commands+=['save secondary-route','wait 2','load secondary-route','wait 3']
  commands+=['wait 65',f'netevent followroutecheck {scenario}']
elif a.mode=='flashes':
 commands+=['wait 90','netevent refflashgallery 1','wait 10','screenshot logs/ssg-left-gallery.png','wait 35','netevent refflashgallery 2','wait 10','screenshot logs/ssg-right-gallery.png']
elif a.mode=='hud':
 commands+=['bind mouse2 +altattack','netevent refpickup','wait 60','screenshot logs/secondary-hud-'+a.language+'.png','wait 130','netevent refpickupagain','netevent refhintlong','wait 45','screenshot logs/secondary-hud-long-'+a.language+'.png','wait 150','use UTNTFist','wait 60','screenshot logs/secondary-hud-single.png']
elif a.mode=='pressure':
 commands+=['give UTNTFlamer','use UTNTFlamer','wait 120','UTNT_fxquality 3','netevent xsetup 3','+altattack','wait 1','-altattack','wait 5','screenshot logs/pressure-shader.png','netevent xair','wait 45','netevent xairblocked','+altattack','wait 1','-altattack','wait 10','netevent xairblockedcheck']
elif a.mode=='burst':
 commands+=['use UTNTPistol','wait 60','netevent xsetup 1','+altattack','wait 1','-altattack','wait 5','save pistol-burst','wait 2','load pistol-burst','wait 60','netevent xburstcheck 3']
elif a.mode=='extended':
 commands+=['give UTNTFlamer','give UTNTPyroCannon','give UTNTShotgun','wait 100','use UTNTPistol','wait 60']
 for boost in ([0,1] if a.playerclass=='Commando' else [0]):
  for button,mode in [('attack',0),('altattack',1)]:
   commands+=['netevent xsetup 1',f'netevent xboost {boost}',f'+{button}','wait 390',f'-{button}','wait 60',f'netevent xrate {mode}']
 commands+=['netevent xsetup 1','+altattack','wait 1','-altattack','wait 60','netevent xburstcheck 3','netevent xsetup 1','netevent xammo 2','+altattack','wait 1','-altattack','wait 60','netevent xburstcheck 2','give Clip 200','use UTNTPistol','wait 60','netevent xsetup 1','+altattack','wait 1','-altattack','wait 5','save pistol-burst','wait 2','load pistol-burst','wait 60','netevent xburstcheck 3','use UTNTShotgun','wait 60']
 for button,mode in [('attack',0),('altattack',1)]:
  commands+=['netevent xsetup 2',f'+{button}','wait 1',f'-{button}','wait 60',f'netevent xspread {mode}']
 commands+=['use UTNTFlamer','wait 60','UTNT_fxquality 3','netevent xsetup 3','+altattack','wait 1','-altattack','wait 5','screenshot logs/pressure-shader.png','netevent xair','wait 45','netevent xairblocked','+altattack','wait 1','-altattack','wait 10','netevent xairblockedcheck','wait 45','use UTNTPyroCannon','wait 60','netevent xsetup 4','+altattack','wait 1','-altattack','wait 62','netevent xpyro','screenshot logs/pyro-orb.png','save pyro-burn','wait 2','load pyro-burn','wait 200','netevent xpyrowall','netevent xburnend','wait 10','netevent xchar','netevent xpyroblocked','wait 20','netevent xblockedcheck']
elif a.mode=='grenade':
 commands+=['UTNT_fxquality 3','wait 100','netevent secgrenade 0','wait 8','netevent secgrenade 1','screenshot logs/grenade-flight.png','save grenade-tumble','wait 4','load grenade-tumble','wait 6','netevent secgrenade 1','netevent secgrenade 2','wait 8','screenshot logs/grenade-voxel-detail.png']
elif a.mode=='visual':
 for weapon,mode in [('UTNTSuperShotgun',0),('UTNTRocketLauncher',1),('UTNTPlasmaRifle',2),('UTNTBFG9000',3)]:
  commands+=['give ammo','use '+weapon,'wait 60',f'netevent secsetup {mode}','+altattack','wait 1','-altattack','wait 42' if weapon=='UTNTBFG9000' else 'wait 12',f'screenshot logs/{weapon}-secondary.png','wait 120']
commands+=['wait 3','echo UTNT_REGRESSION_COMPLETE','echo UTNT_TEST_END','quit']
label=a.playerclass.lower()+'-'+a.mode+('-compile' if a.compile_only else '')
result=run_case(a.engine,a.iwad,renderer=a.renderer,root=logs,mod=a.mod,addon=addon,mapname=None if a.compile_only else 'SECTEST',playerclass=a.playerclass,label=label,commands='; '.join(commands)+'\n',timeout=170,regression=not a.compile_only,settings=[('use_mouse',False),('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_maxfps',200),('screenblocks',11),('motionblur',False),('con_notifytime',0),('language',a.language)])
if not a.compile_only and result['assertions']<{'logic':24,'rate':13,'chain':11,'visual':6,'grenade':15,'extended':32,'pressure':13,'burst':7,'refined':34,'hud':10,'flashes':6,'followup':34}[a.mode]:result['ok']=False
(reports/(label+'.json')).write_text(json.dumps(result,indent=2))
if not result['ok']:print(Path(result['log']).read_text()[-9000:])
sys.exit(0 if result['ok'] else 1)
