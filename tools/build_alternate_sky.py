"""TNT04C alternate ending: amber clouds, a compact beam opening and sparse debris.

Uses the shared CN card intersection and comet flame implementation. Production
rasters contain neither the level beam nor baked moving objects.
"""
from pathlib import Path
import math
import numpy as np
from PIL import Image
from build_rift_sky import sample
from build_storm_sky import FACES,FORMS,smooth
from rift_rocks import basis
ROOT=Path(__file__).resolve().parent.parent
EYE=(962.,13570.,-5350.)
BEAM=(962.,13570.,-992.)
SPAN=8000.
# yaw, elevation, tangent width/height, UV bounds, light, ellipse radius,
# phase, world distance, signed orbit seconds, sampler name.
LAYERS=[
 (130,34,.40,.50,(.770,.430,.925,.746),1.0,.007,1.3,70000,240,'rockmap'),
 (15,29,.25,.32,(.925,.430,.770,.746),.85,.006,4.1,100000,-270,'rockmap'),
 (65,24,.38,.38,(0,0,.5,1),.82,.006,2.2,36000,-220,'platformmap'),
 (165,31,.20,.20,(.5,0,1,1),.70,.005,4.8,65000,280,'platformmap'),
 (290,25,.18,.21,(.245,.270,.420,.540),.72,.007,3.1,55000,230,'rockmap'),
]

def calls():
 def vec(xs):return 'vec%d('%len(xs)+','.join(f'{v:.9f}' for v in xs)+')'
 result=[]
 for yaw,e,w,h,uv,light,motion,phase,distance,period,layer in sorted(LAYERS,key=lambda l:-l[8]):
  f,r,u=basis(yaw,e)
  result.append(' rocks=RiftRockLayer(rocks,'+layer+',ray,rockEye,'+','.join([vec(f),vec(r),vec(u),vec((w,h)),vec(uv),str(light),str(motion),str(phase),str(distance)+'.0',str(period)+'.0'])+');')
 return '\n'.join(result)

def composite(ray,images):
 result=np.zeros(ray.shape[:-1]+(4,),dtype=np.float32)
 for yaw,e,w,h,uv,light,motion,phase,distance,period,layer in sorted(LAYERS,key=lambda l:-l[8]):
  f,r,u=basis(yaw,e);depth=np.sum(ray*f,axis=-1)
  hit=ray/np.maximum(depth,.001)[...,None]
  px=np.sum(hit*r,axis=-1)/w-motion*math.cos(phase)
  py=-np.sum(hit*u,axis=-1)/h+motion*.65*math.sin(phase)
  angle=.004*math.sin(phase);c,s=math.cos(angle),math.sin(angle)
  x=c*px-s*py+.5;y=s*px+c*py+.5
  edge=np.minimum.reduce([x,1-x,y,1-y]);weight=smooth(0,.025,edge)*(depth>.01)
  col=sample(images[layer],uv[0]+(uv[2]-uv[0])*x,uv[1]+(uv[3]-uv[1])*y)*weight[...,None]
  luma=np.sum(col[:,:,:3]*[.2126,.7152,.0722],axis=-1)
  col[:,:,:3]=luma[...,None]*[1.35,.90,.44]*light*smooth(-.25,.30,ray[:,:,1])[...,None]
  result=result*(1-col[:,:,3:4])+col
 return result

