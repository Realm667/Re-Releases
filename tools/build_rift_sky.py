"""Build TNT04CN's approved cosmic rift cubemap and animated layered materials.

Source art stays unchanged. NumPy/Pillow only reproject it into engine cube faces;
the fixed camera projection preserves the approved mockup's composition.
"""
from pathlib import Path
import argparse,math
import numpy as np
from PIL import Image
from build_storm_sky import FACES,FORMS,smooth
ROOT=Path(__file__).resolve().parent.parent

def sample(im,u,v):
 h,w=im.shape[:2];px=np.clip(u*w-.5,0,w-1);py=np.clip(v*h-.5,0,h-1)
 ix=np.floor(px).astype(int);iy=np.floor(py).astype(int);fx=(px-ix)[...,None];fy=(py-iy)[...,None]
 return (im[iy,ix]*(1-fx)+im[iy,np.minimum(ix+1,w-1)]*fx)*(1-fy)+(im[np.minimum(iy+1,h-1),ix]*(1-fx)+im[np.minimum(iy+1,h-1),np.minimum(ix+1,w-1)]*fx)*fy

def build(root):
 out=root/'tutnt';art=out/'graphics/rift'
 def read(name):return np.asarray(Image.open(art/name).convert('RGB'),dtype=np.float32)/255
 nebula=read('nebula.png');surround=read('surround.png');rocks=read('rocks-key.png')
 alpha=1-smooth(.03,.18,rocks[:,:,2]-np.maximum(rocks[:,:,0],rocks[:,:,1]))
 rocks[:,:,2]=np.minimum(rocks[:,:,2],np.maximum(rocks[:,:,0],rocks[:,:,1]))
 rocks=np.dstack((rocks*alpha[:,:,None],alpha))
 def wrap(u,v):
  u=u%1;e=(.5*(1-smooth(0,.035,np.minimum(u,1-u))))[...,None]
  return sample(surround,u,v)*(1-e)+sample(surround,1-u,v)*e
 n=1024;u,v=np.meshgrid(np.linspace(0,1,n,dtype=np.float32),np.linspace(0,1,n,dtype=np.float32));s=1-2*u;t=1-2*v;o=np.ones_like(s)
 rays=[(s,t,-o),(-o,t,-s),(-s,t,o),(o,t,s),(s,o,-t),(s,-o,-t)]
 material=Path(__file__).with_name('rift-material.glsl').read_text();comets=Path(__file__).with_name('war-comets.glsl').read_text()
 gl=['skybox URFSKY { '+' '.join('URF'+f for f in FACES)+' }']
 for face,form,(x,y,z) in zip(FACES,FORMS,rays):
  length=np.sqrt(x*x+y*y+z*z);x=x/length;y=y/length;z=z/length
  lon=np.arctan2(-z,-x);lat=np.arcsin(np.clip(y,-1,1))
  color=wrap(lon/(2*math.pi)+.5,.5-lat/math.pi)
  cap=smooth(.55,.85,np.abs(y))[...,None]
  color=(color*(1-cap)+wrap(.5+x*.28,.5+z*.56)*cap)*.65
  depth=-.69165480*x+.20791169*y+.69165480*z
  pu=.5+(.70710678*x+.70710678*z)/(np.maximum(depth,.001)*2.666666667)
  pv=.5-(.14701577*x+.97814760*y-.14701577*z)/(np.maximum(depth,.001)*1.5)
  edge=np.minimum.reduce([pu,1-pu,pv,1-pv])
  weight=(smooth(-.055,.015,edge)*(depth>=.01))[...,None]
  rockweight=(smooth(0,.025,edge)*(depth>=.01))[...,None]
  nu=pu+.0025*np.sin(pv*7);nv=pv+.0025*np.sin(pu*8)
  nu=1-np.abs(1-np.abs(nu));nv=1-np.abs(1-np.abs(nv))
  nc=sample(nebula,nu,nv)*(.985+.015*np.sin(pu*3))[...,None]
  color=color*(1-weight)+nc*weight
  rock=sample(rocks,pu,pv)*rockweight;color=color*(1-rock[:,:,3:4])+rock[:,:,:3]
  dest=out/f'textures/URF{face}.png';dest.parent.mkdir(parents=True,exist_ok=True)
  Image.fromarray(np.uint8(np.clip(color*255,0,255))).save(dest)
  dest=out/f'shaders/rift/sky-{face}.fp';dest.parent.mkdir(parents=True,exist_ok=True)
  dest.write_text(comets+'\n'+material.replace('@RAY@',form),newline='\n')
  gl.append(f'material texture URF{face} {{ shader "shaders/rift/sky-{face}.fp" texture nebulamap "graphics/rift/nebula.png" texture rockmap "graphics/rift/rocks-key.png" texture surroundmap "graphics/rift/surround.png" }}')
 (out/'GLDEFS.rift').write_text('\n'.join(gl)+'\n',newline='\n')

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);build(p.parse_args().root)
