// Shared canvas data carries the saved ACS clock; renderer timer is never used.
vec4 KeyMountain(vec4 c)
{
 float key=min(c.r,c.b)-c.g;
 c.a=1.0-smoothstep(.12,.40,key);
 // Remove magenta contamination before filtering at the silhouette.
 c.r=min(c.r,c.g+.035);c.b=min(c.b,c.g+.055);
 // Neutral base; reapply the restrained cold tint shared with sector fog.
 c.rgb=vec3(dot(c.rgb,vec3(.2126,.7152,.0722)));
 c.rgb*=c.a;return c;
}
vec4 SampleLayer(sampler2D layer,vec2 uv,bool key)
{
 vec2 size=vec2(textureSize(layer,0)),d=1.0/size;
 vec2 p=uv*size-.5,f=fract(p),b=(floor(p)+.5)/size;
 vec2 lo=vec2(fract(b.x),clamp(b.y,d.y*.5,1.0-d.y*.5));
 vec2 hi=vec2(fract(b.x+d.x),clamp(b.y+d.y,d.y*.5,1.0-d.y*.5));
 vec4 a=texture(layer,lo),c=texture(layer,vec2(hi.x,lo.y));
 vec4 e=texture(layer,vec2(lo.x,hi.y)),g=texture(layer,hi);
 if(key){a=KeyMountain(a);c=KeyMountain(c);e=KeyMountain(e);g=KeyMountain(g);}
 return mix(mix(a,c,f.x),mix(e,g,f.x),f.y);
}
vec4 WrapLayer(sampler2D layer,vec2 uv,bool key)
{
 uv=vec2(fract(uv.x),clamp(uv.y,0.0,1.0));
 vec4 c=SampleLayer(layer,uv,key);
 float edge=.5*(1.0-smoothstep(0.0,.025,min(uv.x,1.0-uv.x)));
 if(edge>0.0)c=mix(c,SampleLayer(layer,vec2(1.0-uv.x,uv.y),key),edge);
 return c;
}
vec3 Clouds(vec2 uv,float phase)
{
 vec3 a=WrapLayer(cloudmap,uv+vec2(phase*5.0,0.0),false).rgb;
 vec3 b=WrapLayer(cloudmap,vec2(uv.x+.11+phase*8.0,uv.y*.93+.03),false).rgb;
 return mix(a,b,.16);
}
// World south, independent of the artwork's longitude rotation.
float SunHeight(float progress) { return mix(.70,.52,smoothstep(.40,.86,progress)); }
float Sunset(float progress) { return smoothstep(.36,.53,progress)*(1.0-smoothstep(.79,.98,progress)); }
vec3 SunRay(float progress) { float a=SunHeight(progress);return vec3(0.0,sin(a),cos(a)); }
float SunTransmission(vec3 ray,float phase,float storm)
{
 float lat=asin(ray.y),lon=atan(-ray.z,-ray.x)/6.283185307+.820;
 vec3 cloud=Clouds(vec2(lon,clamp(.95-lat/3.141592654*1.8,0.0,1.0)),phase);
 float gray=dot(cloud,vec3(.2126,.7152,.0722));
 // A thin break in the cloud sheet; thick clouds and snowstorms obscure it.
 return smoothstep(.22,.76,gray)*(1.0-storm*.88);
}
vec3 SnowHash(vec2 p)
{
 vec3 q=fract(vec3(p.xyx)*vec3(.1031,.1030,.0973));
 q+=dot(q,q.yxz+33.33);return fract((q.xxy+q.yzz)*q.zyx);
}
float FarSnow(vec3 ray,float seconds,vec2 wind,float storm,float layer)
{
 float az=atan(-ray.z,-ray.x),lat=asin(ray.y);
 float columns=mix(220.0,360.0,layer),scale=columns/6.283185307;
 vec2 uv=vec2(az*scale,lat*scale);
 // Project the shared world wind onto the sky's horizontal tangent.
 uv.x-=dot(wind,vec2(-sin(az),cos(az)))*scale*mix(1.0,.6,layer);
 uv.y+=seconds*mix(.18,.12,layer);
 vec2 cell=floor(uv);cell.x=mod(cell.x,columns);cell.y=mod(cell.y,mix(900.0,600.0,layer));
 vec3 rnd=SnowHash(cell+layer*127.0);
 vec2 d=fract(uv)-(.2+.6*rnd.xy);
 d.x+=d.y*.25;
 // Ray derivatives remain continuous across the atan longitude seam.
 float radius=mix(.055,.11,rnd.z),aa=max(length(fwidth(ray))*scale*.45,.012);
 float flake=1.0-smoothstep(radius-aa,radius+aa,length(d*vec2(1.0,.72)));
 return flake*step(rnd.z,.13+storm*.23)*mix(.40,.26,layer);
}
void SetupMaterial(inout Material mat)
{
 vec3 state=floor(texture(statemap,vec2(.125,.5)).rgb*255.0+.5);
 vec3 clock=floor(texture(statemap,vec2(.375,.5)).rgb*255.0+.5);
 float progress=clamp((state.r*256.0+state.g)/65535.0,0.0,1.0);
 float phase=(clock.r*256.0+clock.g)/65535.0;
 vec3 fadeColor=texture(statemap,vec2(.625,.5)).rgb;
 float storm=state.b/255.0;
 float night=smoothstep(.40,1.0,progress);
 float dusk=Sunset(progress);
 float s=1.0-2.0*vTexCoord.x,t=1.0-2.0*vTexCoord.y;
 vec3 ray=normalize(vec3(1.0,t,s));
 float latitude=asin(ray.y),longitude=atan(-ray.z,-ray.x)/6.283185307+.820;
 vec3 cloud=Clouds(vec2(longitude,clamp(.95-latitude/3.141592654*1.8,0.0,1.0)),phase);
 float overhead=smoothstep(.574,.906,ray.y);
 if(overhead>0.0)cloud=mix(cloud,Clouds(vec2(.5,.4)+ray.xz/max(ray.y,.4)*.28,phase),overhead);
 float gray=dot(cloud,vec3(.2126,.7152,.0722));
 cloud=mix(cloud,vec3(gray),.75);
 vec3 tint=mix(vec3(.94,.975,1.0),vec3(.92,.96,1.0),night);
 vec3 color=cloud*mix(.84,.34,night)*tint;
 vec3 sun=SunRay(progress);
 float south=ray.z/max(length(ray.xz),.001);
 float direction=pow(max(0.0,south),10.0);
 float horizon=exp(-pow((latitude-SunHeight(progress))/.18,2.0));
 float weatherLight=1.0-storm*.78;
 color+=dusk*direction*horizon*vec3(.34,.145,.055)*(.4+gray)*weatherLight;
 float separation=acos(clamp(dot(ray,sun),-1.0,1.0));
 float transmission=SunTransmission(ray,phase,storm);
 float disc=1.0-smoothstep(.013,.023,separation);
 float halo=exp(-pow(separation/.07,2.0));
 color+=dusk*transmission*(disc*1.2+halo*.22)*vec3(1.0,.68,.32);
 float silver=exp(-pow((latitude-.60)/.33,2.0))*direction;
 color+=silver*(1.0-storm*.65)*mix(vec3(.04,.04,.038),vec3(.03,.035,.043),night)*gray;
 float mv=.74-latitude/3.141592654*2.7;
 vec4 mountains=WrapLayer(mountainmap,vec2(longitude,mv),true);
 vec3 mountain=mountains.rgb*mix(.97,.43,night)*tint;
 mountain+=mountains.a*dusk*direction*vec3(.035,.018,.007)*weatherLight;
 color=color*(1.0-mountains.a)+mountain;
 // Carry the outdoor sector fade farther up the distant mountain slopes.
 // The stronger low haze tapers out before the upper cloud ceiling.
 color=mix(color,fadeColor,.32*(1.0-smoothstep(0.0,.65,latitude)));
 // Low drifting veil erodes distant contrast during existing snowstorms.
 float veil=WrapLayer(cloudmap,vec2(longitude+phase*8.0,clamp(.60-latitude*.6,0.0,1.0)),false).r;
 float low=1.0-smoothstep(.18,.58,latitude);
 float cover=storm*.52*low*(.65+.35*veil);
 color=mix(color,fadeColor,cover);
 // Two miniature distant fields, clipped by the engine's sky stencil.
 // Dedicated columns avoid vertical canvas orientation differences.
 vec3 wx=floor(texture(statemap,vec2(.8125,.5)).rgb*255.0+.5);
 vec3 wy=floor(texture(statemap,vec2(.9375,.5)).rgb*255.0+.5);
 if(wx.b>0.0)
 {
  vec2 wind=(vec2(wx.r*256.0+wx.g,wy.r*256.0+wy.g)/65535.0-.5)*64.0;
  float snow=FarSnow(ray,phase*5000.0,wind,storm,0.0);
  if(wy.b>1.0)snow+=FarSnow(ray,phase*5000.0,wind,storm,1.0);
  snow*=1.0-smoothstep(.78,.97,abs(ray.y));
  color=mix(color,mix(vec3(.73,.77,.80),vec3(.39,.43,.49),night),clamp(snow,0.0,.65));
 }
 mat.Base=vec4(clamp(color,0.0,1.0),1.0);
 mat.Normal=normalize(vWorldNormal.xyz);
}