def build(root=ROOT):
 out=root/'tutnt';art=out/'graphics/alternate'
 def read(path):return np.asarray(Image.open(path).convert('RGB'),dtype=np.float32)/255
 top=read(art/'zenith.png');clouds=read(art/'clouds.png');images={}
 for key,path in [('rockmap',out/'graphics/rift/rocks-key.png'),('platformmap',art/'platforms-key.png')]:
  im=read(path);alpha=1-smooth(.03,.18,im[:,:,2]-np.maximum(im[:,:,0],im[:,:,1]));im[:,:,2]=np.minimum(im[:,:,2],np.maximum(im[:,:,0],im[:,:,1]))
  images[key]=np.dstack((im*alpha[:,:,None],alpha))
 def wrap(u,v):
  u=u%1;e=(.5*(1-smooth(0,.035,np.minimum(u,1-u))))[...,None]
  return sample(clouds,u,v)*(1-e)+sample(clouds,1-u,v)*e
 shared=Path(__file__).with_name('rift-material.glsl').read_text(encoding='utf-8').split('void SetupMaterial')[0]
 shared=shared.replace('vec4 behind,vec3 ray','vec4 behind,sampler2D layer,vec3 ray').replace('RiftSample(rockmap,','RiftSample(layer,').replace('float angle=.014','float angle=.004')
 shared=shared.replace('rock.rgb=mix(vec3(luma)*vec3(1.05,.94,.82),rock.rgb,.25)*light','rock.rgb=vec3(luma)*vec3(1.35,.90,.44)*light')
 material=Path(__file__).with_name('alternate-material.glsl').read_text(encoding='utf-8')
 comets=Path(__file__).with_name('war-comets.glsl').read_text(encoding='utf-8')
 n=1024;u,v=np.meshgrid(np.linspace(0,1,n,dtype=np.float32),np.linspace(0,1,n,dtype=np.float32));s=1-2*u;t=1-2*v;o=np.ones_like(s)
 rays=[(s,t,-o),(-o,t,-s),(-s,t,o),(o,t,s),(s,o,-t),(s,-o,-t)]
 gl=['skybox UACSKY { '+' '.join('UAC'+f for f in FACES)+' }']
 for face,form,(x,y,z) in zip(FACES,FORMS,rays):
  length=np.sqrt(x*x+y*y+z*z);x=x/length;y=y/length;z=z/length
  lon=np.arctan2(-z,-x);lat=np.arcsin(np.clip(y,-1,1))
  cap=smooth(.55,.85,y)[...,None]
  color=(wrap(lon/(2*math.pi)+.5,.60-lat/math.pi*.90)*(1-cap)+wrap(.5+x*.25,.25+z*.25)*cap)*.85*smooth(-.30,.35,y)[...,None]
  d=(BEAM[2]-EYE[2])/np.maximum(y,.001);pu=.5-x*d/SPAN;pv=.425-z*d/SPAN
  edge=np.minimum.reduce([pu,1-pu,pv,1-pv]);weight=(smooth(0,.13,edge)*smooth(.015,.10,y))[...,None]
  moving=smooth(.10,.20,np.sqrt((pu-.5)**2+(pv-.425)**2))
  nc=sample(top,pu+.001*moving*np.sin(pv*7),pv+.001*moving*np.sin(pu*8))
  color=color*(1-weight)+nc*weight
  rock=composite(np.dstack((x,y,z)),images)*smooth(.10,.16,np.sqrt((pu-.5)**2+(pv-.425)**2))[...,None]
  color=color*(1-rock[:,:,3:4])+rock[:,:,:3]
  dest=out/f'textures/UAC{face}.png';dest.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(np.uint8(np.clip(color*255,0,255))).save(dest)
  dest=out/f'shaders/alternate/sky-{face}.fp';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(comets+'\n'+shared+material.replace('@RAY@',form).replace('@ROCKS@',calls()),encoding='utf-8',newline='\n')
  gl.append(f'material texture UAC{face} {{ shader "shaders/alternate/sky-{face}.fp" texture nebulamap "graphics/alternate/zenith.png" texture rockmap "graphics/rift/rocks-key.png" texture platformmap "graphics/alternate/platforms-key.png" texture surroundmap "graphics/alternate/clouds.png" }}')
 (out/'GLDEFS.alternate').write_text('\n'.join(gl)+'\n',encoding='utf-8',newline='\n')

if __name__=='__main__':build()
