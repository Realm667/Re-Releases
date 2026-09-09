// Generated materials use a single world-space projection per room. Adjacent
// surfaces therefore share exactly the same ray, including the zenith.
vec4 Bilinear(sampler2D src,vec2 uv)
{
 vec2 sz=vec2(textureSize(src,0)), p=uv*sz-.5, f=fract(p), b=(floor(p)+.5)/sz;
 vec2 lo=vec2(fract(b.x),clamp(b.y,.5/sz.y,1.-.5/sz.y));
 vec2 hi=vec2(fract(b.x+1./sz.x),clamp(b.y+1./sz.y,.5/sz.y,1.-.5/sz.y));
 return mix(mix(texture(src,lo),texture(src,vec2(hi.x,lo.y)),f.x),mix(texture(src,vec2(lo.x,hi.y)),texture(src,hi),f.x),f.y);
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
 vec3 r=normalize(pixelpos.xyz-vec3(-24576.,0.,24576.));
 float lat=asin(clamp(r.y,-1.,1.)),u=atan(r.z,r.x)/6.283185307+.625;
 vec2 uv=vec2(u,.60-lat/3.141592654*1.65);
 vec3 base=Wrap(panoramamap,uv).rgb;
 vec2 masks=Wrap(flowmask,uv).rg;
 float mask=masks.r;
 float seconds=SkyTime();
 // Positive latitude points upwards; image V points down. Negative time in
 // the vertical flow coordinate moves EVERY feature down the waterfall.
 vec2 flow=vec2(fract(u)*512.,uv.y*90.-seconds*.512);
 float a=Noise(flow*vec2(1.,1.));
 float b=Noise(vec2(flow.x*2.+13.,uv.y*170.-seconds*1.024));
 float ribbons=.45+1.1*smoothstep(.18,.82,a*.7+b*.3);
 // The mask is stationary: borders, ledges and occluding rock never move.
 vec3 color=base*(1.+mask*(ribbons-1.));
 // Very slow rising density variation only in smooth warm depth haze.
 // This does not displace the image or the occluding rock silhouettes.
 if(Quality()>1.)color*=1.+masks.g*.06*(Noise(vec2(fract(u)*128.,uv.y*22.+seconds*.064))-.5);
 float overhead=smoothstep(.64,.94,r.y);
 vec2 top=.5+r.xz/max(r.y,.4)*.36;
 color=mix(color,Bilinear(vaultmap,top).rgb,overhead);
 // Keep the approved dark basalt appearance without clipping the lava.
 color*=.62+mask*.14;
 mat.Base=vec4(color,1.);mat.Normal=normalize(vWorldNormal.xyz);
}
