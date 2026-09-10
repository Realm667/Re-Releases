// Included sources: d809ed23f6da03b21f213dad6e0c9ebbbc46bd2f8e01439f9b40d504de7ae2a6
#include "shaders/organic/relief.glsl"
#define ENV_ORIGINAL_BODY SetupOrganicMaterial(mat);
#define SetupMaterial OrganicEnvironment
#include "shaders/environment/surface.glsl"
#undef SetupMaterial
#undef ENV_ORIGINAL_BODY
void SetupMaterial(inout Material mat){OrganicEnvironment(mat);}
