"""TNT01 storm tour, save/load and cloud-motion checks in both renderers.
Requires Pillow and NumPy for pixel checks. Test fixtures are never packaged.
"""
import argparse,json,os
from pathlib import Path
import numpy as np
from PIL import Image
from check_engine import run_case,ROOT

def motion(logs,label):
 a=np.asarray(Image.open(logs/(label+'-motion-a.png')).convert('RGB'),dtype=float)
 b=np.asarray(Image.open(logs/(label+'-motion-b.png')).convert('RGB'),dtype=float)
 assert a.shape==b.shape==(1080,1920,3)
 # View 8 has an unobstructed cloud patch above, solid mountains at left.
 # Intro has fully faded, camera is held fixed, HUD/weapon are excluded.
 cloud=float(np.abs(a[30:150,700:1200]-b[30:150,700:1200]).mean())
 mountain=float(np.abs(a[400:520,40:300]-b[400:520,40:300]).mean())
 architecture=float(np.abs(a[750:850,1200:1500]-b[750:850,1200:1500]).mean())
 return {'cloud_mean_abs_rgb_change':cloud,'mountain_mean_abs_rgb_change':mountain,
         'architecture_mean_abs_rgb_change':architecture,'seconds_between_frames':5,
         # Existing map lights animate on masonry; this is informational.
         # The opaque mountain patch is the unlit stationary control.
         'ok':cloud>.15 and mountain<.05}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--engine',type=Path,default=os.environ.get('UTNT_ENGINE'))
 p.add_argument('--iwad',type=Path,default=os.environ.get('UTNT_IWAD'))
 p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
 p.add_argument('--work',type=Path,default=ROOT)
 p.add_argument('--renderer',choices=['0','1','both'],default='both')
 a=p.parse_args()
 if not a.engine or not a.iwad:p.error('Configure engine and IWAD')
 results=[]
 for backend in ['0','1'] if a.renderer=='both' else [a.renderer]:
  label='sky-storm-'+backend;commands=['notarget','wait 350']
  for view in range(9):
   commands += [f'netevent stormview {view}','wait 8',f'screenshot logs/{label}-view{view}.png']
  commands += ['netevent stormview 8','wait 8',f'screenshot logs/{label}-motion-a.png',
   'wait 175',f'screenshot logs/{label}-motion-b.png','netevent stormview 0','wait 8',
   f'save {label}','wait 8',f'load {label}','wait 15','netevent stormcheck','wait 8',
   f'screenshot logs/{label}-loaded.png','echo UTNT_TEST_END','wait 5','quit']
  r=run_case(a.engine,a.iwad,root=a.work,mod=a.mod,addon=ROOT/'tools/storm-tests',
   mapname='TNT01',renderer=backend,label=label,timeout=90,commands='; '.join(commands),
   settings=[('win_w',1938),('win_h',1127),('screenblocks',10),('vid_maxfps',60),
             ('gl_texture_filter',0),('con_notifytime',0)])
  if r['assertions']!=6:r['ok']=False;r['errors'].append('expected six map/save assertions')
  if r['ok']:
   r['motion']=motion(a.work/'logs',label)
   if not r['motion']['ok']:r['ok']=False;r['errors'].append('motion or stationary-region check failed')
  if not r['ok']:print(Path(r['log']).read_text()[-2500:])
  results.append(r)
 (a.work/'logs/storm-results.json').write_text(json.dumps(results,indent=2))
 print(json.dumps(results,indent=2))
 return 0 if all(r['ok'] for r in results) else 1

if __name__=='__main__':raise SystemExit(main())
