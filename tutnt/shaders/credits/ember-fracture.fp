// Stable screen-space footprints keep the fine glowing fissures from sparkling.
vec2 FractureDx,FractureDy;
vec4 RockData(sampler2D dataMap,vec2 uv,vec2 gx,vec2 gy);
void FractureProps(inout Material mat,vec2 uv)
{
    SetMaterialProps(mat,uv);
    mat.Base=desaturate(RockData(tex,uv,FractureDx,FractureDy));
#ifndef NO_LAYERS
    if((uTextureMode & TEXF_Brightmap)!=0)
        mat.Bright=desaturate(RockData(brighttexture,uv,FractureDx,FractureDy));
#endif
}
#define SetMaterialProps FractureProps
#include "shaders/organic/relief.glsl"
#undef SetMaterialProps
void SetupMaterial(inout Material mat)
{
    FractureDx=dFdx(vTexCoord.st);FractureDy=dFdy(vTexCoord.st);
    SetupOrganicMaterial(mat);
    // A round feather hides the tile edge; the old 64-unit gravel keeps its phase.
    float edge=1.0-smoothstep(.28,.49,length((pixelpos.xz-vec2(-4480.0,-448.0))/192.0));
    vec4 floorColor=texture(rockUnderlay,vTexCoord.st*3.0-vec2(71.5,-5.5));
    // Match the dark native floor while retaining the approved amber core colors.
    mat.Base.rgb*=mix(.58,1.0,mat.Bright.r);
    mat.Base=mix(floorColor,mat.Base,edge);
    mat.Bright.rgb*=edge;
    mat.Normal=normalize(mix(normalize(vWorldNormal.xyz),mat.Normal,edge));
}
