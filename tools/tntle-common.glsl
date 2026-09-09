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
