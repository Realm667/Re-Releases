"""Reproduce TNTLE's private material resources from the approved source art.
ImageGen originals remain byte-for-byte unchanged. Pillow/NumPy required.
"""
from pathlib import Path
import argparse,math,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
FACES=['N','E','S','W','U','D']
def smooth(a,b,x):
 q=np.clip((x-a)/(b-a),0,1);return q*q*(3-2*q)
def sample(im,u,v):
 h,w=im.shape[:2];px=u*w-.5;py=np.clip(v,.5/h,1-.5/h)*h-.5
 ix=np.floor(px).astype(int);iy=np.floor(py).astype(int);fx=(px-ix)[...,None];fy=(py-iy)[...,None]
 return ((im[iy,ix%w]*(1-fx)+im[iy,(ix+1)%w]*fx)*(1-fy)
  +(im[np.minimum(iy+1,h-1),ix%w]*(1-fx)+im[np.minimum(iy+1,h-1),(ix+1)%w]*fx)*fy)
def wrap(im,u,v):
 u=u%1;s=(.5*(1-smooth(0,.025,np.minimum(u,1-u))))[...,None]
 return sample(im,u,v)*(1-s)+sample(im,1-u,v)*s
def read(p):return np.asarray(Image.open(p).convert('RGB'),dtype=np.float32)/255.
def save(a,p):Image.fromarray(np.uint8(np.clip(a*255+.5,0,255))).save(p)
def build(root):
 out=root/'tutnt';art=out/'graphics/tntle';tx=out/'textures';sh=out/'shaders/tntle'
 tx.mkdir(parents=True,exist_ok=True);sh.mkdir(parents=True,exist_ok=True)
 cave=read(art/'cavern-panorama.png');vault=read(art/'cavern-vault.png')
 clouds=read(art/'ember-clouds.png');mountains=read(art/'ember-mountains-key.png')
 # Technical masks, not painted replacement artwork. Key before bilinear
 # interpolation to prevent chroma-blue fringes at the stationary ridge.
 alpha=1-smooth(.02,.20,mountains[:,:,2]-np.maximum(mountains[:,:,0],mountains[:,:,1]))
 mountains[:,:,2]=np.minimum(mountains[:,:,2],mountains[:,:,1])
 ridge=np.argmax(alpha>.8,axis=0);distance=np.arange(alpha.shape[0])[:,None]-ridge[None,:]
 mountains*= (.55+.45*smooth(0,14,distance))[:,:,None]
 mountains=np.dstack((mountains*alpha[:,:,None],alpha))
 save(mountains,art/'mountains-rgba.png')
 r,g,b=np.moveaxis(cave,-1,0)
 mask=smooth(.43,.72,r)*smooth(.10,.27,g)*smooth(.14,.32,r-g)*(1-smooth(.25,.5,b))
 rough=abs(r-np.roll(r,3,axis=0))+abs(r-np.roll(r,3,axis=1))
 haze=smooth(.16,.32,r)*(1-smooth(.38,.58,r))*smooth(.04,.13,g)*(1-mask)*(1-smooth(.015,.055,rough))
 save(np.dstack((mask,haze,np.zeros_like(mask))),art/'lava-flow-mask.png')
 n=1024;u,v=np.meshgrid((np.arange(n)+.5)/n,(np.arange(n)+.5)/n)
 s=1-2*u;t=1-2*v;o=np.ones_like(s)
 # Floor/ceiling UVs grow east/south; wall UVs follow clockwise sidedefs.
 rays=[(s,t,-o),(-o,t,-s),(-s,t,o),(o,t,s),(-s,o,t),(-s,-o,t)]
 common=(Path(__file__).with_name('tntle-common.glsl')).read_text()
 gl=[]
 for kind,prefix in [('cavern','ULC'),('night','ULN')]:
  shader=common+(Path(__file__).with_name('tntle-'+kind+'.glsl')).read_text()
  (sh/(kind+'.fp')).write_text(shader)
  for face,(x,y,z) in zip(FACES,rays):
   length=np.sqrt(x*x+y*y+z*z);rx=x/length;ry=y/length;rz=z/length
   lat=np.arcsin(ry);lon=np.arctan2(rz,rx)/(2*math.pi)+.625
   if kind=='cavern':
    c=wrap(cave,lon,.60-lat/math.pi*1.65)
    top=sample(vault,.5+rx/np.maximum(ry,.4)*.36,.5+rz/np.maximum(ry,.4)*.36)
    overhead=smooth(.64,.94,ry)[...,None];m=wrap(mask[:,:,None],lon,.60-lat/math.pi*1.65)
    c=(c*(1-overhead)+top*overhead)*(.62+m*.14)
   else:
    sy=.85-lat/math.pi*1.7
    c=wrap(clouds,lon,sy)*.8+wrap(clouds,lon+.17,sy*.88+.04)*.2
    tu=.5+rx/np.maximum(ry,.4)*.28;tv=.40+rz/np.maximum(ry,.4)*.28
    top=wrap(clouds,tu,tv)*.8+wrap(clouds,tu*.88+.17,tv*.88+.04)*.2
    overhead=smooth(.57,.92,ry)[...,None];c=(c*(1-overhead)+top*overhead)*.8
    m=wrap(mountains,lon,.65-lat*.75);c=c*(1-m[:,:,3:])+m[:,:,:3]*.78
   save(c,tx/(prefix+face+'.png'))
   maps=('texture panoramamap "graphics/tntle/cavern-panorama.png" texture vaultmap "graphics/tntle/cavern-vault.png" texture flowmask "graphics/tntle/lava-flow-mask.png"' if kind=='cavern' else 'texture cloudmap "graphics/tntle/ember-clouds.png" texture mountainmap "graphics/tntle/mountains-rgba.png"')
   gl.append(f'material texture {prefix+face} {{ shader "shaders/tntle/{kind}.fp" {maps} texture statemap "ULEDATA" }}')
 (out/'gldefs/GLDEFS.tntle').parent.mkdir(parents=True,exist_ok=True)
 (out/'gldefs/GLDEFS.tntle').write_text('\n'.join(gl)+'\n')
 print(json.dumps({'source_dimensions':{p.name:Image.open(p).size for p in art.glob('*.png')},'lava_mask_pixels':int(np.sum(mask>.5))}))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);build(p.parse_args().root)
