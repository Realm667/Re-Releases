"""Check real key pickups above SBAR ability cards at varied HUD/UI scales."""
from pathlib import Path
import argparse,json,shutil,sys,zipfile

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parent.parent)
p.add_argument('--engine',required=True)
p.add_argument('--iwad',required=True)
p.add_argument('--mod',type=Path)
p.add_argument('--output',type=Path)
p.add_argument('--fixture',type=Path)
p.add_argument('--quick',action='store_true')
p.add_argument('--renderer',choices=['0','1'],default='1')
p.add_argument('--palette-probe',action='store_true',help='Rotate RGB in an isolated PLAYPAL add-on; never changes the mod palette.')
a=p.parse_args()
sys.path.insert(0,str(a.repo/'tools'))
from check_engine import run_case
output=(a.output or a.repo/'logs/hud-stacking').resolve();output.mkdir(parents=True,exist_ok=True)
fixture=a.fixture or a.repo/'tools/hud-stacking-tests'
mod=a.mod or a.repo/'tutnt'
if a.palette_probe:
    target=output/'palette-fixture';shutil.copytree(fixture,target,dirs_exist_ok=True);fixture=target
    if mod.is_dir(): data=(mod/'PLAYPAL.pal').read_bytes()
    else:
        with zipfile.ZipFile(mod) as archive: data=archive.read('PLAYPAL.pal')
    palette=bytearray(data)
    for i in range(0,len(palette),3):
        red,green,blue=palette[i:i+3];palette[i:i+3]=bytes((green,blue,red))
    (fixture/'PLAYPAL.lmp').write_bytes(palette)
cases=[(1920,1080,1,2,10,'enu','Marine'),
       (640,480,1.5,1,11,'deu','Scout'),
       (1024,768,1.5,2,10,'deu','Commando'),
       (2560,1080,1.5,3,11,'enu','Marine'),
       (960,540,.75,1,9,'deu','Marine')]
results=[]
for width,height,scale,hud,blocks,language,cls in cases[:1] if a.quick else cases:
    label=f'stack-{width}-{height}-{blocks}-{cls}'
    commands=[f'vid_setsize {width} {height}','wait 200','r_drawplayersprites false','crosshair 0']
    for kind in [0,1,2]:
        commands += ['event stackclear',f'netevent stackpick {kind}','wait 12',f'event stackcheck {kind}',
                     f'screenshot logs/{label}-{kind}.png','wait 3']
    commands += ['echo UTNT_TEST_END','quit']
    result=run_case(a.engine,a.iwad,root=output,mod=mod,
        addon=fixture,mapname='TNT02',
        renderer=a.renderer,playerclass=cls,label=label,commands='; '.join(commands)+'\n',timeout=45,
        settings=[('screenblocks',blocks),('UTNT_uiscale',scale),('hud_scale',hud),('language',language),
                  ('vid_activeinbackground',True),('i_pauseinbackground',False),('use_mouse',False),
                  ('con_notifytime',0),('motionblur',False)])
    result['ok'] &= result['assertions']==21
    result['case']=[width,height,scale,hud,blocks,language,cls,a.renderer]
    results.append(result)
    if not result['ok']: print(Path(result['log']).read_text()[-5000:])
(output/'results.json').write_text(json.dumps(results,indent=2)+'\n')
raise SystemExit(0 if all(r['ok'] for r in results) else 1)
