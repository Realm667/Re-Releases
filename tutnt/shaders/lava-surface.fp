// Per-fragment visibility, shared by material setup and final lighting.
float LavaFarVisibility;

// Three world-space layers: crust, flowing channels, and an incandescent bed.
// Renderer coordinates are (Doom X, Doom Z, Doom Y). No map changes are needed.
float LavaHash(vec2 p)
{
    vec3 q=fract(vec3(p.xyx)*0.1031);
    q+=dot(q,q.yzx+33.33);
    return fract((q.x+q.y)*q.z);
}
float LavaNoise(vec2 p)
{
    vec2 i=floor(p),f=fract(p),u=f*f*(3.0-2.0*f);
    return mix(mix(LavaHash(i),LavaHash(i+vec2(1,0)),u.x),
               mix(LavaHash(i+vec2(0,1)),LavaHash(i+vec2(1,1)),u.x),u.y);
}
float LavaPeak(vec3 c) { return max(c.r,max(c.g,c.b)); }
vec4 LavaSmooth(vec2 uv)
{
    vec2 size=vec2(textureSize(tex,0));
    vec2 p=uv*size-0.5,f=fract(p),base=(floor(p)+0.5)/size;
    return mix(mix(getTexel(base),getTexel(base+vec2(1,0)/size),f.x),
               mix(getTexel(base+vec2(0,1)/size),getTexel(base+vec2(1,1)/size),f.x),f.y);
}
// The reference-derived height asset drives cap color, shape, normals and
// ray intersection together. Broad coverage leaves entire stretches molten.
float LavaCrustHeightTexel(vec2 uv)
{
    // Filter the height field explicitly: nearest-filtered high-frequency
    // grains would make the ray skip ridges and create pinhole speckle.
    vec2 size=vec2(textureSize(crustHeight,0))/4.0;
    vec2 q=uv*size-0.5,f=fract(q),b=(floor(q)+0.5)/size;
    return mix(mix(textureLod(crustHeight,b,0.0).r,textureLod(crustHeight,b+vec2(1,0)/size,0.0).r,f.x),
               mix(textureLod(crustHeight,b+vec2(0,1)/size,0.0).r,textureLod(crustHeight,b+vec2(1,1)/size,0.0).r,f.x),f.y);
}
vec3 LavaCrustField(vec2 p, vec2 dx, vec2 dy)
{
    vec2 warped=p+(vec2(LavaNoise(p/173.0+7.8),LavaNoise(p/173.0+31.7))-0.5)*112.0;
    vec2 cell=floor(warped/384.0),uv=fract(warped/384.0);
    float seed=LavaHash(cell+vec2(71.3,29.8));
    if(seed>0.5) { uv=uv.yx; dx=dx.yx; dy=dy.yx; }
    if(fract(seed*7.1)>0.5) { uv.x=1.0-uv.x; dx.x=-dx.x; dy.x=-dy.x; }
    // Fade incomplete border plates before atlas boundaries, avoiding seams.
    vec2 border=min(uv,1.0-uv);
    float edge=smoothstep(0.0,0.035,min(border.x,border.y));
    float regional=LavaNoise(p/410.0+vec2(18.2,6.7))*0.75
                  +LavaNoise(p/157.0+vec2(3.4,27.9))*0.25;
    float groups=smoothstep(0.49,0.70,regional);
    float raw=LavaCrustHeightTexel(uv);
    float cover=smoothstep(0.045,0.11,raw)*smoothstep(0.22,0.55,groups)*edge;
    return vec3(raw,cover,cover*(6.0+raw*5.0));
}

// Trace the visible upper surface instead of shifting a flat decal. Fixed
// iteration counts and explicit texture gradients keep GL/Vulkan sampling safe.
vec3 LavaCrustHit(vec2 base,vec2 slope,vec2 dx,vec2 dy)
{
    const float ceiling=18.0;
    float above=ceiling,below=0.0;
    for(int i=1;i<=32;i++)
    {
        float z=ceiling*(1.0-float(i)/32.0);
        vec2 p=base-slope*z;
        float h=LavaCrustField(p,dx,dy).z;
        if(z<=h) { below=z; above=z+ceiling/32.0; break; }
    }
    for(int i=0;i<5;i++)
    {
        float z=(above+below)*0.5;
        if(z>LavaCrustField(base-slope*z,dx,dy).z) above=z;
        else below=z;
    }
    float z=(above+below)*0.5;
    return vec3(base-slope*z,z);
}

