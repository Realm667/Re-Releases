// Included sources: de44e34146b9a47d2f6b3b897a4c3b20d39fd3448af69c6d83967ee927aec63c
#include "shaders/organic/relief.glsl"
#define ENV_ORIGINAL_BODY SetupOrganicMaterial(mat);
#define SetupMaterial OrganicEnvironment
#include "shaders/environment/surface.glsl"
#undef SetupMaterial
#undef ENV_ORIGINAL_BODY
void SetupMaterial(inout Material mat){OrganicEnvironment(mat);}
