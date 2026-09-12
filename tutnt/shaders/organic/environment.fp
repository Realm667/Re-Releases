// Included sources: c09be3fb04547f27a7e2bd66e45a2d2e503861312bdbefc83eaf35640bee1434
#include "shaders/organic/relief.glsl"
#define ENV_ORIGINAL_BODY SetupOrganicMaterial(mat);
#define SetupMaterial OrganicEnvironment
#include "shaders/environment/surface.glsl"
#undef SetupMaterial
#undef ENV_ORIGINAL_BODY
void SetupMaterial(inout Material mat){OrganicEnvironment(mat);}
