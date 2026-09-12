// Included source: e87a2e8c96feec019f8cca4d5c6ec6920a0b36d4671877c8986abd5cb9c82b42
#include "shaders/organic/relief.glsl"
void SkyEdgeOriginal(inout Material mat){SetupOrganicMaterial(mat);}
#include "shaders/skyedges/ceiling_glow.glsl"

void SetupMaterial(inout Material mat)
{
 SkyEdgeOriginal(mat);
 float up=normalize(vWorldNormal.xyz).y;
 mat.Base.rgb*=1.0+0.12*max(up,0.0)-0.48*max(-up,0.0);
 SkyEdgeCeilingGlow(mat);
}
