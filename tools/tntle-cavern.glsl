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
