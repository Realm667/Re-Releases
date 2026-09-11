// Layered lava curtains: foreground ribbons, faster rear flow, and fine spray-
// like streaks within the same opaque material (no new actors or geometry).
float FallHash(vec3 p)
{
    vec3 q=fract(p*0.1031);q+=dot(q,q.yzx+33.33);
    return fract((q.x+q.y)*q.z);
}
float FallNoise(vec3 p)
{
    vec3 i=floor(p),f=fract(p),u=f*f*(3.0-2.0*f);
    float a=mix(mix(FallHash(i),FallHash(i+vec3(1,0,0)),u.x),
                mix(FallHash(i+vec3(0,1,0)),FallHash(i+vec3(1,1,0)),u.x),u.y);
    float b=mix(mix(FallHash(i+vec3(0,0,1)),FallHash(i+vec3(1,0,1)),u.x),
                mix(FallHash(i+vec3(0,1,1)),FallHash(i+vec3(1,1,1)),u.x),u.y);
    return mix(a,b,u.z);
}
float FallPeak(vec3 c) { return max(c.r,max(c.g,c.b)); }
void SetupMaterial(inout Material mat)
{
    vec3 world=pixelpos.xyz;
    vec3 normal=normalize(vWorldNormal.xyz);
    vec3 ray=normalize(world-uCameraPos.xyz);
    vec3 behind=world+(ray-normal*dot(ray,normal))/max(abs(dot(ray,normal)),0.4)*2.8;
    // Height increases upwards. Positive time offsets advect features DOWN.
    float frontZ=world.y+timer*64.0;
    float rearZ=behind.y+timer*110.0;
    vec3 front=vec3(world.xz/18.0,frontZ/145.0);
    front.xy+=vec2(sin(frontZ/85.0),sin(frontZ/113.0))*0.33;
    float ribbon=FallNoise(front);
    float fold=FallNoise(front*vec3(0.44,0.44,0.73)+17.0);
    float fine=FallNoise(vec3(world.xz/5.8,(world.y+timer*87.0)/65.0)+vec3(8.4,3.7,0));
    vec3 rear=vec3(behind.xz/12.0,rearZ/108.0);
    rear.xy+=(fold-0.5)*0.65;
    float undertow=FallNoise(rear+vec3(29.7,11.2,4.1));
    float backThreads=FallNoise(rear*vec3(2.1,2.1,1.7)+7.3);
    float filled=smoothstep(0.27,0.73,ribbon*0.72+fold*0.28);
    float veil=smoothstep(0.35,0.78,fold*0.55+fine*0.45);
    float bend=(fold-0.5)*0.55;
    vec2 ua=vec2(dot(world.xz,vec2(0.8,0.6))/58.0+bend,frontZ/360.0);
    vec2 ub=vec2(dot(behind.xz,vec2(-0.6,0.8))/58.0-bend,rearZ/360.0+0.37);
    vec3 source=(getTexel(ua).rgb+getTexel(ub).rgb)*0.5;
    // An orange texel of the original LAVA patch; preserves palette changes.
    vec3 tint=getTexel(vec2(0.9453125,0.58203125)).rgb;
    tint/=max(0.001,FallPeak(tint));
    vec3 bed=tint*(0.08+0.66*smoothstep(0.32,0.75,undertow))*(0.58+backThreads*0.42);
    vec3 sheet=tint*(0.10+filled*0.78)*(0.40+fine*0.60);
    // The moving foreground partially occludes a separate, faster background.
    float cover=clamp(0.20+filled*0.60+veil*0.10,0.0,0.95);
    vec3 color=mix(bed,sheet,cover)+source*0.35;
    color*=1.0-veil*0.25;
    color*=min(1.0,0.98/max(0.001,FallPeak(color)));
    mat.Base=vec4(color,getTexel(ua).a);
    mat.Normal=normal;
    mat.Bright=vec4(vec3(clamp(0.25+filled*0.75+undertow*0.20-veil*0.15,0.0,1.0)),1.0);
}

#ifndef UTNT_LAVA_FOG_LIGHT
#define UTNT_LAVA_FOG_LIGHT
float LavaFarVisibility=1.0;

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
