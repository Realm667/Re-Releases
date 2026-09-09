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
