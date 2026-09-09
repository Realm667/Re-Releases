"""Actual player/cuberoom views, animation, reduced FX, freeze and save/load."""
from pathlib import Path
import argparse,json,sys,zipfile
from check_engine import run_case
ROOT=Path(__file__).resolve().parent.parent
def run(a):
 a.work.mkdir(parents=True,exist_ok=True)
 addon=ROOT/'tools/tntle-sky-tests'
 if a.overlay:
  # Testing a pre-install overlay: combine only our resources and our fixture.
  addon=a.work/'tntle-tests.pk3'
  with zipfile.ZipFile(addon,'w',zipfile.ZIP_DEFLATED) as z:
   for p in a.overlay.rglob('*'):
    if p.is_file():
     n=p.relative_to(a.overlay).as_posix();d=p.read_bytes()
     if n=='zscript.zc':d+=b'\n#include "tntle-test.zc"\n'
     if n=='MAPINFO.txt':d+=b'\ngameinfo { AddEventHandlers = "UTNTTNTLESkyTests", "UTNTTNTLESkyLoadTest" }\n'
     z.writestr(n,d)
   test=(ROOT/'tools/tntle-sky-tests/ZSCRIPT').read_text();z.writestr('tntle-test.zc',test.replace('version "5.0.0"',''))
 label='tntle-sky-'+a.renderer
 cmd=['notarget','wait 350','netevent lecheck']
 for view in range(18):cmd += [f'netevent leview {view}','wait 35',f'screenshot logs/{label}-view{view}.png']
 cmd+=['netevent letime 1200','netevent leview 17','wait 35',f'screenshot logs/{label}-lava-a.png','wait 7',f'screenshot logs/{label}-lava-b.png','wait 7',f'screenshot logs/{label}-lava-c.png']
 cmd+=['netevent leview 14','wait 35',f'screenshot logs/{label}-cloud-a.png','wait 175',f'screenshot logs/{label}-cloud-b.png']
 cmd+=['freeze','wait 5','netevent lesnapshot',f'screenshot logs/{label}-fullfx.png','UTNT_reducedfx true','wait 6',f'screenshot logs/{label}-reduced.png','UTNT_reducedfx false','wait 35','netevent lefrozen','freeze']
 cmd+=['netevent lesnapshot',f'save {label}','wait 6','netevent letime 65000',f'load {label}','wait 175','echo UTNT_TEST_END','quit']
 r=run_case(a.engine,a.iwad,root=a.work,mod=a.mod,addon=addon,mapname='TNTLE',renderer=a.renderer,label=label,timeout=150,commands='; '.join(cmd),settings=[('win_w',1938),('win_h',1127),('vid_maxfps',120),('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_lowerinbackground',False),('screenblocks',12),('r_drawplayersprites',False),('crosshair',0),('con_notifytime',0),('UTNT_subtitles',False),('fullhud_fullstats',False),('use_mouse',False),('use_joystick',False),('gl_texture_filter',0),('motionblur',False),('UTNT_shaderoverlayswitch',False)])
 if r['assertions']!=10:r['ok']=False;r['errors'].append('expected 10 assertions')
 (a.work/'logs'/(label+'-result.json')).write_text(json.dumps(r,indent=2))
 if not r['ok']:print(Path(r['log']).read_text()[-3000:])
 return r
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['engine','iwad','mod','work']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--overlay',type=Path);p.add_argument('--renderer',choices=['0','1'],default='1');a=p.parse_args();sys.exit(0 if run(a)['ok'] else 1)
