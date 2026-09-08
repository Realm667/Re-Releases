// Generated per cube face by tools/build_storm_sky.py. timer is engine time.
// Both moving cloud samples share spherical coordinates across all six faces.
vec4 MountainKey(vec4 c)
{
 c.a=1.0-smoothstep(0.02,0.20,c.b-max(c.r,c.g));
 c.b=min(c.b,c.g);c.rgb*=c.a;
 return c;
}
vec3 CloudSample(vec2 uv)
{
 vec2 size=vec2(textureSize(cloudmap,0)), d=1.0/size;
 vec2 p=uv*size-0.5, f=fract(p), b=(floor(p)+0.5)/size;
 vec2 lo=vec2(fract(b.x),clamp(b.y,d.y*0.5,1.0-d.y*0.5));
 vec2 hi=vec2(fract(b.x+d.x),clamp(b.y+d.y,d.y*0.5,1.0-d.y*0.5));
 return mix(mix(texture(cloudmap,lo).rgb,texture(cloudmap,vec2(hi.x,lo.y)).rgb,f.x),
            mix(texture(cloudmap,vec2(lo.x,hi.y)).rgb,texture(cloudmap,hi).rgb,f.x),f.y);
}
vec4 MountainSample(vec2 uv)
{
 vec2 size=vec2(textureSize(mountainmap,0)), d=1.0/size;
 vec2 p=uv*size-0.5, f=fract(p), b=(floor(p)+0.5)/size;
 vec2 lo=vec2(fract(b.x),clamp(b.y,d.y*0.5,1.0-d.y*0.5));
 vec2 hi=vec2(fract(b.x+d.x),clamp(b.y+d.y,d.y*0.5,1.0-d.y*0.5));
 return mix(mix(MountainKey(texture(mountainmap,lo)),MountainKey(texture(mountainmap,vec2(hi.x,lo.y))),f.x),
            mix(MountainKey(texture(mountainmap,vec2(lo.x,hi.y))),MountainKey(texture(mountainmap,hi)),f.x),f.y);
}
vec3 CloudWrap(vec2 uv)
{
 uv.x=fract(uv.x);uv.y=clamp(uv.y,0.0,1.0);
 vec3 c=CloudSample(uv);
 float seam=0.5*(1.0-smoothstep(0.0,0.025,min(uv.x,1.0-uv.x)));
 if(seam>0.0)c=mix(c,CloudSample(vec2(1.0-uv.x,uv.y)),seam);
 return c;
}
vec4 MountainWrap(vec2 uv)
{
 uv.x=fract(uv.x);uv.y=clamp(uv.y,0.0,1.0);
 vec4 c=MountainSample(uv);
 float seam=0.5*(1.0-smoothstep(0.0,0.025,min(uv.x,1.0-uv.x)));
 if(seam>0.0)c=mix(c,MountainSample(vec2(1.0-uv.x,uv.y)),seam);
 return c;
}
void SetupMaterial(inout Material mat)
{
 float s=1.0-2.0*vTexCoord.x,t=1.0-2.0*vTexCoord.y;
 vec3 ray=normalize(vec3(1.0,t,s));
 float latitude=asin(ray.y);
 float longitude=atan(-ray.z,-ray.x)/6.283185307+0.625;
 float skyY=clamp(0.92-latitude/3.141592654*1.84,0.0,1.0);
 // Four times the original speed: one turn in roughly 7.6 and 18.1 minutes.
 vec3 cloud=CloudWrap(vec2(longitude+timer*0.00220,skyY));
 vec3 veil=CloudWrap(vec2(longitude+0.071-timer*0.00092,skyY*0.94+0.025));
 vec3 color=mix(cloud,veil,0.18);
 // Planar overhead projection removes the equirectangular pole singularity.
 // Blend in direction space, so the upper face and its neighbours agree.
 float overhead=smoothstep(0.574,0.906,ray.y);
 if(overhead>0.0)
 {
  vec2 top=vec2(0.5,0.40)+ray.xz/max(ray.y,0.4)*0.28;
  vec3 a=CloudWrap(top+vec2(timer*0.00220,0.0));
  vec3 b=CloudWrap(top*vec2(0.94,0.94)+vec2(0.071-timer*0.00092,0.025));
  color=mix(color,mix(a,b,0.18),overhead);
 }
 vec4 mountains=MountainWrap(vec2(longitude,0.82-latitude/3.141592654*1.4));
 mat.Base=vec4(color*(1.0-mountains.a)+mountains.rgb,1.0);
 mat.Normal=normalize(vWorldNormal.xyz);
}
