// Pure distant sky decoration: no gameplay actors, damage, sound or random state.
// Longitude is wrapped so trails cross cube faces and the panorama seam smoothly.
vec3 WarComets(vec3 color, vec3 ray)
{
 float lon=atan(-ray.z,-ray.x), lat=asin(clamp(ray.y,-1.0,1.0));
 for(int i=0;i<7;i++)
 {
  float seed=float(i), period=32.0+seed*2.7;
  float phase=mod(timer+seed*7.31,period)/period;
  float life=smoothstep(0.0,0.06,phase)*(1.0-smoothstep(0.70,0.86,phase));
  float headLat=1.02-phase*1.28;
  float headLon=seed*0.8976+0.28-phase*0.43;
  float dx=mod(lon-headLon+3.141592654,6.283185307)-3.141592654;
  // Tail points back along the shallow diagonal descent, away from the head.
  float along=lat-headLat;
  float crossTrail=(dx-along*0.336)*cos(lat);
  float tail=clamp(along/0.17,0.0,1.0);
  float width=mix(0.0035,0.0005,tail);
  float turbulence=sin(along*245.0-timer*6.0+seed)*sin(along*133.0+timer*4.2)*0.0012*tail;
  float flame=exp(-pow((crossTrail+turbulence)/width,2.0))*exp(-max(along,0.0)/0.055);
  flame*=smoothstep(-0.009,0.003,along)*(1.0-smoothstep(0.11,0.18,along));
  float head=exp(-pow(dx*cos(lat)/0.0042,2.0)-pow(along/0.0055,2.0));
  float halo=exp(-pow(crossTrail/0.014,2.0)-pow(along/0.025,2.0));
  float ember=0.82+0.18*sin(timer*8.0+along*360.0+seed*3.0);
  vec3 fire=mix(vec3(1.5,0.13,0.012),vec3(2.4,0.78,0.12),exp(-max(along,0.0)/0.026));
  color+=life*(fire*flame*ember+vec3(3.2,2.25,0.9)*head+vec3(0.30,0.035,0.003)*halo);
 }
 return color;
}

// Spherical sampling keeps cloud motion continuous across cube faces.
// Explicit interpolation also works with Doom's nearest-neighbour texture setting.
vec3 SkySample(vec2 uv)
{
 vec2 sz=vec2(textureSize(cloudmap,0));
 vec2 p=uv*sz-0.5, f=fract(p), b=(floor(p)+0.5)/sz;
 vec2 stepUV=1.0/sz;
 vec3 a=texture(cloudmap,vec2(fract(b.x),clamp(b.y,stepUV.y*0.5,1.0-stepUV.y*0.5))).rgb;
 vec3 c=texture(cloudmap,vec2(fract(b.x+stepUV.x),clamp(b.y,stepUV.y*0.5,1.0-stepUV.y*0.5))).rgb;
 vec3 d=texture(cloudmap,vec2(fract(b.x),clamp(b.y+stepUV.y,stepUV.y*0.5,1.0-stepUV.y*0.5))).rgb;
 vec3 e=texture(cloudmap,vec2(fract(b.x+stepUV.x),clamp(b.y+stepUV.y,stepUV.y*0.5,1.0-stepUV.y*0.5))).rgb;
 return mix(mix(a,c,f.x),mix(d,e,f.x),f.y);
}
vec3 SkyWrap(vec2 uv)
{
 uv.x=fract(uv.x);
 vec3 c=SkySample(uv);
 float edge=0.5*(1.0-smoothstep(0.0,0.035,min(uv.x,1.0-uv.x)));
 if(edge>0.0)c=mix(c,SkySample(vec2(1.0-uv.x,uv.y)),edge);
 return c;
}
void SetupMaterial(inout Material mat)
{
 float s=1.0-2.0*vTexCoord.x, t=1.0-2.0*vTexCoord.y;
 vec3 r=normalize(vec3(s,t,-1.0));
 vec2 uv=vec2(fract((atan(-r.z,-r.x)-4.712388980)/6.283185307+0.5),clamp(0.60-asin(r.y)/3.141592654*1.2,0.001,0.999));
 float high=smoothstep(0.65,0.85,r.y);
 vec3 color=SkyWrap(uv);
 if(high>0.0)
 {
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
 }
 // Preserve dim valleys while keeping the canopy subordinate to the architecture.
 float canopy=smoothstep(0.15,0.55,r.y);
 mat.Base=vec4(WarComets(color*mix(0.9,0.70,canopy)*0.985,r),1.0);
 mat.Normal=normalize(vWorldNormal.xyz);
}
