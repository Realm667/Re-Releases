"""Check TNT02 sky motion, lightning/world synchronization, roof gating and saves."""
import argparse,json,os
from pathlib import Path
import numpy as np
from PIL import Image
from check_engine import run_case,ROOT
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--engine',type=Path,default=os.environ.get('UTNT_ENGINE'));p.add_argument('--iwad',type=Path,default=os.environ.get('UTNT_IWAD'))
 p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3');p.add_argument('--work',type=Path,default=ROOT)
 p.add_argument('--fixture',type=Path,default=ROOT/'tools/thunder-tests');p.add_argument('--renderer',choices=['0','1','both'],default='both');a=p.parse_args()
 if not a.engine or not a.iwad:p.error('Set --engine and --iwad')
 results=[]
 for b in ['0','1'] if a.renderer=='both' else [a.renderer]:
  label='thunder-'+b
  cmd=['notarget','wait 350','netevent thunderflash 0','wait 70',f'screenshot logs/{label}-dark.png','netevent thunderroof 1','wait 175',f'screenshot logs/{label}-motion.png','netevent thunderflash 8 1','wait 70',f'screenshot logs/{label}-flash.png','netevent thundercheck',f'save {label}','wait 20',f'load {label}','wait 70','netevent thundercheck','netevent thunderview 2','wait 70','netevent thunderroof 0',f'screenshot logs/{label}-inside-flash.png','netevent thunderflash 0','wait 70',f'screenshot logs/{label}-inside-dark.png','netevent thunderview 3','wait 70','netevent thunderroof 0','netevent thunderview 5','wait 70',f'screenshot logs/{label}-seam.png','netevent thunderview 6','wait 70',f'screenshot logs/{label}-courtyard.png','netevent thunderrun','wait 140','netevent thunderrest','wait 20','echo UTNT_TEST_END','quit']
  r=run_case(a.engine,a.iwad,root=a.work,mod=a.mod,addon=a.fixture,mapname='TNT02',label=label,renderer=b,timeout=95,commands='; '.join(cmd),settings=[('win_w',1938),('win_h',1127),('vid_maxfps',60),('vid_activeinbackground',True),('vid_lowerinbackground',False),('i_pauseinbackground',False),('use_mouse',False),('gl_texture_filter',0),('screenblocks',10),('con_notifytime',0)])
  if r['ok']:
   def read(n):return np.asarray(Image.open(a.work/'logs'/f'{label}-{n}.png').convert('RGB'),dtype=float)
   dark,motion,flash=read('dark'),read('motion'),read('flash')
   r['cloud_motion']=float(np.abs(dark[60:250,700:1300]-motion[60:250,700:1300]).mean())
   r['cloud_flash_gain']=float((flash[40:320,850:1400]-dark[40:320,850:1400]).mean())
   r['world_flash_gain']=float((flash[560:700,200:650]-dark[560:700,200:650]).mean())
   r['inside_difference']=float(np.abs(read('inside-dark')[250:600,500:1400]-read('inside-flash')[250:600,500:1400]).mean())
   r['ok']=r['assertions']>=15 and r['cloud_motion']>.2 and r['cloud_flash_gain']>8 and r['world_flash_gain']>5 and r['inside_difference']<1
   if not r['ok']:r['errors'].append('image or assertion check failed')
  print(json.dumps(r),flush=True);results.append(r)
 (a.work/'logs/thunder-results.json').write_text(json.dumps(results,indent=2))
 return 0 if all(r['ok'] for r in results) else 1
if __name__=='__main__':raise SystemExit(main())