vec3 LavaCrustNormal(vec2 p,vec2 dx,vec2 dy)
{
    float stepSize=max(0.65,min(3.0,max(length(dx),length(dy))));
    float hx=LavaCrustField(p+vec2(stepSize,0),dx,dy).z-LavaCrustField(p-vec2(stepSize,0),dx,dy).z;
    float hz=LavaCrustField(p+vec2(0,stepSize),dx,dy).z-LavaCrustField(p-vec2(0,stepSize),dx,dy).z;
    vec3 n=normalize(vWorldNormal.xyz),g=vec3(hx,0,hz)/(2.0*stepSize);
    g-=n*dot(g,n);
    g*=min(1.0,2.0/max(length(g),0.00001));
    return normalize(n-g);
}
// Recover the horizontal floor behind UZDoom's vertical horizon closure.
// The closure sits on the camera-centred +/-32768 square. Its untransformed
// V coordinate is -(pixelHeight-floorHeight), independent of floor height.
// Undo texture scale/rotation/panning before intersecting the camera ray.
vec2 LavaWorldPosition()
{
    vec3 delta=pixelpos.xyz-uCameraPos.xyz;
    vec3 geometric=cross(dFdx(pixelpos.xyz),dFdy(pixelpos.xyz));
    float edge=max(abs(delta.x),abs(delta.z));
    bool closure=abs(edge-32768.0)<1.0 &&
                 abs(geometric.y)<0.01*max(length(geometric),0.00001);
    if(closure)
    {
        vec4 rawUV=inverse(TextureMatrix)*vTexCoord;
        float planeY=pixelpos.y+rawUV.y;
        float dy=delta.y;
        dy=(dy<0.0 ? -1.0 : 1.0)*max(abs(dy),0.0001);
        float t=clamp((planeY-uCameraPos.y)/dy,1.0,4096.0);
        return uCameraPos.xz+delta.xz*t;
    }
    return pixelpos.xz;
}

