// Procedural sole, at native sprite resolution. No photo overlay or new geometry.
vec4 ProcessTexel()
{
 vec2 p=(floor(vTexCoord.st*vec2(32,64))+0.5)/vec2(32,64);
 vec2 q=(p-vec2(.50,.37))/vec2(.34,.31);
 float toe=1.0-smoothstep(.87,1.03,length(q));
 vec2 h=abs(p-vec2(.50,.80))/vec2(.27,.13);
 float heel=1.0-smoothstep(.88,1.03,max(h.x,h.y));
 float shape=max(toe,heel);
 float tread=step(.30,fract(p.y*12.0+p.x*.8))*.65+.35;
 tread*=mix(.5,1.0,step(.08,abs(p.x-.5)));
#ifdef SNOWPRINT
 float rim=smoothstep(.68,.87,length(q))*(1.0-smoothstep(.94,1.07,length(q)));
 return vec4(mix(vec3(.25,.29,.33),vec3(.68,.72,.75),rim),max(shape*tread*.65,rim*.30));
#else
 return vec4(.055,.068,.075,shape*tread*.62);
#endif
}
