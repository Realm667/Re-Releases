// Per-face material extension. Metadata uses map X,Y,Z coordinates.
float envHash(vec2 p) { return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
float envNoise(vec2 p) {
 vec2 i=floor(p),f=fract(p); f=f*f*(3.0-2.0*f);
 return mix(mix(envHash(i),envHash(i+vec2(1,0)),f.x),mix(envHash(i+vec2(0,1)),envHash(i+1.0),f.x),f.y);
}
float envData(int i) {
 vec3 b=floor(texelFetch(envMeta,ivec2(i,0),0).rgb*255.0+.5);
 return dot(b,vec3(65536.0,256.0,1.0));
}
// Canvas draw coordinates start at the top; raw GPU texelFetch starts at the bottom.
float envCell(int index) { return texelFetch(envState,ivec2(index%256,255-index/256),0).r; }
void SetupMaterial(inout Material mat) {
 ENV_ORIGINAL_BODY
 vec3 origin=vec3(envData(3),envData(4),envData(5))/16.0-65536.0;
 vec3 axis=vec3(envData(6),envData(7),envData(8))/32767.0-1.0;
 vec3 world=pixelpos.xzy,delta=world-origin;
 vec2 extent=vec2(envData(9),envData(10))/16.0;
 int kind=int(envData(11));
 vec2 uv=(kind==0?delta.xy:vec2(dot(delta,axis),delta.z))/max(extent,vec2(.001));
 if(any(lessThan(uv,vec2(-.002))) || any(greaterThan(uv,vec2(1.002))))return;
 ivec2 count=ivec2(envData(1),envData(2));
 ivec2 cell=clamp(ivec2(uv*vec2(count)),ivec2(0),count-1);
 int base=int(envData(0));
 vec2 grid=clamp(uv,0.0,1.0)*vec2(count)-.5;
 ivec2 lo=ivec2(floor(grid)),hi=lo+1;
 vec2 blend=fract(grid);blend=blend*blend*(3.0-2.0*blend);
 lo=clamp(lo,ivec2(0),count-1);hi=clamp(hi,ivec2(0),count-1);
 float amount=mix(mix(envCell(base+lo.x+lo.y*count.x),envCell(base+hi.x+lo.y*count.x),blend.x),mix(envCell(base+lo.x+hi.y*count.x),envCell(base+hi.x+hi.y*count.x),blend.x),blend.y);
 if(amount<.001)return;
 float time=timer*.01;
 if(envData(13)>.5) {
  float waterZ=envData(12)/16.0-65536.0;
  if(world.z>waterZ+(kind==0?.5:24.0))return;
  // Warped cellular ridges: world anchored, slow and continuous around corners.
  vec2 p=(kind==0?world.xy:vec2(dot(world,axis),world.z))*.055;
  p+=vec2(envNoise(p*.7+time*.15),envNoise(p*.6-time*.12))*1.4;
  vec2 cellId=floor(p);float first=9.0,second=9.0;
  {
   vec2 id=cellId+vec2(-1,-1);
   vec2 seed=vec2(envHash(id),envHash(id+37.2));
   vec2 q=id+.5+.3*sin(seed*6.283+time*.6)-p;
   float d=length(q);if(d<first){second=first;first=d;}else second=min(second,d);
  }
  {
   vec2 id=cellId+vec2(0,-1);
   vec2 seed=vec2(envHash(id),envHash(id+37.2));
   vec2 q=id+.5+.3*sin(seed*6.283+time*.6)-p;
   float d=length(q);if(d<first){second=first;first=d;}else second=min(second,d);
  }
  {
   vec2 id=cellId+vec2(1,-1);
   vec2 seed=vec2(envHash(id),envHash(id+37.2));
   vec2 q=id+.5+.3*sin(seed*6.283+time*.6)-p;
   float d=length(q);if(d<first){second=first;first=d;}else second=min(second,d);
  }
  {
   vec2 id=cellId+vec2(-1,0);
   vec2 seed=vec2(envHash(id),envHash(id+37.2));
   vec2 q=id+.5+.3*sin(seed*6.283+time*.6)-p;
   float d=length(q);if(d<first){second=first;first=d;}else second=min(second,d);
  }
  {
   vec2 id=cellId+vec2(0,0);
   vec2 seed=vec2(envHash(id),envHash(id+37.2));
   vec2 q=id+.5+.3*sin(seed*6.283+time*.6)-p;
   float d=length(q);if(d<first){second=first;first=d;}else second=min(second,d);
  }
  {
   vec2 id=cellId+vec2(1,0);
   vec2 seed=vec2(envHash(id),envHash(id+37.2));
   vec2 q=id+.5+.3*sin(seed*6.283+time*.6)-p;
   float d=length(q);if(d<first){second=first;first=d;}else second=min(second,d);
  }
  {
   vec2 id=cellId+vec2(-1,1);
   vec2 seed=vec2(envHash(id),envHash(id+37.2));
   vec2 q=id+.5+.3*sin(seed*6.283+time*.6)-p;
   float d=length(q);if(d<first){second=first;first=d;}else second=min(second,d);
  }
  {
   vec2 id=cellId+vec2(0,1);
   vec2 seed=vec2(envHash(id),envHash(id+37.2));
   vec2 q=id+.5+.3*sin(seed*6.283+time*.6)-p;
   float d=length(q);if(d<first){second=first;first=d;}else second=min(second,d);
  }
  {
   vec2 id=cellId+vec2(1,1);
   vec2 seed=vec2(envHash(id),envHash(id+37.2));
   vec2 q=id+.5+.3*sin(seed*6.283+time*.6)-p;
   float d=length(q);if(d<first){second=first;first=d;}else second=min(second,d);
  }
  float ridge=1.0-smoothstep(.025,.14,second-first);
  float depthFade=(1.0-smoothstep(96.0,384.0,waterZ-world.z))*(1.0-smoothstep(0.0,24.0,max(0.0,world.z-waterZ)));
  float skin=kind==0?1.0-.75*(1.0-smoothstep(.0,1.0,abs(waterZ-world.z))):1.0;
  mat.Base.rgb+=vec3(.19,.32,.30)*ridge*depthFade*amount*skin;
  return;
 }
 float metal=envData(14);
 vec3 n=normalize(mat.Normal),view=normalize(uCameraPos.xyz-pixelpos.xyz);
 vec2 p=(kind==0?world.xy:vec2(dot(world,axis),world.z));
 float patches=smoothstep(.25,.72,envNoise(p*.018)+envNoise(p*.073)*.22);
 vec3 bump=kind==0?vec3(sin(p.x*.13+time)*.035,0,sin(p.y*.11-time*.8)*.035):vec3(0,.025*sin(p.x*.1+time),0);
 vec3 wetNormal=normalize(mix(n,normalize(vWorldNormal.xyz),amount*(.55+.35*patches))+bump);
 vec3 reflection=reflect(-view,wetNormal);
 float fresnel=.16+.84*pow(1.0-abs(dot(wetNormal,view)),2.5);
 // Approximate overcast-sky reflection; not an image of nearby map objects.
 float clouds=.42+.58*envNoise(reflection.xz*3.5+vec2(time*.013,0));
 float sky=smoothstep(-.15,.4,reflection.y)*clouds;
 float sheen=(.07+.22*patches)*amount*fresnel;
 mat.Base.rgb*=1.0-amount*mix(.19,.10,metal);
 mat.Base.rgb+=vec3(.36,.49,.59)*(sky*.7+.3)*sheen*2.0;
 // Glow modulates lighting in UZDoom; reflected color must also enter the base.
 float coat=amount*(.20+.80*fresnel)*(.15+.85*patches);
 mat.Base.rgb+=vec3(.30,.39,.47)*coat;
 mat.Glow=vec4(1,1,1,amount*(.45+.55*patches)*.60);
 mat.Specular=mix(mat.Specular,vec3(.55+.25*metal),amount);
 mat.Glossiness=max(mat.Glossiness,12.0*amount);
 mat.SpecularLevel=max(mat.SpecularLevel,1.0*amount);
 mat.Normal=normalize(mix(n,wetNormal,amount));
}
