vec4 AshKey(vec4 c,bool cloud)
{
 if(!cloud)
 {
  c.a=1.0-smoothstep(.03,.18,c.b-max(c.r,c.g));
  c.b=min(c.b,c.g);c.rgb*=c.a;
 }
 return c;
}
// Continuous world-ray projection across every face and every lightning state.
vec4 AshSample(sampler2D layer,vec2 uv,bool tileY)
{
 vec2 sz=vec2(textureSize(layer,0)),d=1.0/sz;
 vec2 p=uv*sz-.5,f=fract(p),b=(floor(p)+.5)/sz;
 vec2 lo=vec2(fract(b.x),tileY?fract(b.y):clamp(b.y,d.y*.5,1.0-d.y*.5));
 vec2 hi=vec2(fract(b.x+d.x),tileY?fract(b.y+d.y):clamp(b.y+d.y,d.y*.5,1.0-d.y*.5));
 return mix(mix(AshKey(texture(layer,lo),tileY),AshKey(texture(layer,vec2(hi.x,lo.y)),tileY),f.x),
            mix(AshKey(texture(layer,vec2(lo.x,hi.y)),tileY),AshKey(texture(layer,hi),tileY),f.x),f.y);
}
vec4 AshWrap(sampler2D layer,vec2 uv,bool tileY)
{
 uv=vec2(fract(uv.x),tileY?fract(uv.y):clamp(uv.y,0.0,1.0));
 float ex=.5*(1.0-smoothstep(0.0,.025,min(uv.x,1.0-uv.x)));
 vec4 a=AshSample(layer,uv,tileY);
 if(ex>0.0)a=mix(a,AshSample(layer,vec2(1.0-uv.x,uv.y),tileY),ex);
 if(tileY)
 {
  float ey=.5*(1.0-smoothstep(0.0,.025,min(uv.y,1.0-uv.y)));
  if(ey>0.0)
  {
   vec4 b=AshSample(layer,vec2(uv.x,1.0-uv.y),true);
   if(ex>0.0)b=mix(b,AshSample(layer,1.0-uv,true),ex);
   a=mix(a,b,ey);
  }
 }
 return a;
}
vec3 AshClouds(vec2 uv)
{
 return AshWrap(cloudmap,uv+vec2(timer*.00085,timer*.00020),true).rgb*.82
       +AshWrap(cloudmap,uv*.94+vec2(.13-timer*.00042,.07+timer*.00012),true).rgb*.18;
}
void SetupMaterial(inout Material mat)
{
 vec2 sz=vec2(textureSize(tex,0));
 float flash=clamp(floor((sz.x/sz.y-1.0)*768.0+.5),0.0,8.0)/8.0;
 float s=1.0-2.0*vTexCoord.x,t=1.0-2.0*vTexCoord.y;
 vec3 ray=normalize(@RAY@);
 float lat=asin(clamp(ray.y,-1.0,1.0));
 float turn=fract(atan(-ray.z,-ray.x)/6.283185307+.25);
 vec2 uv=vec2(fract(turn*2.0),clamp(.78-lat/3.141592654*1.8,0.0,1.0));
 float hemisphere=smoothstep(-.045,.045,sin(turn*6.283185307));
 vec4 landscape=hemisphere>0.0?AshWrap(panoramamap,uv,false):vec4(0.0);
 if(hemisphere<1.0)landscape=mix(AshWrap(reversemap,uv,false),landscape,hemisphere);
 // Separate moving sky from fixed mountains, including smoke and the actual skyline.
 vec3 clouds=AshClouds(vec2(turn*2.0,.8-lat/3.141592654*1.3));
 float overhead=smoothstep(.45,.85,ray.y);
 vec2 top=vec2(.5)+ray.xz/max(ray.y,.40)*.28;
 clouds=mix(clouds,AshClouds(top),overhead);
 vec3 color=clouds*.82;
 // Read-only synchronization to the original ACS lightning; no new weather timing.
 float transmission=smoothstep(.035,.28,dot(clouds,vec3(.2126,.7152,.0722)));
 float cone=exp((dot(ray,normalize(vec3(.35,.90,-.25)))-1.0)*5.0);
 color+=flash*flash*cone*transmission*vec3(.27,.25,.22);
 color=color*(1.0-landscape.a)+landscape.rgb*(.82+.12*flash);
 mat.Base=vec4(WarComets(color,ray),1.0);
 mat.Normal=normalize(vWorldNormal.xyz);
}
