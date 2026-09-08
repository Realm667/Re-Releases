"""Reproject the authored caldera panorama and regenerate its six material shaders.
Requires Python, Pillow and NumPy. Source art stays in tutnt/graphics/caldera.
The map geometry is authored in maps/tnt03b.wad and is not regenerated here.
"""
import math,argparse
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'tutnt'
def put(name,data):
 p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
 p.write_bytes(data.encode() if isinstance(data,str) else data)
def assets():
 sky=OUT/'graphics/caldera/panorama.png'
 rock=OUT/'textures/UCBASALT.png'
 put('graphics/caldera/panorama.png',sky.read_bytes());put('textures/UCBASALT.png',rock.read_bytes())
 im=np.asarray(Image.open(sky).convert('RGB'));h,w=im.shape[:2]
 n=768;u,v=np.meshgrid(np.linspace(0,1,n),np.linspace(0,1,n));s=1-2*u;t=1-2*v;o=np.ones_like(s)
 rays=[(s,t,-o),(-o,t,-s),(-s,t,o),(o,t,s),(s,o,-t),(s,-o,-t)]
 forms=['vec3(s,t,-1.0)','vec3(-1.0,t,-s)','vec3(-s,t,1.0)','vec3(1.0,t,s)','vec3(s,1.0,-t)','vec3(s,-1.0,-t)']
 names=['N','E','S','W','U','D'];gl=['skybox UCHSKY { '+' '.join('UCH'+x for x in names)+' }']
 for face,(x,y,z),form in zip(names,rays,forms):
  # Engine box coordinates are (x,up,y) and rotate -180 degrees around up.
  lon=np.arctan2(-z,-x);lat=np.arctan2(y,np.hypot(x,z))
  sx=((lon-math.radians(270))/(2*math.pi)+.5)%1*w-.5;sy=np.clip(.60-lat/math.pi*1.2,0,1)*(h-1)
  x0=np.floor(sx).astype(int);y0=np.floor(sy).astype(int);dx=(sx-x0)[...,None];dy=(sy-y0)[...,None]
  a=im[y0%h,x0%w]*(1-dx)+im[y0%h,(x0+1)%w]*dx
  b=im[np.minimum(y0+1,h-1),x0%w]*(1-dx)+im[np.minimum(y0+1,h-1),(x0+1)%w]*dx
  rgb=a*(1-dy)+b*dy
  def sample_at_x(px):
   ix=np.floor(px).astype(int);fx=(px-ix)[...,None]
   top=im[y0%h,ix%w]*(1-fx)+im[y0%h,(ix+1)%w]*fx
   bot=im[np.minimum(y0+1,h-1),ix%w]*(1-fx)+im[np.minimum(y0+1,h-1),(ix+1)%w]*fx
   return top*(1-dy)+bot*dy
  uvx=(sx+.5)/w;edge=np.clip(np.minimum(uvx,1-uvx)/.035,0,1);edge=(1-edge*edge*(3-2*edge))[...,None]*.5
  rgb=rgb*(1-edge)+sample_at_x(w-1-sx)*edge
  normy=y/np.sqrt(x*x+y*y+z*z);canopy=np.clip((normy-.15)/.4,0,1);canopy=canopy*canopy*(3-2*canopy)
  rgb*=((.9-.2*canopy)*.985)[...,None]
  p=OUT/f'textures/UCH{face}.png';p.parent.mkdir(exist_ok=True);Image.fromarray(np.uint8(np.clip(rgb,0,255))).save(p)
  gl.append(f'material texture UCH{face} {{ shader "shaders/caldera/sky-{face}.fp" texture cloudmap "graphics/caldera/panorama.png" }}')
  put(f'shaders/caldera/sky-{face}.fp',f'''// Spherical sampling keeps cloud motion continuous across cube faces.
// Explicit interpolation also works with Doom's nearest-neighbour texture setting.
vec3 SkySample(vec2 uv)
{{
 vec2 sz=vec2(textureSize(cloudmap,0));
 vec2 p=uv*sz-0.5, f=fract(p), b=(floor(p)+0.5)/sz;
 vec2 stepUV=1.0/sz;
 vec3 a=texture(cloudmap,vec2(fract(b.x),clamp(b.y,stepUV.y*0.5,1.0-stepUV.y*0.5))).rgb;
 vec3 c=texture(cloudmap,vec2(fract(b.x+stepUV.x),clamp(b.y,stepUV.y*0.5,1.0-stepUV.y*0.5))).rgb;
 vec3 d=texture(cloudmap,vec2(fract(b.x),clamp(b.y+stepUV.y,stepUV.y*0.5,1.0-stepUV.y*0.5))).rgb;
 vec3 e=texture(cloudmap,vec2(fract(b.x+stepUV.x),clamp(b.y+stepUV.y,stepUV.y*0.5,1.0-stepUV.y*0.5))).rgb;
 return mix(mix(a,c,f.x),mix(d,e,f.x),f.y);
}}
vec3 SkyWrap(vec2 uv)
{{
 uv.x=fract(uv.x);
 vec3 c=SkySample(uv);
 float edge=0.5*(1.0-smoothstep(0.0,0.035,min(uv.x,1.0-uv.x)));
 if(edge>0.0)c=mix(c,SkySample(vec2(1.0-uv.x,uv.y)),edge);
 return c;
}}
void SetupMaterial(inout Material mat)
{{
 float s=1.0-2.0*vTexCoord.x, t=1.0-2.0*vTexCoord.y;
 vec3 r=normalize({form});
 vec2 uv=vec2(fract((atan(-r.z,-r.x)-4.712388980)/6.283185307+0.5),clamp(0.60-asin(r.y)/3.141592654*1.2,0.001,0.999));
 float high=smoothstep(0.65,0.85,r.y);
 vec3 color=SkyWrap(uv);
 if(high>0.0)
 {{
  // Polar projection creates a continuous, slowly rotating cloud wall.
  // Restrict sampling to cloud-only rows; mountains below 40 degrees stay fixed.
  float radius=acos(clamp(r.y,0.0,1.0));
  float cloudY=0.06+0.28*smoothstep(0.10,0.90,radius);
  float spin=timer*0.0024; // One circuit in about seven minutes.
  float spiral=radius*0.18;
  vec3 wall=SkyWrap(vec2(uv.x+spin+spiral,cloudY));
  vec3 veil=SkyWrap(vec2(uv.x+timer*0.00170+spiral*1.3+0.12,cloudY*0.88+0.025));
  float eyeRadius=radius+0.012*sin(uv.x*31.41592654+spin*6.283185307);
  float eye=smoothstep(0.07,0.27,eyeRadius);
  vec3 vortex=mix(vec3(0.035,0.009,0.007),mix(wall,veil,0.14),eye);
  color=mix(color,vortex,high);
 }}
 // Preserve dim valleys while keeping the canopy subordinate to the architecture.
 float canopy=smoothstep(0.15,0.55,r.y);
 mat.Base=vec4(color*mix(0.9,0.70,canopy)*0.985,1.0);
 mat.Normal=normalize(vWorldNormal.xyz);
}}
''')
 put('GLDEFS.caldera','\n'.join(gl)+'\n')

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);a=p.parse_args()
 OUT=a.root/'tutnt';assets()
