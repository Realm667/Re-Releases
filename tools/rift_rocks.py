"""Shared sky-rock layout for animated materials and the static cubemap fallback.

Angles are world yaw/elevation; spans are tangent-plane width/height. UV bounds
select intact clusters in the existing keyed artwork, without modifying it.
"""
import math
import numpy as np

# World reference eye preserves the approved composition at the arena center.
REFERENCE_EYE=(128.0,-320.0,3241.0)
# yaw, elevation, width, height, UV bounds, light, radius, phase, distance, period
# Signed periods set opposite orbit directions; all are 2-4 minutes.
LAYERS=[
 (315,12,2.666666667,1.5,(0,0,1,1),.72,.004,0,55000,190),
 (80,48,.36,.48,(.770,.430,.925,.746),.90,.018,1.3,90000,220),
 (175,38,.50,.48,(.925,.430,.770,.746),.82,.016,3.7,110000,-240),
 (265,42,.27,.32,(.770,.430,.925,.746),.72,.014,5.1,140000,205),
 (120,27,.50,.44,(.245,.270,.420,.540),.86,.022,2.2,18000,-150),
 (215,23,.55,.66,(.560,.540,.720,.910),.77,.020,4.5,26000,130),
 (20,35,.44,.46,(.420,.270,.245,.540),.82,.017,6.0,32000,-170),
]

def basis(yaw,elevation):
 a,e=math.radians(yaw),math.radians(elevation)
 return ((-math.cos(a)*math.cos(e),math.sin(e),-math.sin(a)*math.cos(e)),
         (-math.sin(a),0,math.cos(a)),
         (math.cos(a)*math.sin(e),math.cos(e),math.sin(a)*math.sin(e)))

def shader_calls():
 def vec(xs):return 'vec%d('%len(xs)+','.join(f'{v:.9f}' for v in xs)+')'
 calls=[]
 for yaw,e,w,h,uv,light,motion,phase,distance,period in sorted(LAYERS,key=lambda l:-l[8]):
  f,r,u=basis(yaw,e)
  calls.append(' rocks=RiftRockLayer(rocks,ray,rockEye,'+','.join([vec(f),vec(r),vec(u),vec((w,h)),vec(uv),f'{light:.9f}',f'{motion:.9f}',f'{phase:.9f}',f'{distance:.9f}',f'{period:.9f}'])+');')
 return '\n'.join(calls)

def camera_offset(eye):
 delta=np.asarray(eye)-REFERENCE_EYE
 return np.array([-delta[0],delta[2],-delta[1]])

def project(layer,ray,eye=REFERENCE_EYE,time=0):
 yaw,e,w,h,uv,light,motion,phase,distance,period=layer
 f,r,u=basis(yaw,e);offset=camera_offset(eye);depth=np.sum(ray*f,axis=-1)
 plane=distance-np.dot(offset,f)
 hit=ray*(plane/np.maximum(depth,.001))[...,None]+offset
 theta=time*(2*math.pi/period)+phase
 px=np.sum(hit*r,axis=-1)/(distance*w)-motion*math.cos(theta)
 py=-np.sum(hit*u,axis=-1)/(distance*h)+motion*.65*math.sin(theta)
 angle=.014*math.sin(time*.023+phase);c,s=math.cos(angle),math.sin(angle)
 return c*px-s*py+.5,s*px+c*py+.5,(depth>.01)&(plane>0)

def composite(ray,keyed,sample,smooth,clearance,time=0,eye=REFERENCE_EYE):
 result=np.zeros(ray.shape[:-1]+(4,),dtype=np.float32)
 for layer in sorted(LAYERS,key=lambda l:-l[8]):
  yaw,e,w,h,uv,light,motion,phase,distance,period=layer
  x,y,visible=project(layer,ray,eye,time)
  edge=np.minimum.reduce([x,1-x,y,1-y]);weight=smooth(0,.025,edge)*visible
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
