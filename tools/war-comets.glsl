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
