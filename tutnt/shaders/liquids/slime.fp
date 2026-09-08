// Generated from tools/liquid-surface.glsl
#define LIQUID_KIND 1
#define LIQUID_DEPTH 5.500
// Coherent high-resolution height, normals and independent depth currents.
// All coordinates below are renderer-world coordinates (X, Doom Z, Doom Y).
float LiqHash(vec2 p)
{
    vec3 q=fract(vec3(p.xyx)*0.1031);q+=dot(q,q.yzx+33.33);
    return fract((q.x+q.y)*q.z);
}
float LiqNoise(vec2 p)
{
    vec2 i=floor(p),f=fract(p),u=f*f*(3.0-2.0*f);
    return mix(mix(LiqHash(i),LiqHash(i+vec2(1,0)),u.x),mix(LiqHash(i+vec2(0,1)),LiqHash(i+1.0),u.x),u.y);
}
float liqLod;
const mat2 LiqTurn=mat2(0.7648,0.6442,-0.6442,0.7648);

vec2 LiqMirror(vec2 uv,out vec2 direction)
{
    vec2 f=fract(uv*0.5)*2.0;
    direction=vec2(1.0)-2.0*step(vec2(1.0),f);
    // Mirrored boundaries are continuous even if source art edges differ.
    return 1.0-abs(f-1.0);
}
float LiqHeightSample(vec2 uv)
{
    vec2 direction;uv=LiqMirror(uv,direction);
    vec2 size=vec2(textureSize(liquidHeight,0));
    vec2 p=clamp(uv*size-0.5,vec2(0.0),size-1.001),f=fract(p);
    vec2 b=(floor(p)+0.5)/size;
    vec3 fields=mix(mix(textureLod(liquidHeight,b,0.0).rgb,textureLod(liquidHeight,b+vec2(1,0)/size,0.0).rgb,f.x),
               mix(textureLod(liquidHeight,b+vec2(0,1)/size,0.0).rgb,textureLod(liquidHeight,b+1.0/size,0.0).rgb,f.x),f.y);
    float h=mix(fields.r,fields.g,smoothstep(0.0,2.3,liqLod));
    return mix(h,fields.b,smoothstep(2.0,5.0,liqLod));
}
void LiqCoordinates(vec2 p,out vec2 a,out vec2 b,out float blend)
{
    vec2 bend=vec2(LiqNoise(p/517.0+11.7),LiqNoise(p/463.0+37.4))-0.5;
    vec2 small=vec2(sin(p.y/117.0+timer*0.23),sin(p.x/137.0-timer*0.19));
    a=(p+bend*193.0+small*5.0)/384.0;
    b=(LiqTurn*p*0.713-bend*151.0)/384.0+vec2(3.713,8.291);
    blend=0.18+0.42*smoothstep(0.18,0.82,LiqNoise(p/1103.0+43.7));
}
float LiqField(vec2 p)
{
    vec2 a,b;float blend;LiqCoordinates(p,a,b,blend);
    return mix(LiqHeightSample(a),LiqHeightSample(b),blend);
}
vec2 LiqMapGradient(vec2 p)
{
    vec2 a,b,sa,sb;float blend;LiqCoordinates(p,a,b,blend);
    a=LiqMirror(a,sa);b=LiqMirror(b,sb);
    vec3 na=textureLod(normaltexture,clamp(a,0.001,0.999),0.0).xyz*2.0-1.0;
    vec3 nb=textureLod(normaltexture,clamp(b,0.001,0.999),0.0).xyz*2.0-1.0;
    vec2 ga=-na.xy/max(na.z,0.18)*sa;
    vec2 gb=transpose(LiqTurn)*(-nb.xy/max(nb.z,0.18)*sb)*0.713;
    return mix(ga,gb,blend);
}
vec2 LiqWorldPosition(vec3 n,vec3 tangent,vec3 bitangent)
{
    vec3 delta=pixelpos.xyz-uCameraPos.xyz;
    vec3 geometric=cross(dFdx(pixelpos.xyz),dFdy(pixelpos.xyz));
    float edge=max(abs(delta.x),abs(delta.z));
    bool closure=abs(n.y)>0.85 && abs(edge-32768.0)<1.0 &&
        abs(geometric.y)<0.01*max(length(geometric),0.00001);
    if(closure)
    {
        vec4 rawUV=inverse(TextureMatrix)*vTexCoord;
        float planeY=pixelpos.y+rawUV.y;
        float dy=(delta.y<0.0?-1.0:1.0)*max(abs(delta.y),0.0001);
        float t=clamp((planeY-uCameraPos.y)/dy,1.0,4096.0);
        return uCameraPos.xz+delta.xz*t;
    }
    return vec2(dot(pixelpos.xyz,tangent),dot(pixelpos.xyz,bitangent));
}
vec3 LiqSourceHue()
{
    // The original palette is sampled at runtime, including user PLAYPAL changes.
    vec3 c=getTexel(vec2(0.13,0.17)).rgb+getTexel(vec2(0.31,0.73)).rgb+
        getTexel(vec2(0.53,0.29)).rgb+getTexel(vec2(0.79,0.61)).rgb+
        getTexel(vec2(0.91,0.43)).rgb+getTexel(vec2(0.43,0.91)).rgb;
    return c/max(0.0001,max(c.r,max(c.g,c.b)));
}
void SetupMaterial(inout Material mat)
{
    vec3 n=normalize(vWorldNormal.xyz);
    vec3 tangent=abs(n.y)>0.85?vec3(1,0,0):normalize(vec3(n.z,0,-n.x));
    vec3 bitangent=abs(n.y)>0.85?vec3(0,0,1):normalize(cross(n,tangent));
    vec2 world=LiqWorldPosition(n,tangent,bitangent);
    float footprint=max(length(dFdx(world)),length(dFdy(world)));
    liqLod=clamp(log2(max(1.0,footprint*1024.0/384.0)),0.0,9.0);
    vec3 ray=normalize(pixelpos.xyz-uCameraPos.xyz);
    vec2 slope=vec2(dot(ray,tangent),dot(ray,bitangent))/max(abs(dot(ray,n)),0.32);
    float reliefFade=1.0-smoothstep(2.0,6.0,footprint);
#if LIQUID_KIND == 0
    vec2 velocity=vec2(12.0,-5.5);
#elif LIQUID_KIND == 1
    vec2 velocity=vec2(3.7,-1.8);
#else
    vec2 velocity=vec2(7.4,-3.1);
#endif
    vec2 top=world-timer*velocity;
    // A bounded two-step height intersection keeps the surface stable at grazing angles.
    vec2 hit=top;
    for(int i=0;i<2;i++)hit=top-slope*(LiqField(hit)-0.30)*LIQUID_DEPTH*reliefFade;
    float h=LiqField(hit);
    float stepSize=max(0.6,min(3.0,footprint));
    vec2 gradient=vec2(LiqField(hit+vec2(stepSize,0))-LiqField(hit-vec2(stepSize,0)),
                       LiqField(hit+vec2(0,stepSize))-LiqField(hit-vec2(0,stepSize)))*LIQUID_DEPTH/(2.0*stepSize);
    // The matching normal asset supplies fine relief below the finite-difference scale.
    gradient+=LiqMapGradient(hit)*0.22*reliefFade;
    vec3 g=tangent*gradient.x+bitangent*gradient.y;g-=n*dot(g,n);
    vec3 bumpedNormal=normalize(n-g);
    vec2 middle=world+slope*LIQUID_DEPTH*0.45-timer*velocity*1.71;
    vec2 deep=world+slope*LIQUID_DEPTH-timer*velocity*2.57;
    float m=LiqField(middle*1.29+vec2(139.3,317.1));
    float d=LiqField(deep*1.83+vec2(739.7,183.2));
    float open=1.0-smoothstep(0.25,0.62,h);
    vec3 hue=LiqSourceHue();
    float macro=LiqNoise(world/773.0+vec2(18.2,47.6));
    vec3 color;
#if LIQUID_KIND == 0
    color=hue*(0.012+pow(h,1.35)*0.62);
    color+=hue*(m*0.105+d*0.035)*open;
    color*=0.82+macro*0.33;
    mat.Specular=mix(hue,vec3(1.0),0.55)*0.46;
    mat.Glossiness=52.0;mat.SpecularLevel=0.42;
#elif LIQUID_KIND == 1
    float skin=smoothstep(0.34,0.64,h)*smoothstep(0.17,0.62,macro);
    color=hue*(0.025+h*0.27+open*m*0.047);
    color=mix(color,hue*(0.045+h*0.25),skin);
    mat.Specular=mix(hue,vec3(1.0),0.15)*mix(0.38,0.10,skin);
    mat.Glossiness=mix(38.0,12.0,skin);mat.SpecularLevel=0.32;
#else
    color=hue*(0.008+pow(h,1.6)*0.92+open*m*0.055);
    color*=0.77+macro*0.40;
    mat.Specular=mix(hue,vec3(1.0),0.25)*0.27;
    mat.Glossiness=58.0;mat.SpecularLevel=0.33;
#endif
    // Subtle material variation reads in sector lighting; directed highlights use engine lights.
    color*=0.84+0.24*smoothstep(0.16,0.65,h);
    mat.Base=vec4(clamp(color,0.0,0.96),getTexel(vTexCoord.st).a);
    mat.Normal=bumpedNormal;
    mat.Bright=vec4(0.0,0.0,0.0,1.0);
}
