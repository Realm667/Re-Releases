// Spherical sampling keeps cloud motion continuous across cube faces.
// Explicit interpolation also works with Doom's nearest-neighbour texture setting.
vec3 SkySample(vec2 uv)
{
 vec2 sz=vec2(textureSize(cloudmap,0));
 vec2 p=uv*sz-0.5, f=fract(p), b=(floor(p)+0.5)/sz;
 vec2 stepUV=1.0/sz;
 vec3 a=texture(cloudmap,vec2(fract(b.x),clamp(b.y,stepUV.y*0.5,1.0-stepUV.y*0.5))).rgb;
 vec3 c=texture(cloudmap,vec2(fract(b.x+stepUV.x),clamp(b.y,stepUV.y*0.5,1.0-stepUV.y*0.5))).rgb;
 vec3 d=texture(cloudmap,vec2(fract(b.x),clamp(b.y+stepUV.y,stepUV.y*0.5,1.0-stepUV.y*0.5))).rgb;
 vec3 e=texture(cloudmap,vec2(fract(b.x+stepUV.x),clamp(b.y+stepUV.y,stepUV.y*0.5,1.0-stepUV.y*0.5))).rgb;
 return mix(mix(a,c,f.x),mix(d,e,f.x),f.y);
}
void SetupMaterial(inout Material mat)
{
 float s=1.0-2.0*vTexCoord.x, t=1.0-2.0*vTexCoord.y;
 vec3 r=normalize(vec3(-s,t,1.0));
 vec2 uv=vec2(fract((atan(-r.z,-r.x)-4.712388980)/6.283185307+0.5),clamp(0.60-asin(r.y)/3.141592654*1.2,0.001,0.999));
 float high=smoothstep(0.65,0.85,r.y);
 float drift=sin(timer*0.008)*0.012*high;
 vec3 base=SkySample(vec2(fract(uv.x+drift),clamp(uv.y,0.001,0.999)));
 float edge=0.5*(1.0-smoothstep(0.0,0.035,min(uv.x,1.0-uv.x)));
 if(edge>0.0) base=mix(base,SkySample(vec2(fract(1.0-uv.x+drift),uv.y)),edge);
 vec3 veil=SkySample(vec2(fract(uv.x-drift*0.63+0.018),clamp(uv.y+0.012*high,0.001,0.999)));
 vec3 color=mix(base,veil,0.16*high);
 // Preserve dim valleys while keeping the canopy subordinate to the architecture.
 float canopy=smoothstep(0.15,0.55,r.y);
 mat.Base=vec4(color*mix(0.9,0.70,canopy)*(0.985+0.015*sin(timer*0.13)*high),1.0);
 mat.Normal=normalize(vWorldNormal.xyz);
}
