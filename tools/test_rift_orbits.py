"""Check each closed orbital path against world-space plane projection."""
import json,math
import numpy as np
from rift_rocks import LAYERS,REFERENCE_EYE,basis,project

def check():
 maximum_error=0
 for layer in LAYERS:
  yaw,e,w,h,uv,light,radius,phase,distance,period=layer
  assert 120<=abs(period)<=240
  f,r,u=map(np.asarray,basis(yaw,e))
  def center(time):
   theta=time*2*math.pi/period+phase
   return f*distance+r*(radius*w*distance*math.cos(theta))+u*(radius*.65*h*distance*math.sin(theta))
  assert np.linalg.norm(center(0)-center(abs(period)))<1e-8
  for time in np.linspace(0,abs(period),17):
   point=center(time)
   # A ray to the moving object's true centre must hit the image centre.
   for translation in [(0,0,0),(512,-384,1600)]:
    eye=np.asarray(REFERENCE_EYE)+translation
    dx,dy,dz=translation;direction=point-[-dx,dz,-dy];direction/=np.linalg.norm(direction)
    x,y,visible=project(layer,direction,eye,time)
    error=max(abs(float(x)-.5),abs(float(y)-.5));maximum_error=max(maximum_error,error)
    assert visible and error<1e-10
 return dict(ok=True,ellipses=len(LAYERS),projection_cases=len(LAYERS)*17*2,maximum_center_error=maximum_error)
if __name__=='__main__':print(json.dumps(check(),indent=2))
