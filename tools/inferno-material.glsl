// TNT04B's authored fire room. One world direction spans every wall and cap.
// Explicit bilinear filtering keeps the sky smooth with nearest-filtered sprites.
vec3 InfernoLinear(sampler2D tex,vec2 uv)
{
 vec2 size=vec2(textureSize(tex,0));vec2 q=uv*size-.5;
 vec2 f=fract(q);vec2 a=(floor(q)+.5)/size;vec2 d=1./size;
 return mix(mix(textureLod(tex,a,0.).rgb,textureLod(tex,a+vec2(d.x,0),0.).rgb,f.x),
            mix(textureLod(tex,a+vec2(0,d.y),0.).rgb,textureLod(tex,a+d,0.).rgb,f.x),f.y);
}
vec3 InfernoSample(sampler2D tex,vec2 uv,bool repeatV)
{
 uv.x=fract(uv.x);uv.y=repeatV?fract(uv.y):clamp(uv.y,.001,.999);
 float sx=.5*(1.-smoothstep(0.,.035,min(uv.x,1.-uv.x)));
 vec3 a=mix(InfernoLinear(tex,uv),InfernoLinear(tex,vec2(1.-uv.x,uv.y)),sx);
 if(repeatV){float sy=.5*(1.-smoothstep(0.,.035,min(uv.y,1.-uv.y)));vec3 b=mix(InfernoLinear(tex,vec2(uv.x,1.-uv.y)),InfernoLinear(tex,1.-uv),sx);a=mix(a,b,sy);}
 return a;
}
void SetupMaterial(inout Material mat)
{
 vec3 ray=normalize(pixelpos.xyz-uCameraPos.xyz);
 float lon=atan(ray.z,ray.x)/6.283185307+.5;
 float lat=asin(clamp(ray.y,-1.,1.));
 vec2 uv=vec2(lon,.54-lat/3.141592654*1.4);
 // Only fire above the distant cliffs drifts. Rock silhouettes stay anchored.
 float fire=1.-smoothstep(.30,.54,uv.y);
 vec2 drift=vec2(sin(timer*.052+lon*25.132741229)*.002,cos(timer*.039+lon*18.849555922)*.003)*fire;
 vec3 color=InfernoSample(panoramamap,uv+drift,false);
 vec2 top=.5+ray.xz/max(ray.y,.35)*.26;
 vec2 wind=vec2(timer*.00065,-timer*.00034);
 vec3 clouds=InfernoSample(cloudmap,top+wind,true);
 color=mix(color,clouds,smoothstep(.30,.75,ray.y));
 vec2 bottom=.5+ray.xz/max(-ray.y,.30)*.24;
 vec3 lava=InfernoSample(magmamap,bottom,true);
 float hot=smoothstep(.28,.82,lava.r-lava.b);
 lava*=1.+hot*.035*sin(timer*.6+bottom.x*19.+bottom.y*23.);
 color=mix(color,lava,smoothstep(.34,.84,-ray.y));
 // Slow brightness changes remain local to luminous flame details.
 color*=.91+.018*sin(timer*.31+ray.x*9.+ray.z*7.)*smoothstep(.45,.9,color.r);
 // Sky-only full brightness avoids directional wall contrast at cube edges.
 mat.Bright=vec4(1.);
 mat.Base=vec4(color,1.);mat.Normal=normalize(vWorldNormal.xyz);
}
