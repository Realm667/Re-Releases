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
