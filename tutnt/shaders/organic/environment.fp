// Included sources: 69fdbb6063c28649e07a27e1141a3a909f9fa6ace8df0e7422feeb9808b56d98
#include "shaders/organic/relief.glsl"
#define ENV_ORIGINAL_BODY SetupOrganicMaterial(mat);
#define SetupMaterial OrganicEnvironment
#include "shaders/environment/surface.glsl"
#undef SetupMaterial
#undef ENV_ORIGINAL_BODY
void SetupMaterial(inout Material mat){OrganicEnvironment(mat);}
