"""Rebuild TNT01's panoramic storm cubemap and animated material shaders.

Requires NumPy and Pillow. Original ImageGen textures remain unmodified.
The CPU projection is the static fallback; shaders composite moving clouds
behind stationary, blue-keyed mountains with explicit bilinear sampling.
"""
import argparse, math
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parent.parent
FACES=['N','E','S','W','U','D']
FORMS=['vec3(s,t,-1.0)','vec3(-1.0,t,-s)','vec3(-s,t,1.0)',
       'vec3(1.0,t,s)','vec3(s,1.0,-t)','vec3(s,-1.0,-t)']

def smooth(a,b,x):
 q=np.clip((x-a)/(b-a),0,1);return q*q*(3-2*q)

def sample(im,u,v):
 h,w=im.shape[:2];px=u*w-.5;py=np.clip(v, .5/h,1-.5/h)*h-.5
 ix=np.floor(px).astype(int);iy=np.floor(py).astype(int)
 fx=(px-ix)[...,None];fy=(py-iy)[...,None]
 a=im[iy,ix%w]*(1-fx)+im[iy,(ix+1)%w]*fx
 b=im[np.minimum(iy+1,h-1),ix%w]*(1-fx)+im[np.minimum(iy+1,h-1),(ix+1)%w]*fx
 return a*(1-fy)+b*fy

def wrapped(im,u,v):
 u=u%1;edge=.5*(1-smooth(0,.025,np.minimum(u,1-u)))
 return sample(im,u,v)*(1-edge[...,None])+sample(im,1-u,v)*edge[...,None]

def build(root):
 out=root/'tutnt';art=out/'graphics/storm'
 clouds=np.asarray(Image.open(art/'clouds.png').convert('RGB'),dtype=float)/255
 mountains=np.asarray(Image.open(art/'mountains-key.png').convert('RGB'),dtype=float)/255
 alpha=1-smooth(.02,.20,mountains[:,:,2]-np.maximum(mountains[:,:,0],mountains[:,:,1]))
 mountains[:,:,2]=np.minimum(mountains[:,:,2],mountains[:,:,1])
 # Key each texel before interpolation, avoiding blue fringes at ridge edges.
 mountains=np.dstack((mountains*alpha[:,:,None],alpha))
 n=768;u,v=np.meshgrid(np.linspace(0,1,n),np.linspace(0,1,n))
 s=1-2*u;t=1-2*v;o=np.ones_like(s)
 rays=[(s,t,-o),(-o,t,-s),(-s,t,o),(o,t,s),(s,o,-t),(s,-o,-t)]
 common=(Path(__file__).with_name('storm-material.glsl')).read_text()
 gl=['skybox USTSKY { '+' '.join('UST'+f for f in FACES)+' }']
 for face,form,(x,y,z) in zip(FACES,FORMS,rays):
  lat=np.arctan2(y,np.hypot(x,z));lon=np.arctan2(-z,-x)
  uvx=(lon/(2*math.pi)+.5+.125)%1
  skyv=np.clip(.92-lat/math.pi*1.84,0,1)
  base=wrapped(clouds,uvx,skyv)
  veil=wrapped(clouds,uvx+.071,np.clip(skyv*.94+.025,0,1))
  color=base*.82+veil*.18
  length=np.sqrt(x*x+y*y+z*z);rx=x/length;ry=y/length;rz=z/length
  topx=.5+rx/np.maximum(ry,.4)*.28;topv=.4+rz/np.maximum(ry,.4)*.28
  top=wrapped(clouds,topx,np.clip(topv,0,1))*.82+wrapped(clouds,topx*.94+.071,np.clip(topv*.94+.025,0,1))*.18
  overhead=smooth(.574,.906,ry)[...,None]
  color=color*(1-overhead)+top*overhead
  m=wrapped(mountains,uvx,np.clip(.82-lat/math.pi*1.4,0,1))
  color=color*(1-m[:,:,3:4])+m[:,:,:3]
  (out/'textures').mkdir(exist_ok=True)
  Image.fromarray(np.uint8(np.clip(color*255,0,255))).save(out/f'textures/UST{face}.png')
  shader=common.replace('@RAY@',form)
  p=out/f'shaders/storm/sky-{face}.fp';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(shader)
  gl.append(f'material texture UST{face} {{ shader "shaders/storm/sky-{face}.fp" texture cloudmap "graphics/storm/clouds.png" texture mountainmap "graphics/storm/mountains-key.png" }}')
 (out/'gldefs/GLDEFS.storm').parent.mkdir(parents=True,exist_ok=True)
 (out/'gldefs/GLDEFS.storm').write_text('\n'.join(gl)+'\n')

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT)
 build(p.parse_args().root)
