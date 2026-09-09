"""Shared sky-rock layout for animated materials and the static cubemap fallback.

Angles are world yaw/elevation; spans are tangent-plane width/height. UV bounds
select intact clusters in the existing keyed artwork, without modifying it.
"""
import math
import numpy as np

# yaw, elevation, width, height, (u0,v0,u1,v1), light, motion, phase
LAYERS=[
 (315,12,2.666666667,1.5,(0,0,1,1),.72,.004,0),
 (80,48,.36,.48,(.770,.430,.925,.746),.90,.018,1.3),
 (175,38,.50,.48,(.925,.430,.770,.746),.82,.016,3.7),
 (265,42,.27,.32,(.770,.430,.925,.746),.72,.014,5.1),
 (120,27,.50,.44,(.245,.270,.420,.540),.86,.022,2.2),
 (215,23,.55,.66,(.560,.540,.720,.910),.77,.020,4.5),
 (20,35,.44,.46,(.420,.270,.245,.540),.82,.017,6.0),
]

def basis(yaw,elevation):
 a,e=math.radians(yaw),math.radians(elevation)
 return ((-math.cos(a)*math.cos(e),math.sin(e),-math.sin(a)*math.cos(e)),
         (-math.sin(a),0,math.cos(a)),
         (math.cos(a)*math.sin(e),math.cos(e),math.sin(a)*math.sin(e)))

def shader_calls():
 def vec(xs):return 'vec%d('%len(xs)+','.join(f'{v:.9f}' for v in xs)+')'
 calls=[]
 for yaw,e,w,h,uv,light,motion,phase in LAYERS:
  f,r,u=basis(yaw,e)
  calls.append(' rocks=RiftRockLayer(rocks,ray,'+','.join([vec(f),vec(r),vec(u),vec((w,h)),vec(uv),f'{light:.9f}',f'{motion:.9f}',f'{phase:.9f}'])+');')
 return '\n'.join(calls)

def composite(ray,keyed,sample,smooth,clearance,time=0):
 result=np.zeros(ray.shape[:-1]+(4,),dtype=np.float32)
 for yaw,e,w,h,uv,light,motion,phase in LAYERS:
  f,r,u=basis(yaw,e);depth=np.sum(ray*f,axis=-1)
  px=np.sum(ray*r,axis=-1)/(np.maximum(depth,.001)*w)
  py=-np.sum(ray*u,axis=-1)/(np.maximum(depth,.001)*h)
  angle=.014*math.sin(time*.023+phase);c,s=math.cos(angle),math.sin(angle)
  x=c*px-s*py+.5+motion*math.sin(time*.035+phase)
  y=s*px+c*py+.5+motion*math.sin(time*.052+phase*1.7)
  edge=np.minimum.reduce([x,1-x,y,1-y]);weight=smooth(0,.025,edge)*(depth>.01)
  active=weight>0
  rock=np.zeros_like(result)
  if active.any():
   col=sample(keyed,uv[0]+(uv[2]-uv[0])*x[active],uv[1]+(uv[3]-uv[1])*y[active])
   col*=weight[active,None]
   luma=np.sum(col[:,:3]*[.2126,.7152,.0722],axis=-1)
   col[:,:3]=(luma[:,None]*[1.05,.94,.82]*.75+col[:,:3]*.25)*light*smooth(-.25,.30,ray[:,:,1][active,None])
   rock[active]=col
  result=result*(1-rock[:,:,3:4])+rock
 return result*clearance[:,:,None]
