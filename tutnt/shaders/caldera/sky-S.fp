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
vec3 SkyWrap(vec2 uv)
{
 uv.x=fract(uv.x);
 vec3 c=SkySample(uv);
 float edge=0.5*(1.0-smoothstep(0.0,0.035,min(uv.x,1.0-uv.x)));
 if(edge>0.0)c=mix(c,SkySample(vec2(1.0-uv.x,uv.y)),edge);
 return c;
}
void SetupMaterial(inout Material mat)
{
 float s=1.0-2.0*vTexCoord.x, t=1.0-2.0*vTexCoord.y;
 vec3 r=normalize(vec3(-s,t,1.0));
 vec2 uv=vec2(fract((atan(-r.z,-r.x)-4.712388980)/6.283185307+0.5),clamp(0.60-asin(r.y)/3.141592654*1.2,0.001,0.999));
 float high=smoothstep(0.65,0.85,r.y);
 vec3 color=SkyWrap(uv);
 if(high>0.0)
 {
  // Polar projection creates a continuous, slowly rotating cloud wall.
  // Restrict sampling to cloud-only rows; mountains below 40 degrees stay fixed.
  float radius=acos(clamp(r.y,0.0,1.0));
  float cloudY=0.06+0.28*smoothstep(0.10,0.90,radius);
  float spin=timer*0.0024; // One circuit in about seven minutes.
  float spiral=radius*0.18;
  vec3 wall=SkyWrap(vec2(uv.x+spin+spiral,cloudY));
  vec3 veil=SkyWrap(vec2(uv.x+timer*0.00170+spiral*1.3+0.12,cloudY*0.88+0.025));
  float eyeRadius=radius+0.012*sin(uv.x*31.41592654+spin*6.283185307);
  float eye=smoothstep(0.07,0.27,eyeRadius);
  vec3 vortex=mix(vec3(0.035,0.009,0.007),mix(wall,veil,0.14),eye);
  color=mix(color,vortex,high);
 }
 // Preserve dim valleys while keeping the canopy subordinate to the architecture.
 float canopy=smoothstep(0.15,0.55,r.y);
 mat.Base=vec4(color*mix(0.9,0.70,canopy)*0.985,1.0);
 mat.Normal=normalize(vWorldNormal.xyz);
}
