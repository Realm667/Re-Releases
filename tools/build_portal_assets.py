"""Deterministic material data and soft VFX primitives; no external artwork."""
from pathlib import Path
import numpy as np
from PIL import Image
import wave
import argparse
p=argparse.ArgumentParser(description=__doc__); p.add_argument('--out',type=Path,required=True); A=p.parse_args().out; A.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(667)
n=512
y,x=np.mgrid[:n,:n]/n
def noise():
 a=np.zeros((n,n))
 for size,weight in [(4,.48),(8,.25),(16,.14),(32,.08),(64,.05)]:
  grid=rng.random((size,size));xx=x*size;yy=y*size
  ix=xx.astype(int);iy=yy.astype(int);fx=xx-ix;fy=yy-iy
  fx=fx**3*(fx*(fx*6-15)+10);fy=fy**3*(fy*(fy*6-15)+10)
  value=(grid[iy,ix]*(1-fx)+grid[iy,(ix+1)%size]*fx)*(1-fy)+(grid[(iy+1)%size,ix]*(1-fx)+grid[(iy+1)%size,(ix+1)%size]*fx)*fy
  a+=value*weight
 return np.clip((a-a.min())/(a.max()-a.min()),0,1)
fields=[noise() for _ in range(4)]
Image.fromarray(np.uint8(np.stack(fields,axis=2)*255)).save(A/'flow.png')
h=fields[0]; dx=(np.roll(h,-1,1)-np.roll(h,1,1))*7;dy=(np.roll(h,-1,0)-np.roll(h,1,0))*7
normal=np.stack([-dx,-dy,np.ones_like(h)],axis=2);normal/=np.linalg.norm(normal,axis=2,keepdims=True)
Image.fromarray(np.uint8((normal*.5+.5)*255)).save(A/'normal.png')
# Software-renderer/editor fallback: a restrained dark crimson recess.
p=np.maximum(abs(x*2-1),abs(y*2-1));r=np.sqrt(((x-.5)*2)**2+((y-.5)*1.8)**2)
rim=np.exp(-(1-p)*65)*(0.6+fields[1]*.4)
v=np.clip((r-.20)*1.4,0,1)*(fields[0]**2)*.36+rim*.8
rgb=np.stack([v,v*.035,v*.018],axis=2)
Image.fromarray(np.uint8(np.clip(rgb,0,1)*255)).resize((256,256)).save(A/'portal.png')
for name,size,wisp in [('UPRMA0',32,False),('UPRWA0',128,True)]:
 yy,xx=np.mgrid[:size,:size];xx=(xx+.5-size/2)/(size/2);yy=(yy+.5-size/2)/(size/2)
 rr=(xx**2+yy**2)
 alpha=np.exp(-rr*(5 if wisp else 11))*np.clip((1-rr)*3,0,1)
 if wisp: alpha*=np.clip(.5+.5*np.sin(xx*13+np.sin(yy*8)*2),0,1)*.7
 rgba=np.zeros((size,size,4));rgba[:,:,0]=1;rgba[:,:,1]=.055+(0 if wisp else .5*np.exp(-rr*32));rgba[:,:,2]=.01+(0 if wisp else .08*np.exp(-rr*32));rgba[:,:,3]=alpha
 Image.fromarray(np.uint8(rgba*255)).save(A/(name+'.png'))
# Seamless seven-second local hum, with a low pulse and filtered suction.
rate=22050; t=np.arange(rate*7)/rate
raw=rng.standard_normal(len(t));kernel=np.exp(-np.arange(-6,7)**2/8);kernel/=kernel.sum()
noise_audio=sum(np.roll(raw,k-6)*v for k,v in enumerate(kernel))
env=np.maximum(0,np.sin(2*np.pi*t/7))**10
signal=(np.sin(2*np.pi*42*t)*.18+np.sin(2*np.pi*63*t)*.065+np.sin(2*np.pi*84*t)*.025)*(0.65+.35*env)
signal+=noise_audio*(.035+.10*env)
with wave.open(str(A/'portal-hum.wav'),'wb') as f:
 f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(np.int16(np.clip(signal,-1,1)*32767).tobytes())
print('Created',len(list(A.iterdir())),'material/particle/audio assets')
