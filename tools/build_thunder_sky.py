"""Build TNT02's animated thunder sky from the approved cloud/mountain artwork.

Python/NumPy/Pillow. All 25 sky states share six fallback faces and six programs;
texture aspect ratios carry the 8-step pulse at three sky locations.
The normal and flash materials use identical texture coordinates and clocks.
"""
import argparse,math
from pathlib import Path
import numpy as np
from PIL import Image
from build_storm_sky import FACES,FORMS,smooth,wrapped
ROOT=Path(__file__).resolve().parent.parent

def build(root):
 out=root/'tutnt';art=out/'graphics/thunder'
 clouds=np.asarray(Image.open(art/'clouds.png').convert('RGB'),dtype=float)/255
 mountains=np.asarray(Image.open(art/'mountains.png').convert('RGB'),dtype=float)/255
 alpha=1-smooth(.15,.35,mountains[:,:,2]-np.maximum(mountains[:,:,0],mountains[:,:,1]))
 mountains[:,:,2]=np.minimum(mountains[:,:,2],np.maximum(mountains[:,:,0],mountains[:,:,1])+.08)
 mountains=np.dstack((mountains*alpha[:,:,None],alpha))
 n=768;u,v=np.meshgrid(np.linspace(0,1,n),np.linspace(0,1,n));s=1-2*u;t=1-2*v;o=np.ones_like(s)
 rays=[(s,t,-o),(-o,t,-s),(-s,t,o),(o,t,s),(s,o,-t),(s,-o,-t)]
 common=Path(__file__).with_name('thunder-material.glsl').read_text(encoding='utf-8')
 gl=[];textures=[]
 for f,(x,y,z) in zip(FACES,rays):
  length=np.sqrt(x*x+y*y+z*z);rx=x/length;ry=y/length;rz=z/length
  lat=np.arcsin(ry);longitude=np.arctan2(-z,-x)/(2*math.pi)+.625
  skyv=np.clip(.90-lat/math.pi*1.7,0,1)
  cloud=wrapped(clouds,longitude,skyv)*.82+wrapped(clouds,longitude+.09,skyv*.96+.02)*.18
  tx=.5+rx/np.maximum(ry,.4)*.28;ty=.40+rz/np.maximum(ry,.4)*.28
  top=wrapped(clouds,tx,ty)*.82+wrapped(clouds,tx+.09,ty*.96+.02)*.18
  overhead=smooth(.574,.906,ry)[...,None];cloud=cloud*(1-overhead)+top*overhead
  mountain=wrapped(mountains,longitude,1.06-lat/math.pi*2.2)
  rgb=cloud*.88*(1-mountain[:,:,3:4])+mountain[:,:,:3]*.74
  p=out/f'textures/UGT0{f}.png';p.parent.mkdir(parents=True,exist_ok=True)
  Image.fromarray(np.uint8(np.clip(rgb*255,0,255))).save(p)
 for face,form in zip(FACES,FORMS):
  p=out/f'shaders/thunder/sky-{face}.fp';p.parent.mkdir(parents=True,exist_ok=True)
  p.write_text(common.replace('@RAY@',form),encoding='utf-8',newline='\n')
 for state in range(25):
  gl.append('skybox UGT'+str(state)+' { '+' '.join('UGT'+str(state)+f for f in FACES)+' }')
  for f in FACES:
   # Padding encodes the state without extra bitmaps; the first patch fills
   # the right edge for the software fallback, the second retains the face.
   if state:textures.append(f'Texture UGT{state}{f}, {768+state}, 768 {{ Patch UGT0{f}, {state}, 0 Patch UGT0{f}, 0, 0 }}')
   gl.append(f'material texture UGT{state}{f} {{ shader "shaders/thunder/sky-{f}.fp" texture cloudmap "graphics/thunder/clouds.png" texture mountainmap "graphics/thunder/mountains.png" }}')
 gl.append('HardwareShader PostProcess scene { Name "UTNTThunderExposure" Shader "shaders/thunder-exposure.fp" 330 Uniform float amount }')
 (out/'GLDEFS.thunder').write_text('\n'.join(gl)+'\n',encoding='utf-8',newline='\n')
 (out/'TEXTURES.thunder').write_text('\n'.join(textures)+'\n',encoding='utf-8',newline='\n')

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);build(p.parse_args().root)
