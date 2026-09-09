// Generated materials use a single world-space projection per room. Adjacent
// surfaces therefore share exactly the same ray, including the zenith.
// Wrapped/quantized taps have discontinuous derivatives: pin the source LOD
// so filtering cannot introduce dark lines at longitude and texel boundaries.
vec4 Bilinear(sampler2D src,vec2 uv)
{
 vec2 sz=vec2(textureSize(src,0)), p=uv*sz-.5, f=fract(p), b=(floor(p)+.5)/sz;
 vec2 lo=vec2(fract(b.x),clamp(b.y,.5/sz.y,1.-.5/sz.y));
 vec2 hi=vec2(fract(b.x+1./sz.x),clamp(b.y+1./sz.y,.5/sz.y,1.-.5/sz.y));
 return mix(mix(textureLod(src,lo,0.),textureLod(src,vec2(hi.x,lo.y),0.),f.x),mix(textureLod(src,vec2(lo.x,hi.y),0.),textureLod(src,hi,0.),f.x),f.y);
}
vec4 Wrap(sampler2D src,vec2 uv)
{
 uv.x=fract(uv.x);
 float seam=.5*(1.-smoothstep(0.,.025,min(uv.x,1.-uv.x)));
 vec4 c=Bilinear(src,uv);
 if(seam>0.)c=mix(c,Bilinear(src,vec2(1.-uv.x,uv.y)),seam);
 return c;
}
float SkyTime()
{
 vec3 c=floor(texture(statemap,vec2(.25,.5)).rgb*255.+.5);
 return dot(c,vec3(65536.,256.,1.))/16777215.*2000.;
}
float Quality() { return floor(texture(statemap,vec2(.75,.5)).r*255.+.5); }
float Hash(vec2 p) { p=mod(p,128.);return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
float Noise(vec2 p)
{
 vec2 i=floor(p),f=fract(p),u=f*f*(3.-2.*f);
 return mix(mix(Hash(i),Hash(i+vec2(1,0)),u.x),mix(Hash(i+vec2(0,1)),Hash(i+vec2(1,1)),u.x),u.y);
}
void SetupMaterial(inout Material mat)
{
 vec3 r=normalize(pixelpos.xyz-vec3(-20480.,0.,24576.));
 float lat=asin(clamp(r.y,-1.,1.)),u=atan(r.z,r.x)/6.283185307+.625;
 float seconds=SkyTime(),v=.85-lat/3.141592654*1.7;
 vec3 a=Wrap(cloudmap,vec2(u+seconds*.001,v)).rgb;
 vec3 b=Wrap(cloudmap,vec2(u+.17-seconds*.0005,v*.88+.04)).rgb;
 vec3 color=mix(a,b,.20);
 float overhead=smoothstep(.57,.92,r.y);
 vec2 top=vec2(.5,.40)+r.xz/max(r.y,.4)*.28;
 vec3 topcolor=mix(Wrap(cloudmap,top+vec2(seconds*.001,0)).rgb,
  Wrap(cloudmap,top*.88+vec2(.17-seconds*.0005,.04)).rgb,.20);
 color=mix(color,topcolor,overhead)*.80;
 // Sparse embers on the sky sphere: no actors, no gameplay RNG, no HUD layer.
 if(Quality()>1. && lat>0.)
 {
  float sparks=0.;
  for(int i=0;i<16;i++)
  {
   float fi=float(i),p=fract(seconds*.02+fi*.618033989);
   float longitude=fi*2.39996323+.03*sin(p*6.283185307);
   float elevation=.08+p*1.05;
   vec3 d=vec3(cos(longitude)*cos(elevation),sin(elevation),sin(longitude)*cos(elevation));
   float q=length(r-d)/(.0013+fract(fi*.317)*.0008);
   sparks+=exp(-q*q*2.)*smoothstep(0.,.15,p)*(1.-smoothstep(.8,1.,p));
  }
  color+=vec3(.65,.23,.055)*sparks;
 }
 vec4 m=Wrap(mountainmap,vec2(u,.65-lat*.75));
 color=color*(1.-m.a)+m.rgb*.78;
 mat.Base=vec4(color,1.);mat.Normal=normalize(vWorldNormal.xyz);
}
