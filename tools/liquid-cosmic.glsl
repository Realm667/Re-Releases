// Spatial particulate materials inspired by native QTELEPT / STARSKY points.
// No actors, frame textures or nebula replacement; each layer has its own depth.
float CosHash(vec2 p)
{
    vec3 q=fract(vec3(p.xyx)*0.1031);q+=dot(q,q.yzx+33.33);
    return fract((q.x+q.y)*q.z);
}
float CosNoise(vec2 p)
{
    vec2 i=floor(p),f=fract(p),u=f*f*(3.0-2.0*f);
    return mix(mix(CosHash(i),CosHash(i+vec2(1,0)),u.x),mix(CosHash(i+vec2(0,1)),CosHash(i+1.0),u.x),u.y);
}
float CosPoints(vec2 p,float spacing,float seed,float density,float phase)
{
    p/=spacing;
    vec2 cell=floor(p),f=fract(p);
    float pixel=max(length(dFdx(p)),length(dFdy(p)));
    float result=0.0;
    for(int y=-1;y<=1;y++)for(int x=-1;x<=1;x++)
    {
        vec2 offset=vec2(float(x),float(y)),id=cell+offset;
        float chance=CosHash(id+seed);
        if(chance<1.0-density)continue;
        vec2 pos=0.13+0.74*vec2(CosHash(id+seed+7.3),CosHash(id+seed+21.7));
        vec2 delta=f-offset-pos;
#if COSMIC_KIND == 0
        delta.y*=0.57;
        float radius=mix(0.035,0.090,CosHash(id+seed+13.7));
#else
        float radius=mix(0.010,0.037,CosHash(id+seed+13.7));
#endif
        float filterWidth=max(radius,pixel*0.65);
        float falloff=dot(delta,delta)/(filterWidth*filterWidth);
        float coverage=min(1.0,radius*radius/(filterWidth*filterWidth));
        float twinkle=0.94+0.06*sin(timer*phase+chance*27.3);
        result+=exp(-falloff)*coverage*twinkle*(0.24+CosHash(id+seed+51.3)*0.76);
    }
    return result;
}
void SetupMaterial(inout Material mat)
{
    vec3 n=normalize(vWorldNormal.xyz);
    vec3 tangent=abs(n.y)>0.85?vec3(1,0,0):normalize(vec3(n.z,0,-n.x));
    vec3 bitangent=abs(n.y)>0.85?vec3(0,0,1):normalize(cross(n,tangent));
    vec2 world=vec2(dot(pixelpos.xyz,tangent),dot(pixelpos.xyz,bitangent));
    vec3 ray=normalize(pixelpos.xyz-uCameraPos.xyz);
    vec2 parallax=vec2(dot(ray,tangent),dot(ray,bitangent))/max(abs(dot(ray,n)),0.4);
    float region=CosNoise(world/541.0+vec2(5.4,13.7));
    float region2=CosNoise(world/183.0+vec2(43.1,19.7));
    float density=0.16+0.60*smoothstep(0.20,0.78,region*0.72+region2*0.28);
    vec3 color;float luminous;
#if COSMIC_KIND == 0
    vec2 bend=(vec2(CosNoise(world/137.0),CosNoise(world/157.0+31.4))-0.5)*30.0;
    vec2 back=world+parallax*23.0-timer*vec2(1.8,-5.1)+bend;
    vec2 mid=world+parallax*9.0-timer*vec2(-2.1,-8.3)-bend*0.3;
    vec2 front=world+parallax*2.0-timer*vec2(2.7,-12.7)+bend*0.2;
    float a=CosPoints(back,11.0,7.7,density,0.55);
    float b=CosPoints(mid,17.0,31.3,density*0.71,0.8);
    float c=CosPoints(front,23.0,61.1,density*0.35,1.05);
    vec3 bronze=vec3(0.48,0.35,0.19);
    color=bronze*(a*0.35+b*0.70+c)+vec3(0.005,0.005,0.004)*region2;
    luminous=clamp((a+b+c)*3.5,0.0,1.0);
#else
    vec2 drift=vec2(sin(timer*0.09),cos(timer*0.07)-1.0);
    float a=CosPoints(world+parallax*34.0,18.0,3.1,density,0.23);
    float b=CosPoints(world+parallax*12.0+drift*0.7,31.0,73.7,density*0.50,0.51);
    float c=CosPoints(world+parallax*3.0+drift*1.7,53.0,103.1,density*0.19,0.73);
#if COSMIC_KIND == 1
    vec3 tint=vec3(0.76,0.79,0.80);
#else
    vec3 tint=vec3(0.85,0.45,0.12);
#endif
    color=tint*(a*0.46+b*0.84+c*1.16);
    luminous=clamp((a+b+c)*4.0,0.0,1.0);
#endif
    mat.Base=vec4(clamp(color,0.0,0.98),getTexel(vTexCoord.st).a);
    mat.Normal=n;
    mat.Bright=vec4(vec3(luminous),1.0);
}
