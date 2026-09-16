"""Explicit authoring of TNT04B inferno materials. Never called by packaging.
Original generated artwork and all final material/fallback outputs live in tutnt/.
"""
from pathlib import Path
import math
import numpy as np
from PIL import Image
from build_storm_sky import FACES,smooth,wrapped
from build_ash_sky import tile
ROOT=Path(__file__).resolve().parents[1]
def build(root=ROOT):
 out=root/'tutnt';art=out/'graphics/inferno'
 read=lambda name:np.asarray(Image.open(art/name).convert('RGB'),dtype=np.float32)/255
 pano=read('panorama.png');cloud=read('zenith.png');magma=read('magma.png')
 shader=Path(__file__).with_name('inferno-material.glsl').read_text(encoding='utf-8-sig')
 dest=out/'shaders/inferno';dest.mkdir(parents=True,exist_ok=True);(dest/'sky.fp').write_text(shader,encoding='utf-8',newline='\n')
 n=1024;u,v=np.meshgrid(np.linspace(0,1,n,dtype=np.float32),np.linspace(0,1,n,dtype=np.float32));s=1-2*u;t=1-2*v;o=np.ones_like(s)
 rays=[(s,t,-o),(-o,t,-s),(-s,t,o),(o,t,s),(s,o,-t),(s,-o,-t)]
 gl=[]
 for face,(x,y,z) in zip(FACES,rays):
  length=np.sqrt(x*x+y*y+z*z);x=x/length;y=y/length;z=z/length
  lon=np.arctan2(z,x)/(2*math.pi)+.5;lat=np.arcsin(y)
  color=wrapped(pano,lon,np.clip(.54-lat/math.pi*1.4,0,1))
  top=tile(cloud,.5+x/np.maximum(y,.35)*.26,.5+z/np.maximum(y,.35)*.26)
  blend=smooth(.30,.75,y)[...,None];color=color*(1-blend)+top*blend
  bottom=tile(magma,.5+x/np.maximum(-y,.30)*.24,.5+z/np.maximum(-y,.30)*.24)
  blend=smooth(.34,.84,-y)[...,None];color=color*(1-blend)+bottom*blend
  Image.fromarray(np.uint8(np.clip(color*.91*255,0,255))).save(out/f'textures/UFI{face}.png')
  gl.append(f'material texture UFI{face} {{ shader "shaders/inferno/sky.fp" texture panoramamap "graphics/inferno/panorama.png" texture cloudmap "graphics/inferno/zenith.png" texture magmamap "graphics/inferno/magma.png" }}')
 gl.append('material texture UFIHAZE { shader "shaders/inferno/haze.fp" }')
 (out/'gldefs/GLDEFS.inferno').write_text('\n'.join(gl)+'\n',encoding='utf-8',newline='\n')
if __name__=='__main__':build()
