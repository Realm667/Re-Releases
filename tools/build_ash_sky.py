"""Reproject approved TNT04B art and combine it with the shared TNT04A comets.
CPU projection supplies static fallback faces; runtime adds motion and lightning.
Requires NumPy and Pillow. Does not regenerate map geometry or alter source art.
"""
from pathlib import Path
import argparse,math
import numpy as np
from PIL import Image
from build_storm_sky import FACES,FORMS,smooth,wrapped
ROOT=Path(__file__).resolve().parent.parent

def tile(im,u,v):
 # Match the shader's bilinear repeat and symmetric seam blend on both axes.
 u=u%1;v=v%1
 def raw(x,y):
  h,w=im.shape[:2];px=x*w-.5;py=y*h-.5;ix=np.floor(px).astype(int);iy=np.floor(py).astype(int)
  fx=(px-ix)[...,None];fy=(py-iy)[...,None]
  a=im[iy%h,ix%w]*(1-fx)+im[iy%h,(ix+1)%w]*fx
  b=im[(iy+1)%h,ix%w]*(1-fx)+im[(iy+1)%h,(ix+1)%w]*fx
  return a*(1-fy)+b*fy
 ex=(.5*(1-smooth(0,.025,np.minimum(u,1-u))))[...,None]
 ey=(.5*(1-smooth(0,.025,np.minimum(v,1-v))))[...,None]
 a=raw(u,v)*(1-ex)+raw(1-u,v)*ex;b=raw(u,1-v)*(1-ex)+raw(1-u,1-v)*ex
 return a*(1-ey)+b*ey

def build(root):
 out=root/'tutnt';art=out/'graphics/ash'
 pano=np.asarray(Image.open(art/'mountains-key.png').convert('RGB'),dtype=float)/255
 reverse=np.asarray(Image.open(art/'reverse-key.png').convert('RGB'),dtype=float)/255
 cloud=np.asarray(Image.open(art/'clouds.png').convert('RGB'),dtype=float)/255
 common=Path(__file__).with_name('ash-material.glsl').read_text()
 comets=Path(__file__).with_name('war-comets.glsl').read_text()
 def key(im):
  alpha=1-smooth(.03,.18,im[:,:,2]-np.maximum(im[:,:,0],im[:,:,1]))
  im[:,:,2]=np.minimum(im[:,:,2],im[:,:,1])
  return np.dstack((im*alpha[:,:,None],alpha))
 pano=key(pano);reverse=key(reverse)
 n=768;u,v=np.meshgrid(np.linspace(0,1,n),np.linspace(0,1,n));s=1-2*u;t=1-2*v;o=np.ones_like(s)
 rays=[(s,t,-o),(-o,t,-s),(-s,t,o),(o,t,s),(s,o,-t),(s,-o,-t)]
 for face,form,(x,y,z) in zip(FACES,FORMS,rays):
  length=np.sqrt(x*x+y*y+z*z);rx=x/length;ry=y/length;rz=z/length
  lat=np.arcsin(ry);turn=(np.arctan2(-z,-x)/(2*math.pi)+.25)%1;lon=(turn*2)%1
  hemisphere=smooth(-.045,.045,np.sin(turn*2*math.pi))[...,None]
  land=wrapped(pano,lon,np.clip(.78-lat/math.pi*1.8,0,1))*hemisphere+wrapped(reverse,lon,np.clip(.78-lat/math.pi*1.8,0,1))*(1-hemisphere)
  def cloud_at(x,y):return tile(cloud,x,y)*.82+tile(cloud,x*.94+.13,y*.94+.07)*.18
  clouds=cloud_at(turn*2,.8-lat/math.pi*1.3)
  tx=.5+rx/np.maximum(ry,.40)*.28;ty=.5+rz/np.maximum(ry,.40)*.28
  high=smooth(.45,.85,ry)[...,None];clouds=clouds*(1-high)+cloud_at(tx,ty)*high
  color=clouds*.82*(1-land[:,:,3:4])+land[:,:,:3]*.82
  dest=out/f'textures/UAS0{face}.png';dest.parent.mkdir(parents=True,exist_ok=True)
  Image.fromarray(np.uint8(np.clip(color*255,0,255))).save(dest)
  dest=out/f'shaders/ash/sky-{face}.fp';dest.parent.mkdir(parents=True,exist_ok=True)
  dest.write_text(comets+'\n'+common.replace('@RAY@',form),newline='\n')
 gl=[];textures=[]
 for state in range(9):
  gl.append('skybox UAS'+str(state)+' { '+' '.join(f'UAS{state}{f}' for f in FACES)+' }')
  for f in FACES:
   if state:textures.append(f'Texture UAS{state}{f}, {768+state}, 768 {{ Patch UAS0{f}, {state}, 0 Patch UAS0{f}, 0, 0 }}')
   gl.append(f'material texture UAS{state}{f} {{ shader "shaders/ash/sky-{f}.fp" texture panoramamap "graphics/ash/mountains-key.png" texture reversemap "graphics/ash/reverse-key.png" texture cloudmap "graphics/ash/clouds.png" }}')
 (out/'gldefs/GLDEFS.ash').parent.mkdir(parents=True,exist_ok=True)
 (out/'gldefs/GLDEFS.ash').write_text('\n'.join(gl)+'\n',newline='\n')
 (out/'textures/definitions/TEXTURES.ash').parent.mkdir(parents=True,exist_ok=True)
 (out/'textures/definitions/TEXTURES.ash').write_text('\n'.join(textures)+'\n',newline='\n')

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);build(p.parse_args().root)
