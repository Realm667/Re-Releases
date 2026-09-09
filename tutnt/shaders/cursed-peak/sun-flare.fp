// Generated with the same cloud sampling and sun path as the sky material.
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

float VisibleSun(vec3 ray)
{
 float lon=atan(-ray.z,-ray.x)/6.283185307+.820;
 float lat=asin(ray.y);
 float ridge=WrapLayer(mountainmap,vec2(lon,.74-lat/3.141592654*2.7),true).a;
 return (1.0-ridge)*SunTransmission(ray,phase,storm);
}
void main()
{
 vec2 uv=TexCoord;
 vec3 color=texture(InputTexture,uv).rgb;
 vec3 sun=SunRay(progress),up=normalize(vec3(0.0,sun.z,-sun.y));
 // Average the tiny disc, so a ridge clips the glare with the visible sun.
 float visible=VisibleSun(sun);
 visible+=VisibleSun(normalize(sun+vec3(.012,0.0,0.0)));
 visible+=VisibleSun(normalize(sun-vec3(.012,0.0,0.0)));
 visible+=VisibleSun(normalize(sun+up*.012));
 visible+=VisibleSun(normalize(sun-up*.012));
 float strength=amount*visible*.2;
 float aspect=float(textureSize(InputTexture,0).x)/float(textureSize(InputTexture,0).y);
 vec2 metric=vec2(aspect,1.0),d=(uv-focus)*metric;
 float glow=exp(-dot(d,d)/.026);
 float streak=exp(-abs(d.x)*9.0-abs(d.y)*150.0);
 vec2 axis=vec2(.5)-focus;
 float ghosts=0.0;
 for(int i=0;i<3;i++)
 {
  vec2 delta=(uv-(focus+axis*(1.35+float(i)*.65)))*metric;
  float radius=.028+float(i)*.016;
  ghosts+=exp(-pow((length(delta)-radius)/.009,2.0))*.025;
 }
 // A restrained warm veiling glare; no whiteout, camera shake or flashing.
 color+=strength*(vec3(1.0,.71,.38)*(glow*.22+streak*.09+ghosts)+vec3(.015,.011,.006));
 FragColor=vec4(color,1.0);
}
