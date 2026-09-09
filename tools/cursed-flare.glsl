// Generated with the same cloud sampling and sun path as the sky material.
@LAYERS@
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
