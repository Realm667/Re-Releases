#include "shaders/organic/relief.glsl"
#define ENV_ORIGINAL_BODY SetupOrganicMaterial(mat);
#define SetupMaterial OrganicEnvironment
#include "shaders/environment/surface.glsl"
#undef SetupMaterial
#undef ENV_ORIGINAL_BODY
void SetupMaterial(inout Material mat){OrganicEnvironment(mat);}
