// Shared distant-comet style for TNT04A; reserved for TNT04B's approved sky.
// Pure decoration: no gameplay actors, damage, sound or random state.
vec3 WarCometLight(float lon, float lat, float headLon, float headLat, float size, float seed)
{
 // Wrap before scaling, including detached fragments across cube seams.
 float dx=(mod(lon-headLon+3.141592654,6.283185307)-3.141592654)/size;
 float along=(lat-headLat)/size;
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
 return fire*flame*ember+vec3(3.2,2.25,0.9)*head+vec3(0.30,0.035,0.003)*halo;
}

vec3 WarComets(vec3 color, vec3 ray)
{
 float lon=atan(-ray.z,-ray.x), lat=asin(clamp(ray.y,-1.0,1.0));
 for(int i=0;i<7;i++)
 {
  float seed=float(i), period=32.0+seed*2.7;
  float flight=(timer+seed*7.31)/period;
  float cycle=floor(flight), phase=fract(flight);
  float life=smoothstep(0.0,0.06,phase)*(1.0-smoothstep(0.70,0.86,phase));
  float headLat=1.02-phase*1.28;
  float headLon=seed*0.8976+0.28-phase*0.43;
  // Constant throughout a flight, changing only while the head is invisible.
  float size=mix(0.72,1.34,mod(cycle*17.0+seed*11.0,29.0)/28.0);
  // Exactly one flight in 32 per track, staggered between tracks and blocks.
  bool group=mod(cycle*13.0+seed*7.0+floor(cycle/32.0)*11.0+19.0,32.0)<0.5;
  float split=group?smoothstep(0.32,0.65,phase):0.0;
  color+=life*(1.0-0.18*split)*WarCometLight(lon,lat,headLon,headLat,size,seed);
  if(group && phase>0.32 && life>0.0)
  {
   // Two small pieces gently fan out; no extra main tracks or sudden flash.
   float appear=smoothstep(0.32,0.42,phase);
   color+=life*appear*0.65*WarCometLight(lon,lat,headLon+0.038*split,headLat+0.018*split,size*0.52,seed+11.0);
   color+=life*appear*0.55*WarCometLight(lon,lat,headLon-0.030*split,headLat-0.014*split,size*0.40,seed+23.0);
  }
 }
 return color;
}

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
 vec3 ray=normalize(vec3(-1.0,t,-s));
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
