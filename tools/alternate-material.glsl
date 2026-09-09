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
 vec3 ray=normalize(@RAY@),color=RiftSurround(ray);
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
@ROCKS@
 rocks*=mix(1.0,smoothstep(.10,.16,length(uv-vec2(.5,.425))),weight);
 color=AlternateComet(color,ray);
 color=color*(1.0-rocks.a)+rocks.rgb;
 mat.Base=vec4(color,1.0);mat.Normal=normalize(vWorldNormal.xyz);
}
