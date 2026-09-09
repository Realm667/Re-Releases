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

// Dark cloud ceiling anchored to the real TNT04CN beam endpoint.
// The beam itself is level geometry; no beam is drawn by this material.
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
 vec3 color=RiftWrap(vec2(lon/6.283185307+.5+timer*.000035,.60-lat/3.141592654*.90));
 float cap=smoothstep(.55,.85,ray.y);
 color=mix(color,RiftWrap(vec2(.5+ray.x*.25,.25+ray.z*.25)),cap);
 return color*.85*smoothstep(-.30,.35,ray.y);
}
vec4 RiftRockLayer(vec4 behind,sampler2D layer,vec3 ray,vec3 cameraOffset,vec3 forward,vec3 right,vec3 up,
                   vec2 span,vec4 bounds,float light,float motion,float phase,float distance,float period)
{
 float depth=dot(ray,forward);
 float plane=distance-dot(cameraOffset,forward);
 if(depth<=.01 || plane<=0.0)return behind;
 // Intersect a fixed world-space card, giving nearby debris stronger parallax.
 vec3 hit=cameraOffset+ray*(plane/depth);
 vec2 p=vec2(dot(hit,right),-dot(hit,up))/(distance*span);
 // A true closed ellipse: quadrature at one frequency, opposite signed periods.
 float theta=timer*(6.283185307/period)+phase;
 p+=motion*vec2(-cos(theta),.65*sin(theta));
 float angle=.004*sin(timer*.023+phase),c=cos(angle),s=sin(angle);
 vec2 uv=vec2(c*p.x-s*p.y,s*p.x+c*p.y)+.5;
 float edge=min(min(uv.x,1.0-uv.x),min(uv.y,1.0-uv.y));
 if(edge<=0.0)return behind;
 vec4 rock=RiftSample(layer,mix(bounds.xy,bounds.zw,uv),true)*smoothstep(0.0,.025,edge);
 float luma=dot(rock.rgb,vec3(.2126,.7152,.0722));
 rock.rgb=vec3(luma)*vec3(1.02,1.0,.97)*light*smoothstep(-.25,.30,ray.y);
 return behind*(1.0-rock.a)+rock;
}
// TNT04C: single sparse comet, using the unchanged shared flame profile.
vec3 AlternateComet(vec3 color,vec3 ray)
{
 float flight=timer/65.0,cycle=floor(flight),phase=fract(flight);
 float life=smoothstep(0.0,.05,phase)*(1.0-smoothstep(.46,.55,phase));
 float lon=atan(-ray.z,-ray.x),lat=asin(clamp(ray.y,-1.0,1.0));
 float size=mix(.72,1.10,mod(cycle*17.0,29.0)/28.0);
 return color+life*WarCometLight(lon,lat,mod(cycle*2.39996+.28,6.283185307)-phase*.30,1.0-phase*1.15,size,cycle);
}
float AlternateViewCoord(float u)
{
 vec3 b=floor(textureLod(viewmap,vec2(u,.5),0.0).rgb*255.0+.5);
 return dot(b,vec3(65536.0,256.0,1.0))/16777215.0*65536.0-32768.0;
}
void SetupMaterial(inout Material mat)
{
 float s=1.0-2.0*vTexCoord.x,t=1.0-2.0*vTexCoord.y;
 vec3 ray=normalize(vec3(s,1.0,-t)),color=RiftSurround(ray);
 // Renderer coordinates are world X/Z/Y. The first three height sections
 // view a miniature beam at (6464,704,2848); the final arena uses tag 88's
 // full-size beam at (962,13570,-992). Never mix these coordinate systems.
 vec3 eye=uCameraPos.xyz;
 bool room=eye.x>5120.0 && eye.x<7808.0 && eye.z>-1664.0 && eye.z<1536.0;
 vec3 beam=room?vec3(6464.0,2848.0,704.0):vec3(962.0,-992.0,13570.0);
 float span=room?4200.0:8000.0;
 float distanceToCeiling=(beam.y-eye.y)/max(ray.y,.001);
 vec2 point=eye.xz-ray.xz*distanceToCeiling;
 vec2 uv=vec2(.5,.425)+(point-beam.xz)/span;
 float edge=min(min(uv.x,1.0-uv.x),min(uv.y,1.0-uv.y));
 float weight=smoothstep(0.0,.13,edge)*smoothstep(.015,.10,ray.y)*step(0.0,distanceToCeiling);
 if(weight>0.0)
 {
  float moving=smoothstep(.10,.20,length(uv-vec2(.5,.425)));
  vec2 drift=.001*moving*vec2(sin(timer*.014+uv.y*7.0),sin(timer*.011+uv.x*8.0));
  color=mix(color,RiftSample(nebulamap,uv+drift,false).rgb,weight);
 }
 vec4 rocks=vec4(0.0);
 vec3 cardEye=eye;
 if(room)
 {
  cardEye=vec3(962.0,-5350.0,13570.0);
  if(textureLod(viewmap,vec2(.875,.5),0.0).r>.5)
   cardEye=vec3(AlternateViewCoord(.125),AlternateViewCoord(.375),AlternateViewCoord(.625));
 }
 vec3 rockEye=vec3(-cardEye.x,cardEye.y,-cardEye.z)-vec3(-962.0,-5350.0,-13570.0);
 rocks=RiftRockLayer(rocks,rockmap,ray,rockEye,vec3(-0.844817763,0.484809620,-0.226368237),vec3(-0.258819045,0.000000000,0.965925826),vec3(0.468290133,0.874619707,0.125477963),vec2(0.250000000,0.320000000),vec4(0.925000000,0.430000000,0.770000000,0.746000000),0.85,0.006,4.1,100000.0,-270.0);
 rocks=RiftRockLayer(rocks,rockmap,ray,rockEye,vec3(0.532895080,0.559192903,-0.635079626),vec3(-0.766044443,0.000000000,-0.642787610),vec3(-0.359442270,0.829037573,0.428366616),vec2(0.400000000,0.500000000),vec4(0.770000000,0.430000000,0.925000000,0.746000000),1.0,0.007,1.3,70000.0,240.0);
 rocks=RiftRockLayer(rocks,platformmap,ray,rockEye,vec3(0.827960033,0.515038075,-0.221851222),vec3(-0.258819045,0.000000000,-0.965925826),vec3(-0.497488578,0.857167301,0.133301663),vec2(0.200000000,0.200000000),vec4(0.500000000,0.000000000,1.000000000,1.000000000),0.7,0.005,4.8,65000.0,280.0);
 rocks=RiftRockLayer(rocks,rockmap,ray,rockEye,vec3(-0.309975519,0.422618262,0.851650740),vec3(0.939692621,0.000000000,0.342020143),vec3(0.144543958,0.906307787,-0.397131262),vec2(0.180000000,0.210000000),vec4(0.245000000,0.270000000,0.420000000,0.540000000),0.72,0.007,3.1,55000.0,230.0);
 rocks=RiftRockLayer(rocks,platformmap,ray,rockEye,vec3(-0.386080993,0.406736643,-0.827953362),vec3(-0.906307787,0.000000000,0.422618262),vec3(0.171894333,0.913545458,0.368628587),vec2(0.380000000,0.380000000),vec4(0.000000000,0.000000000,0.500000000,1.000000000),0.82,0.006,2.2,36000.0,-220.0);
 rocks*=mix(1.0,smoothstep(.10,.16,length(uv-vec2(.5,.425))),weight);
 color=AlternateComet(color,ray);
 color=color*(1.0-rocks.a)+rocks.rgb;
 mat.Base=vec4(color,1.0);mat.Normal=normalize(vWorldNormal.xyz);
}
