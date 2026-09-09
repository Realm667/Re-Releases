"""Build Cursed Peak's shared animated sky and three software fallbacks.

Pillow/NumPy; original ImageGen sources are retained unmodified. The material
uses one 16x4 canvas for continuous saved clock/weather/fade values, not hundreds of
discrete sky textures. All six faces share the same world-space projection.
"""
import argparse,math
from pathlib import Path
import numpy as np
from PIL import Image
from build_storm_sky import FACES,FORMS,smooth,wrapped
ROOT=Path(__file__).resolve().parent.parent

def build(root,software_only=False):
 out=root/'tutnt';art=out/'graphics/cursed-peak'
 clouds=np.asarray(Image.open(art/'clouds.png').convert('RGB'),dtype=float)/255
 m=np.asarray(Image.open(art/'mountains-key.png').convert('RGB'),dtype=float)/255
 alpha=1-smooth(.12,.40,np.minimum(m[:,:,0],m[:,:,2])-m[:,:,1])
 m[:,:,0]=np.minimum(m[:,:,0],m[:,:,1]+.035);m[:,:,2]=np.minimum(m[:,:,2],m[:,:,1]+.055)
 m=np.repeat(np.sum(m*np.array([.2126,.7152,.0722]),axis=2,keepdims=True),3,axis=2)
 mountains=np.dstack((m*alpha[:,:,None],alpha))
 n=768;u,v=np.meshgrid(np.linspace(0,1,n),np.linspace(0,1,n));s=1-2*u;t=1-2*v;o=np.ones_like(s)
 rays=[(s,t,-o),(-o,t,-s),(-s,t,o),(o,t,s),(s,o,-t),(s,-o,-t)]
 common=Path(__file__).with_name('cursed-material.glsl').read_text()
 gl=[]
 projections=[] if software_only else list(zip(FACES,FORMS,rays))
 # A native cylindrical texture of the same name is FSkyBox's software source.
 # Without it the software renderer repeats only the first cube face.
 pu,pv=np.meshgrid(np.linspace(0,1,1024),np.linspace(0,1,256))
 plat=(.95-pv)*1.35;plon=pu*2*math.pi
 projections.append(('',None,(-np.cos(plon)*np.cos(plat),np.sin(plat),-np.sin(plon)*np.cos(plat))))
 for f,form,(x,y,z) in projections:
  length=np.sqrt(x*x+y*y+z*z);rx=x/length;ry=y/length;rz=z/length
  lat=np.arcsin(ry);lon=np.arctan2(-rz,-rx)/(2*math.pi)+.820
  skyv=np.clip(.95-lat/math.pi*1.8,0,1)
  def cloud_at(a,b):return wrapped(clouds,a,b)*.84+wrapped(clouds,a+.11,b*.93+.03)*.16
  cloud=cloud_at(lon,skyv)
  top=cloud_at(.5+rx/np.maximum(ry,.4)*.28,.4+rz/np.maximum(ry,.4)*.28)
  overhead=smooth(.574,.906,ry)[...,None];cloud=cloud*(1-overhead)+top*overhead
  gray=np.sum(cloud*np.array([.2126,.7152,.0722]),axis=2,keepdims=True)
  cloud=cloud*.25+gray*.75
  mountain=wrapped(mountains,lon,.74-lat/math.pi*2.7)
  direction=np.maximum(0,rz/np.maximum(np.sqrt(rx*rx+rz*rz),.001))**10
  silver=np.exp(-((lat-.60)/.33)**2)*direction
  for state,progress in enumerate([0,.60,1]):
   night=smooth(.40,1.,progress);dusk=smooth(.36,.53,progress)*(1-smooth(.79,.98,progress))
   sun_height=.70-.18*smooth(.40,.86,progress)
   horizon=np.exp(-((lat-sun_height)/.18)**2)
   tint=(1-night)*np.array([.94,.975,1.])+night*np.array([.92,.96,1.])
   color=cloud*(.84*(1-night)+.34*night)*tint
   color+=dusk*(direction*horizon)[...,None]*np.array([.34,.145,.055])*(.4+gray)
   separation=np.arccos(np.clip(ry*np.sin(sun_height)+rz*np.cos(sun_height),-1,1))
   disc=1-smooth(.013,.023,separation);halo=np.exp(-(separation/.07)**2)
   transmission=smooth(.22,.76,gray)
   color+=dusk*transmission*(disc*1.2+halo*.22)[...,None]*np.array([1.,.68,.32])
   color+=silver[...,None]*((1-night)*np.array([.04,.04,.038])+night*np.array([.03,.035,.043]))*gray
   land=mountain[:,:,:3]*(.97*(1-night)+.43*night)*tint
   land+=mountain[:,:,3:4]*dusk*direction[...,None]*np.array([.035,.018,.007])
   color=color*(1-mountain[:,:,3:4])+land
   haze=(.32*(1-smooth(0.,.65,lat)))[...,None]
   fade=np.floor((255-int(progress*165))*tint+.5)/255
   color=color*(1-haze)+fade*haze
   p=out/f'textures/UCP{state}{f}.png';p.parent.mkdir(parents=True,exist_ok=True)
   Image.fromarray(np.uint8(np.clip(color*255,0,255))).save(p)
  if form:
   p=out/f'shaders/cursed-peak/sky-{f}.fp';p.parent.mkdir(parents=True,exist_ok=True)
   p.write_text(common.replace('@RAY@',form),encoding='utf-8',newline='\n')
 for state in range(3):
  gl.append(f'skybox UCP{state} {{ '+' '.join(f'UCP{state}{f}' for f in FACES)+' }')
  for f in FACES:
   gl.append(f'material texture UCP{state}{f} {{ shader "shaders/cursed-peak/sky-{f}.fp" texture cloudmap "graphics/cursed-peak/clouds.png" texture mountainmap "graphics/cursed-peak/mountains-key.png" texture statemap "UCPDATA" }}')
 if not software_only:
  gl.append('''HardwareShader PostProcess scene
{
 Name "UTNTCursedSun"
 Shader "shaders/cursed-peak/sun-flare.fp" 330
 Texture cloudmap "graphics/cursed-peak/clouds.png"
 Texture mountainmap "graphics/cursed-peak/mountains-key.png"
 Uniform vec2 focus
 Uniform float amount
 Uniform float progress
 Uniform float phase
 Uniform float storm
}''')
  (out/'GLDEFS.cursed').write_text('\n'.join(gl)+'\n',encoding='utf-8',newline='\n')
  flare=Path(__file__).with_name('cursed-flare.glsl').read_text()
  (out/'shaders/cursed-peak/sun-flare.fp').write_text(flare.replace('@LAYERS@',common.split('void SetupMaterial')[0]),encoding='utf-8',newline='\n')

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--software-only',action='store_true')
 a=p.parse_args();build(a.root,a.software_only)
