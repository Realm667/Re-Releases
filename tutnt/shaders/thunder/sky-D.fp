// Same spherical/planar projection and engine clock in every pulse state.
vec4 MountainKey(vec4 c)
{
 c.a=1.0-smoothstep(.15,.35,c.b-max(c.r,c.g));
 c.b=min(c.b,max(c.r,c.g)+.08);c.rgb*=c.a;return c;
}
vec4 SampleLayer(sampler2D layer,vec2 uv,bool alphaLayer)
{
 vec2 size=vec2(textureSize(layer,0)),d=1.0/size;
 vec2 p=uv*size-.5,f=fract(p),b=(floor(p)+.5)/size;
 vec2 lo=vec2(fract(b.x),clamp(b.y,d.y*.5,1.0-d.y*.5));
 vec2 hi=vec2(fract(b.x+d.x),clamp(b.y+d.y,d.y*.5,1.0-d.y*.5));
 vec4 a=texture(layer,lo),c=texture(layer,vec2(hi.x,lo.y));
 vec4 e=texture(layer,vec2(lo.x,hi.y)),g=texture(layer,hi);
 if(alphaLayer){a=MountainKey(a);c=MountainKey(c);e=MountainKey(e);g=MountainKey(g);}
 return mix(mix(a,c,f.x),mix(e,g,f.x),f.y);
}
vec4 WrapLayer(sampler2D layer,vec2 uv,bool alphaLayer)
{
 uv=vec2(fract(uv.x),clamp(uv.y,0.0,1.0));
 vec4 c=SampleLayer(layer,uv,alphaLayer);
 float edge=.5*(1.0-smoothstep(0.0,.025,min(uv.x,1.0-uv.x)));
 if(edge>0.0)c=mix(c,SampleLayer(layer,vec2(1.0-uv.x,uv.y),alphaLayer),edge);
 return c;
}
vec3 Clouds(vec2 uv)
{
 vec3 a=WrapLayer(cloudmap,uv+vec2(timer*.00130,0.0),false).rgb;
 vec3 b=WrapLayer(cloudmap,vec2(uv.x+.09-timer*.00055,uv.y*.96+.02),false).rgb;
 return mix(a,b,.18);
}
void SetupMaterial(inout Material mat)
{
 // Encoded by the source texture's aspect ratio; invariant under HQ scaling.
 // All pulse states reuse this program instead of compiling 25 copies.
 vec2 sourceSize=vec2(textureSize(tex,0));
 float state=clamp(floor((sourceSize.x/sourceSize.y-1.0)*768.0+.5),0.0,24.0);
 float flashStrength=state<.5 ? 0.0 : (mod(state-1.0,8.0)+1.0)/8.0;
 flashStrength*=flashStrength;
 float flashDirection=state<.5 ? 0.0 : floor((state-1.0)/8.0);
 float s=1.0-2.0*vTexCoord.x,t=1.0-2.0*vTexCoord.y;
 vec3 ray=normalize(vec3(s,-1.0,-t));
 float latitude=asin(ray.y),longitude=atan(-ray.z,-ray.x)/6.283185307+.625;
 vec3 cloud=Clouds(vec2(longitude,clamp(.90-latitude/3.141592654*1.7,0.0,1.0)));
 float overhead=smoothstep(.574,.906,ray.y);
 if(overhead>0.0)cloud=mix(cloud,Clouds(vec2(.5,.40)+ray.xz/max(ray.y,.4)*.28),overhead);
 // Fixed world directions: both sides of every cube seam get the same pulse.
 float angle=3.85+flashDirection*2.094395102;
 vec3 flashDir=normalize(vec3(cos(angle),.80,sin(angle)));
 float cone=exp((dot(ray,flashDir)-1.0)*17.0);
 float fine=dot(cloud,vec3(.2126,.7152,.0722));
 float transmission=smoothstep(.045,.27,fine);
 // Neutralize the blue artwork before lighting, retaining fine cloud detail.
 cloud=mix(cloud,vec3(fine),.78)*vec3(1.0,1.0,.98);
 vec3 color=cloud*.34;
 // Cloud-dependent scattering keeps thick dark masses in front of the flash.
 color+=flashStrength*cone*(vec3(1.70,1.70,1.68)*transmission+cloud*.65);
 // A near discharge scatters beyond its core; distant steps barely lift it.
 color+=flashStrength*flashStrength*vec3(.14)*transmission;
 float mountainV=1.06-latitude/3.141592654*2.2;
 vec4 mountains=WrapLayer(mountainmap,vec2(longitude,mountainV),true);
 float ridge=WrapLayer(ridgemap,vec2(longitude,.5),false).r;
 // No bright fog at the silhouette: follow the actual crest in each column.
 float valleyFog=smoothstep(.035,.15,mountainV-ridge);
 mountains.rgb*=mix(.20,1.0,valleyFog);
 float mountainGray=dot(mountains.rgb,vec3(.2126,.7152,.0722));
 vec3 mountain=mix(mountains.rgb,vec3(mountainGray),.78)*vec3(1.0,1.0,.98)*(.30+flashStrength*.60);
 color=color*(1.0-mountains.a)+mountain;
 mat.Base=vec4(clamp(color,0.0,1.0),1.0);
 mat.Normal=normalize(vWorldNormal.xyz);
}
