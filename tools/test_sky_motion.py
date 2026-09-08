"""Check faster TNT01 clouds and the TNT03B storm eye in both renderers.
Requires NumPy/Pillow. Uses existing sky fixtures; no test actors are packaged.
"""
import argparse,json,os
from pathlib import Path
import numpy as np
from PIL import Image
from check_engine import run_case,ROOT

def read(path):return np.asarray(Image.open(path).convert('RGB'),dtype=float)

def vortex_rotation(a,b):
 # At pitch -89 the zenith lies just above the crosshair. Compare cloud
 # features in an annulus; ignore the calm eye, weapon, HUD and counters.
 angles=np.linspace(0,2*np.pi,1440,endpoint=False)
 radii=np.linspace(220,400,48)[:,None]
 def polar(im,shift):
  x=960+radii*np.cos(angles+shift);y=523+radii*np.sin(angles+shift)
  ix=np.floor(x).astype(int);iy=np.floor(y).astype(int);fx=(x-ix)[...,None];fy=(y-iy)[...,None]
  return ((im[iy,ix]*(1-fx)+im[iy,ix+1]*fx)*(1-fy)+
          (im[iy+1,ix]*(1-fx)+im[iy+1,ix+1]*fx)*fy)
 ref=polar(a,0);degrees=np.linspace(-8,8,321)
 errors=[float(np.abs(ref-polar(b,np.deg2rad(d))).mean()) for d in degrees]
 best=int(np.argmin(errors));zero=errors[len(degrees)//2]
 return {'estimated_rotation_degrees':float(degrees[best]),'aligned_error':errors[best],
         'unshifted_error':zero,'ok':bool(abs(degrees[best])>.5 and errors[best]<zero*.9)}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--engine',type=Path,default=os.environ.get('UTNT_ENGINE'))
 p.add_argument('--iwad',type=Path,default=os.environ.get('UTNT_IWAD'))
 p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3');p.add_argument('--work',type=Path,default=ROOT)
 p.add_argument('--map',choices=['TNT01','TNT03B'],help='Run only one map')
 p.add_argument('--renderer',choices=['0','1','both'],default='both')
 a=p.parse_args()
 if not a.engine or not a.iwad:p.error('Configure engine and IWAD')
 results=[]
 for backend in ['0','1'] if a.renderer=='both' else [a.renderer]:
  for mapname,kind,view in [('TNT01','storm',8),('TNT03B','caldera',11)]:
   if a.map and a.map!=mapname:continue
   label=f'sky-motion-{mapname}-{backend}';cmd=['notarget','wait 350',f'netevent {kind}view {view}','wait 8',f'screenshot logs/{label}-a.png','wait 175',f'screenshot logs/{label}-b.png']
   if kind=='caldera':
    cmd += ['netevent calderaview 8','wait 8',f'screenshot logs/{label}-horizon-a.png','wait 35',f'screenshot logs/{label}-horizon-b.png','netevent calderaview 6','wait 8',f'screenshot logs/{label}-miniature.png']
   cmd += [f'netevent {kind}view '+('7' if kind=='caldera' else '0'),'wait 8',f'screenshot logs/{label}-scene.png',f'save {label}','wait 8',f'load {label}','wait 15',f'netevent {kind}check','wait 8','echo UTNT_TEST_END','wait 5','quit']
   r=run_case(a.engine,a.iwad,root=a.work,mod=a.mod,addon=ROOT/f'tools/{kind}-tests',mapname=mapname,renderer=backend,label=label,timeout=70,commands='; '.join(cmd),settings=[('win_w',1938),('win_h',1127),('screenblocks',10),('vid_maxfps',60),('gl_texture_filter',0),('con_notifytime',0)])
   if r['assertions']!=6:r['ok']=False;r['errors'].append('expected six runtime/save assertions')
   if r['ok']:
    im1=read(a.work/'logs'/f'{label}-a.png');im2=read(a.work/'logs'/f'{label}-b.png')
    if kind=='caldera':
     r['rotation']=vortex_rotation(im1,im2)
     r['ok']=r['rotation']['ok']
     h1=read(a.work/'logs'/f'{label}-horizon-a.png');h2=read(a.work/'logs'/f'{label}-horizon-b.png')
     # Below 40-degree elevation the panorama is time independent.
     r['horizon_difference']=float(np.abs(h1[400:500,200:600]-h2[400:500,200:600]).mean())
     # Subpixel camera/render rounding may change an 8-bit sample by one level.
     r['ok']=r['ok'] and r['horizon_difference']<.25
    else:
     r['cloud_difference']=float(np.abs(im1[30:150,700:1200]-im2[30:150,700:1200]).mean())
     r['mountain_difference']=float(np.abs(im1[400:520,40:300]-im2[400:520,40:300]).mean())
     r['ok']=r['cloud_difference']>.15 and r['mountain_difference']<.05
    if not r['ok']:r['errors'].append('sky motion or stationary control failed')
   print(json.dumps(r),flush=True);results.append(r)
 (a.work/'logs/sky-motion-results.json').write_text(json.dumps(results,indent=2))
 return 0 if all(r['ok'] for r in results) else 1

if __name__=='__main__':raise SystemExit(main())
