"""Render and verify plasma tint, unchanged other-blue halos, impact and live firing.
All generated addons, captures and logs are kept in tutnt/.codex.
"""
from pathlib import Path
import argparse,os,sys,shutil,json
root=Path(__file__).resolve().parent.parent
from check_engine import run_case
work=root/'tutnt/.codex/work/plasma-blue';addon=work/'addon';(addon/'maps').mkdir(parents=True,exist_ok=True)
shutil.copyfile(root/'tools/industrial-revision-tests/maps/utntifx.wad',addon/'maps/utntifx.wad')
shutil.copyfile(root/'tools/fixtures/plasma-color/ZSCRIPT',addon/'ZSCRIPT')
(addon/'MAPINFO').write_text('gameinfo { AddEventHandlers="UTNTPlasmaColorTest" }\nmap UTNTIFX "Plasma color validation" { levelnum=98 }\n')
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--label',default='after')
parser.add_argument('--renderer',choices=['0','1'],default='1')
parser.add_argument('--mod',type=Path,default=root/'tutnt.pk3')
parser.add_argument('--engine',default=os.environ.get('UTNT_ENGINE','F:/DoomDev/uzdoom.exe'))
parser.add_argument('--iwad',default=os.environ.get('UTNT_IWAD','F:/DoomDev/DOOM2.WAD'))
parser.add_argument('--baseline',action='store_true',help='Capture the previous package without expecting the new tint.')
a=parser.parse_args();label=a.label;backend=a.renderer;check=not a.baseline
(root/'tutnt/.codex/validation/plasma-blue').mkdir(parents=True,exist_ok=True)
cmd=['vid_setsize 1600 900','wait 160','netevent plasmastage 0','wait 12']
if check:cmd+=['netevent plasmacheck']
cmd+=['netevent plasmastage 1','wait 12',f'screenshot tutnt/.codex/validation/plasma-blue/{label}-flight-{backend}.png','netevent plasmaimpact','wait 3',f'screenshot tutnt/.codex/validation/plasma-blue/{label}-impact-{backend}.png','wait 70','netevent plasmastage 2','give plasmarifle','give cell 300','use UTNTPlasmaRifle','r_drawplayersprites true','wait 35','+attack','wait 18',f'screenshot tutnt/.codex/validation/plasma-blue/{label}-firing-{backend}.png','-attack','wait 40','echo UTNT_TEST_END','quit']
r=run_case(a.engine,a.iwad,mod=a.mod,mapname='UTNTIFX',addon=addon,renderer=backend,label='plasma-blue-'+label+'-'+backend,timeout=55,regression=check,commands='; '.join(cmd)+'\n',settings=[('use_mouse',False),('use_joystick',False),('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_maxfps',60),('con_notifytime',0),('motionblur',False),('UTNT_shaderoverlayswitch',False),('UTNT_visoreffects',False),('UTNT_subtitles',False),('UTNT_effectglow',True),('UTNT_glowstrength',0.65),('UTNT_fxquality',3),('UTNT_lod',2400),('r_drawplayersprites',False),('screenblocks',12),('gl_bloom',False),('crosshair',0)])
(root/f'tutnt/.codex/validation/plasma-blue/{label}-{backend}.json').write_text(json.dumps(r,indent=2)+'\n')
if not r['ok']:print(Path(r['log']).read_text()[-5000:]);sys.exit(1)
