// Included source: c9622f048cd31400aaca488d30d60938ba6426789d2c345d7598b5c9d57ceb52
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
