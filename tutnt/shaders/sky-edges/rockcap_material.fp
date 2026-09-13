// Included source: e87a2e8c96feec019f8cca4d5c6ec6920a0b36d4671877c8986abd5cb9c82b42
#include "shaders/organic/relief.glsl"
void SkyEdgeOriginal(inout Material mat){SetupOrganicMaterial(mat);}
#include "shaders/skyedges/ceiling_glow.glsl"

float SkyEdgeBlendValue(int i) { return (SkyGlowNumber(texelFetch(skyEdgeBlend,ivec2(i,0),0).rgb)-8388608.0)/256.0; }
void SetupMaterial(inout Material mat)
{
 SkyEdgeOriginal(mat);
 float up=normalize(vWorldNormal.xyz).y;
 mat.Base.rgb*=1.0-0.12*max(-up,0.0);
 SkyEdgeCeilingGlow(mat);
 vec2 n=vec2(SkyEdgeBlendValue(0),SkyEdgeBlendValue(1))/4096.0;
 float d=dot(pixelpos.xz,n)+SkyEdgeBlendValue(2)-pixelpos.y;
 float lo=SkyEdgeBlendValue(3),hi=SkyEdgeBlendValue(4),fade=SkyEdgeBlendValue(5);
 mat.Base.a*=1.0-smoothstep(lo,hi,d);
}
