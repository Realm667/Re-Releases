"""Regression capture for filtered TNTLE sky seams, sky AO and packaged lava."""
from pathlib import Path
import argparse,json,re,sys,zipfile
import numpy as np
from PIL import Image
from check_engine import run_case

def run(a):
 a.work.mkdir(parents=True,exist_ok=True);addon=a.work/'fixture';addon.mkdir(exist_ok=True)
 fixture=(Path(__file__).parent/'tntle-sky-tests/ZSCRIPT').read_text()
 fixture=fixture.replace('p.SetOrigin(pos,false);', 'if(View==18){pos=(100,-5300,80);angle=155;pitch=22;}\n  p.SetOrigin(pos,false);')
 (addon/'ZSCRIPT').write_text(fixture)
 (addon/'MAPINFO').write_text('gameinfo { AddEventHandlers = "UTNTTNTLESkyTests", "UTNTTNTLESkyLoadTest" }\n')
 label='tntle-materials-'+a.renderer
 cmd=['notarget','wait 175','netevent lehold 1200']
 for view in [1,3,11]:
  cmd += [f'netevent leview {view}','wait 35','freeze','wait 10','gl_ssao 0','wait 15',f'screenshot logs/{label}-view{view}-off.png','gl_ssao 3','wait 15',f'screenshot logs/{label}-view{view}-on.png','freeze']
 cmd+=['netevent leview 18','wait 35',f'screenshot logs/{label}-lava.png','wait 35',f'screenshot logs/{label}-lava-moving.png','echo UTNT_TEST_END','quit']
 r=run_case(a.engine,a.iwad,root=a.work,mod=a.mod,addon=addon,mapname='TNTLE',renderer=a.renderer,label=label,timeout=130,commands='; '.join(cmd),settings=[('win_w',1938),('win_h',1127),('motionblur',False),('UTNT_shaderoverlayswitch',False),('gl_ssao',3),('gl_ssao_portals',8),('gl_texture_filter',4),('gl_texture_filter_anisotropic',16),('screenblocks',12),('con_notifytime',0),('crosshair',0),('r_drawplayersprites',False),('use_mouse',False),('use_joystick',False),('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_lowerinbackground',False)])
 def pic(s):return np.asarray(Image.open(a.work/'logs'/(label+s+'.png')).convert('RGB'),dtype=float)
 if r['ok']:
  # Actual skybox portals in the gameplay views, away from their foreground.
  r['sky_ao_max_delta']={}
  for v in [1,3]:
   d=abs(pic(f'-view{v}-on')-pic(f'-view{v}-off'))[170:500,500:1400]
   r['sky_ao_max_delta'][v]=float(d.max())
  r['lava_motion_mean_delta']=float(abs(pic('-lava')[520:800,400:1400]-pic('-lava-moving')[520:800,400:1400]).mean())
  r['ok']=max(r['sky_ao_max_delta'].values())<=2 and r['lava_motion_mean_delta']>.1
  if a.mod.suffix.lower()=='.pk3':
   with zipfile.ZipFile(a.mod) as z:
    required=['GLDEFS.lava','shaders/lava-surface.fp','shaders/lava-fall.fp','materials/lava/crust-height.png']
    r['packaged_lava_assets']=all(n in z.namelist() for n in required) and b'#include "GLDEFS.lava"' in z.read('GLDEFS.txt')
    r['ok'] &= r['packaged_lava_assets']
 (a.work/'logs'/(label+'-result.json')).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2));return r['ok']

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['engine','iwad','mod','work']:p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--renderer',choices=['0','1'],default='1');a=p.parse_args();sys.exit(0 if run(a) else 1)
