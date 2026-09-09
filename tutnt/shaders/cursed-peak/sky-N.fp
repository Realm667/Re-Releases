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
void SetupMaterial(inout Material mat)
{
 vec3 state=floor(texture(statemap,vec2(.125,.5)).rgb*255.0+.5);
 vec3 clock=floor(texture(statemap,vec2(.375,.5)).rgb*255.0+.5);
 float progress=clamp((state.r*256.0+state.g)/65535.0,0.0,1.0);
 float phase=(clock.r*256.0+clock.g)/65535.0;
 vec3 fadeColor=texture(statemap,vec2(.75,.5)).rgb;
 float storm=state.b/255.0;
 float night=smoothstep(.40,1.0,progress);
 float dusk=smoothstep(.25,.58,progress)*(1.0-smoothstep(.64,.94,progress));
 float s=1.0-2.0*vTexCoord.x,t=1.0-2.0*vTexCoord.y;
 vec3 ray=normalize(vec3(s,t,-1.0));
 float latitude=asin(ray.y),longitude=atan(-ray.z,-ray.x)/6.283185307+.820;
 vec3 cloud=Clouds(vec2(longitude,clamp(.95-latitude/3.141592654*1.8,0.0,1.0)),phase);
 float overhead=smoothstep(.574,.906,ray.y);
 if(overhead>0.0)cloud=mix(cloud,Clouds(vec2(.5,.4)+ray.xz/max(ray.y,.4)*.28,phase),overhead);
 float gray=dot(cloud,vec3(.2126,.7152,.0722));
 cloud=mix(cloud,vec3(gray),.75);
 vec3 tint=mix(vec3(.94,.975,1.0),vec3(.92,.96,1.0),night);
 vec3 color=cloud*mix(.84,.34,night)*tint;
 float az=cos((longitude-.57)*6.283185307);
 float direction=pow(max(0.0,(az+1.0)*.5),6.0);
 float horizon=exp(-pow((latitude-.43)/.24,2.0));
 color+=dusk*(.25+.75*direction)*horizon*vec3(.18,.055,.075)*(0.4+gray);
 float silver=exp(-pow((latitude-.60)/.33,2.0))*direction;
 color+=silver*(1.0-storm*.65)*mix(vec3(.04,.04,.038),vec3(.03,.035,.043),night)*gray;
 float mv=.74-latitude/3.141592654*2.7;
 vec4 mountains=WrapLayer(mountainmap,vec2(longitude,mv),true);
 vec3 mountain=mountains.rgb*mix(.97,.43,night)*tint;
 mountain+=mountains.a*dusk*direction*vec3(.015,.006,.008);
 color=color*(1.0-mountains.a)+mountain;
 // Carry the outdoor sector fade farther up the distant mountain slopes.
 // The stronger low haze tapers out before the upper cloud ceiling.
 color=mix(color,fadeColor,.32*(1.0-smoothstep(0.0,.65,latitude)));
 // Low drifting veil erodes distant contrast during existing snowstorms.
 float veil=WrapLayer(cloudmap,vec2(longitude+phase*8.0,clamp(.60-latitude*.6,0.0,1.0)),false).r;
 float low=1.0-smoothstep(.18,.58,latitude);
 float cover=storm*.52*low*(.65+.35*veil);
 color=mix(color,fadeColor,cover);
 mat.Base=vec4(clamp(color,0.0,1.0),1.0);
 mat.Normal=normalize(vWorldNormal.xyz);
}
