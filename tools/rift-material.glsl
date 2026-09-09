// World-ray projection keeps the approved view fixed while clouds drift behind rocks.
vec4 RiftKey(vec4 c)
{
 c.a=1.0-smoothstep(.03,.18,c.b-max(c.r,c.g));
 c.b=min(c.b,max(c.r,c.g));c.rgb*=c.a;return c;
}
vec4 RiftSample(sampler2D layer,vec2 uv,bool key)
{
 vec2 sz=vec2(textureSize(layer,0)),d=1.0/sz;
 vec2 p=uv*sz-.5,f=fract(p),b=(floor(p)+.5)/sz;
 vec2 lo=clamp(b,d*.5,1.0-d*.5),hi=clamp(b+d,d*.5,1.0-d*.5);
 vec4 a=texture(layer,lo),c=texture(layer,vec2(hi.x,lo.y));
 vec4 e=texture(layer,vec2(lo.x,hi.y)),g=texture(layer,hi);
 if(key){a=RiftKey(a);c=RiftKey(c);e=RiftKey(e);g=RiftKey(g);}
 return mix(mix(a,c,f.x),mix(e,g,f.x),f.y);
}
vec3 RiftWrap(vec2 uv)
{
 uv=vec2(fract(uv.x),clamp(uv.y,0.0,1.0));
 float seam=.5*(1.0-smoothstep(0.0,.035,min(uv.x,1.0-uv.x)));
 return mix(RiftSample(surroundmap,uv,false).rgb,RiftSample(surroundmap,vec2(1.0-uv.x,uv.y),false).rgb,seam);
}
vec3 RiftSurround(vec3 ray)
{
 float lon=atan(-ray.z,-ray.x),lat=asin(clamp(ray.y,-1.0,1.0));
 vec2 uv=vec2(lon/6.283185307+.5+timer*.000045,.5-lat/3.141592654);
 vec3 color=RiftWrap(uv);
 // Planar pole caps converge to a single value instead of stretching stars.
 float cap=smoothstep(.55,.85,abs(ray.y));
 vec2 pole=vec2(.5+ray.x*.28,.5+ray.z*.56);
 return mix(color,RiftWrap(pole),cap)*.65;
}
void SetupMaterial(inout Material mat)
{
 float s=1.0-2.0*vTexCoord.x,t=1.0-2.0*vTexCoord.y;
 vec3 ray=normalize(@RAY@);
 // Approved screenshot: yaw 315 degrees, pitch -12, widescreen 90-degree base FOV.
 vec3 forward=vec3(-.69165480,.20791169,.69165480);
 vec3 right=vec3(.70710678,0.0,.70710678),up=vec3(.14701577,.97814760,-.14701577);
 float depth=dot(ray,forward);
 vec2 uv=vec2(.5+dot(ray,right)/(max(depth,.001)*2.666666667),.5-dot(ray,up)/(max(depth,.001)*1.5));
 float edge=min(min(uv.x,1.0-uv.x),min(uv.y,1.0-uv.y));
 float weight=smoothstep(-.055,.015,edge)*step(.01,depth);
 float rockWeight=smoothstep(0.0,.025,edge)*step(.01,depth);
 vec3 color=RiftSurround(ray);
 vec4 rocks=vec4(0.0);
 if(weight>0.0)
 {
  vec2 drift=.0025*vec2(sin(timer*.024+uv.y*7.0),sin(timer*.017+uv.x*8.0));
  // Reflect the narrow outer feather instead of stretching the last texel row.
  vec2 nebulaUV=1.0-abs(1.0-abs(uv+drift));
  vec3 nebula=RiftSample(nebulamap,nebulaUV,false).rgb;
  // Small, slow light changes; no flashing or gameplay lighting changes.
  nebula*=.985+.015*sin(timer*.071+uv.x*3.0);
  color=mix(color,nebula,weight);
  rocks=RiftSample(rockmap,uv,true)*rockWeight;
 }
 // Exact shared TNT04A/B fire, sizes and rare dispersing groups, behind the rocks.
 color=WarComets(color,ray);
 color=color*(1.0-rocks.a)+rocks.rgb;
 mat.Base=vec4(color,1.0);mat.Normal=normalize(vWorldNormal.xyz);
}
