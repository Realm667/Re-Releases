// Stable screen-space footprints keep the fine glowing fissures from sparkling.
vec2 FractureDx,FractureDy;
// OpenGL may allocate only mip 0 for unfiltered color/brightmap textures.
// Sample valid base-level texels and integrate four points across the pixel footprint.
vec4 FractureBilinear(sampler2D dataMap,vec2 uv)
{
    ivec2 size=textureSize(dataMap,0);
    vec2 p=uv*vec2(size)-.5;ivec2 a=ivec2(floor(p));vec2 f=fract(p);
    ivec2 q=((a%size)+size)%size,r=(q+ivec2(1))%size;
    return mix(mix(texelFetch(dataMap,q,0),texelFetch(dataMap,ivec2(r.x,q.y),0),f.x),
               mix(texelFetch(dataMap,ivec2(q.x,r.y),0),texelFetch(dataMap,r,0),f.x),f.y);
}
vec4 FractureColor(sampler2D dataMap,vec2 uv)
{
    vec2 a=(FractureDx+FractureDy)*.30,b=(FractureDx-FractureDy)*.30;
    return .25*(FractureBilinear(dataMap,uv+a)+FractureBilinear(dataMap,uv-a)+
                FractureBilinear(dataMap,uv+b)+FractureBilinear(dataMap,uv-b));
}
void FractureProps(inout Material mat,vec2 uv)
{
    SetMaterialProps(mat,uv);
    mat.Base=desaturate(FractureColor(tex,uv));
#ifndef NO_LAYERS
    if((uTextureMode & TEXF_Brightmap)!=0)
        mat.Bright=desaturate(FractureColor(brighttexture,uv));
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
