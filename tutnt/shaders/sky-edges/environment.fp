// Included sources: c09be3fb04547f27a7e2bd66e45a2d2e503861312bdbefc83eaf35640bee1434
#include "shaders/organic/relief.glsl"
#define ENV_ORIGINAL_BODY SetupOrganicMaterial(mat);
#define SetupMaterial OrganicEnvironment
#include "shaders/environment/surface.glsl"
#undef SetupMaterial
#undef ENV_ORIGINAL_BODY
void SkyEdgeOriginal(inout Material mat){OrganicEnvironment(mat);}
#include "shaders/skyedges/ceiling_glow.glsl"

void SetupMaterial(inout Material mat)
{
 SkyEdgeOriginal(mat);
 float up=normalize(vWorldNormal.xyz).y;
 mat.Base.rgb*=1.0+0.12*max(up,0.0)-0.48*max(-up,0.0);
 SkyEdgeCeilingGlow(mat);
}
