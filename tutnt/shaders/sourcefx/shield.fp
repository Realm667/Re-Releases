// Clean native teleporter ink at texel centres, then interpolate explicitly.
// This preserves QRUNT63's four silhouettes under nearest/trilinear filtering.
float RunePixel(vec2 pixel,float index)
{
 pixel=clamp(pixel,vec2(0.0),vec2(31.0));
 vec4 c=texture(runeAtlas,(pixel+vec2(0.5,index*32.0+0.5))/vec2(32.0,128.0));
 return step(0.04,c.r-max(c.g,c.b))*c.a;
}
float Rune(vec2 uv,float index)
{
 if(any(lessThan(uv,vec2(0.0)))||any(greaterThan(uv,vec2(1.0))))return 0.0;
 index=mod(index,4.0);
 vec2 p=uv*32.0-0.5,b=floor(p),f=fract(p);
 return mix(mix(RunePixel(b,index),RunePixel(b+vec2(1,0),index),f.x),
            mix(RunePixel(b+vec2(0,1),index),RunePixel(b+vec2(1,1),index),f.x),f.y);
}
// Surface stays aligned with the physical cylindrical shield, independent of
 // old ACS texture scrolling. The same QRUNT63 atlas as the teleporters.
vec4 SourceShieldColor()
{
 vec3 ray=normalize(pixelpos.xyz-uCameraPos.xyz);
 vec2 q=uCameraPos.xz-vec2(128.0,-384.0);
 float a=dot(ray.xz,ray.xz),b=dot(q,ray.xz);
 float disc=b*b-a*(dot(q,q)-455.0*455.0);
 if(disc<=0.0 || a<0.00001)return vec4(0.0);
 float side=dot(pixelpos.xz-vec2(128.0,-384.0),ray.xz)<0.0?-1.0:1.0;
 float t=(-b+side*sqrt(disc))/a;
 if(t<0.0)return vec4(0.0);
 vec3 surface=uCameraPos.xyz+ray*t;
 vec2 d=surface.xz-vec2(128.0,-384.0);
 float turn=(atan(d.y,d.x)+3.14159265)/6.2831853;
 float row=(surface.y-3200.0)/280.0-timer*0.035;
 float col=turn*12.0;
 vec2 uv=vec2((fract(col)-0.5)*2.2+0.5,(fract(row)-0.5)*2.4+0.5);
 float ink=0.0;
 if(all(greaterThanEqual(uv,vec2(0)))&&all(lessThanEqual(uv,vec2(1))))
 {
  float index=mod(floor(col)+floor(row)*3.0,4.0);
  ink=Rune(uv,index);
 }
 float face=abs(dot(normalize(d),normalize(ray.xz)));
 float silhouette=pow(1.0-face,0.6);
 float flow=0.5+0.5*sin(turn*120.0+sin(row*3.0));
 float membrane=(0.035+0.055*silhouette)*(0.8+0.2*flow);
 float contour=pow(silhouette,9.0)*0.50;
 float brightness=membrane+ink*1.65*(0.02+0.98*pow(silhouette,1.8))+contour;
 return vec4(vec3(1.0,0.30,0.025)*brightness,1.0);
}
void SetupMaterial(inout Material mat)
{
 mat.Base=SourceShieldColor();
 mat.Bright=vec4(1.0);
}