void SetupMaterial(inout Material mat)
{
    vec2 world=LavaWorldPosition();
    // Shallow parallax: the bed lies five units beneath the crust. Bound the
    // displacement at grazing angles so openings do not stretch at the horizon.
    vec3 ray=normalize(pixelpos.xyz-uCameraPos.xyz);
    vec2 parallax=ray.xz/max(abs(ray.y),0.35)*5.0;
    vec2 top=world+timer*vec2(7.0,-4.0);
    vec2 broad=top/310.0;
    vec2 bend=vec2(LavaNoise(broad),LavaNoise(broad+vec2(37.2,19.8)))-0.5;
    vec2 drift=vec2(sin(top.y/91.0+timer*0.38),sin(top.x/113.0-timer*0.31))*0.045;
    vec2 uv=top/185.0+bend*1.15+drift;
    vec4 crust=LavaSmooth(uv);
    vec3 detail=getTexel(top/64.0+bend*0.37-drift).rgb;
    float height=LavaPeak(crust.rgb);
    float opening=smoothstep(0.11,0.42,height);
    float rim=smoothstep(0.035,0.14,height)*(1.0-smoothstep(0.14,0.32,height));

    // The middle current and deeper bed overtake the crust independently.
    vec2 middle=world+parallax*0.5+timer*vec2(13.0,-8.0);
    vec2 deep=world+parallax+timer*vec2(22.0,-13.0);
    vec3 channel=LavaSmooth(middle/112.0+bend*0.42-drift).rgb;
    vec3 bed=LavaSmooth(deep/83.0-bend*0.30+drift*0.7).rgb;
    float eddies=LavaNoise(deep/23.0+vec2(4.7,13.2));
    // Derive hue from source assets, including the user's PLAYPAL. Openings
    // remain incandescent even while a darker part of the deep layer passes.
    vec3 tint=crust.rgb+channel*0.55+bed*0.25;
    tint/=max(0.001,LavaPeak(tint));
    vec3 radiance=tint*(0.46+0.30*eddies)+bed*0.42;
    radiance=mix(radiance,max(channel*1.10,tint*0.26),0.42);

    // Fine relief is evaluated per pixel, not enlarged from 64x64 texels.
    // Fade frequencies smaller than a screen pixel to avoid distance shimmer.
    float footprint=max(length(dFdx(world)),length(dFdy(world)));
    float fineWeight=1.0-smoothstep(1.2,4.0,footprint);
    float grain=mix(0.5,LavaNoise(top/2.2)*0.6+LavaNoise(top/5.1)*0.4,fineWeight);
    // Filled, softly varying melt instead of a bright noise isoline. A ridge
    // around noise == 0.5 would draw a connected orange net over the liquid.
    vec2 meltUV=deep/vec2(9.0,6.0)+bend*1.7;
    float melt=LavaNoise(meltUV)*0.7+LavaNoise(meltUV*1.87+vec2(17.3,6.8))*0.3;
    float heat=smoothstep(0.18,0.82,melt);
    radiance*=mix(0.92,0.76+heat*0.34,fineWeight);
    float region=LavaNoise(broad*0.71+vec2(8.7,21.4));
    float ridge=smoothstep(0.08,0.38,height);
    vec3 rock=max(crust.rgb*ridge*mix(1.1,1.7,region)*(0.65+LavaPeak(detail)*0.9),
                  detail*mix(0.20,0.58,region));
    rock*=mix(0.45,1.10,smoothstep(0.25,0.70,region))*(0.80+grain*0.4);
    vec3 color=mix(rock,radiance,opening*0.58);
    // A dark lip and a warm inner edge separate the upper crust from the bed.
    color+=tint*rim*(0.12+0.13*eddies);
    // Clustered angular, folded basalt plates from the new high-resolution
    // height texture, advected independently of the molten layers beneath them.
    vec2 raft=world+timer*vec2(4.0,-2.4);
    vec2 dx=dFdx(world),dy=dFdy(world);
    vec2 slope=ray.xz/max(abs(ray.y),0.30);
    vec3 hit=LavaCrustHit(raft,slope,dx,dy);
    vec3 plate=LavaCrustField(hit.xy,dx,dy);
    float floe=plate.y;
    vec3 bumpedNormal=LavaCrustNormal(hit.xy,dx,dy);
    // Folds remain legible in sector-only lighting through height-linked
    // material variation. Real dynamic lights also use the derived normal.
    float folds=smoothstep(0.10,0.56,plate.x);
    vec3 basalt=vec3(0.055,0.050,0.046)*(0.42+folds*2.2);
    float edgeHeat=(1.0-smoothstep(0.06,0.20,plate.x))*floe;
    color=mix(color,basalt,floe);
    color+=tint*edgeHeat*0.24;
    color*=min(1.0,0.98/max(0.001,LavaPeak(color)));
    mat.Base=vec4(color,crust.a);
    mat.Normal=bumpedNormal;
    float molten=clamp(opening*1.15+rim*0.38,0.0,1.0);
    mat.Bright=vec4(vec3(clamp(molten*(1.0-floe)+edgeHeat*0.45,0.0,1.0)),1.0);

    // Fade towards the effective sector fog color using the reconstructed floor
    // distance, including the horizon closure. Preserve the first 6400 units.
    // Inverse distance reaches the target only at infinity, avoiding a solid
    // finite-distance band. Smoothstep gives a soft start and horizon edge.
    float farDistance=length(world-uCameraPos.xz);
    float farVisibility=smoothstep(0.0,1.0,6400.0/max(farDistance,6400.0));
    LavaFarVisibility=farVisibility;
    mat.Base.rgb*=farVisibility;
    mat.Bright.rgb*=farVisibility;


}

// Compensate only molten emission before the engine applies its colored fog.
#ifndef UTNT_LAVA_FOG_LIGHT
#define UTNT_LAVA_FOG_LIGHT

float LavaFogGain()
{
    if(uFogEnabled>=0 || uFogEnabled==-3)return 0.0;
    float dist=uFogEnabled==-1?max(16.0,pixelpos.w):max(16.0,distance(pixelpos.xyz,uCameraPos.xyz));
    if(uThickFogDistance>0.0 && dist>uThickFogDistance)dist+=uThickFogMultiplier*(dist-uThickFogDistance);
    float visibility=clamp(exp2(uFogDensity*dist),0.0,1.0);
    // Molten emission travels farther than reflected light, but dense fog still wins.
    return min(32.0,(pow(visibility,.28)-visibility)/max(visibility,.00001));
}
vec3 LavaEngineMaterialLight(Material material, vec3 color);
vec3 ProcessMaterialLight(Material material, vec3 color)
{
    vec3 lit=LavaEngineMaterialLight(material,color);
    vec3 emission=material.Base.rgb*clamp(material.Bright.rgb,0.0,1.0);
    return lit+emission*LavaFogGain()+uFogColor.rgb*(1.0-LavaFarVisibility);
}
#define ProcessMaterialLight LavaEngineMaterialLight
#endif
