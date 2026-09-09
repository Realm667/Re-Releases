// Surface stays aligned with the physical cylindrical shield, independent of
// old ACS texture scrolling. The same original RUNE1..9 atlas as the seal.
vec4 ProcessTexel()
{
 vec2 d=vec2(pixelpos.x-128.0,pixelpos.z+320.0);
 float turn=(atan(d.y,d.x)+3.14159265)/6.2831853;
 float row=(pixelpos.y-3200.0)/280.0-timer*0.035;
 float col=turn*12.0;
 vec2 uv=vec2((fract(col)-0.5)*2.2+0.5,(fract(row)-0.5)*2.4+0.5);
 float ink=0.0;
 if(all(greaterThanEqual(uv,vec2(0)))&&all(lessThanEqual(uv,vec2(1))))
 {
  float index=mod(floor(col)+floor(row)*3.0,5.0)*2.0;
  vec4 rune=texture(runeAtlas,vec2((index+uv.x)/9.0,uv.y));
  ink=smoothstep(0.05,0.38,rune.r-max(rune.g,rune.b))*rune.a;
 }
 float contour=pow(max(0.0,cos(turn*6.2831853*6.0)),80.0)*0.08;
 float membrane=0.009+0.004*sin(row*6.2831853);
 float face=abs(dot(normalize(d),normalize(uCameraPos.xz-pixelpos.xz)));
 float silhouette=1.0-smoothstep(0.45,0.85,face);
 float brightness=membrane+ink*1.25*silhouette+contour;
 return vec4(vec3(1.0,0.30,0.025)*brightness,1.0);
}
