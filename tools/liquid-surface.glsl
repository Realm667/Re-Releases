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
    vec2 small=vec2(sin(p.y/61.0+timer*0.93),sin(p.x/79.0-timer*0.71));
    a=(p+bend*193.0+small*22.0)/384.0;
    b=(LiqTurn*p*0.713-bend*151.0)/384.0+vec2(3.713,8.291);
    blend=0.18+0.42*smoothstep(0.18,0.82,LiqNoise(p/1103.0+43.7));
}
float LiqField(vec2 p)
{
    vec2 a,b;float blend;LiqCoordinates(p,a,b,blend);
    float art=mix(LiqHeightSample(a),LiqHeightSample(b),blend);
    // Travelling waves change the surface shape, rather than only translating art.
    float phase=LiqNoise(p/137.0)*5.0;
#if LIQUID_KIND == 0
    float waves=sin(dot(p,vec2(0.061,0.037))-timer*2.8+phase)*0.13;
    waves+=sin(dot(p,vec2(-0.043,0.081))-timer*3.7+phase*0.6)*0.065;
#elif LIQUID_KIND == 1
    float waves=sin(dot(p,vec2(0.042,0.027))-timer*1.15+phase)*0.095;
    // Sparse domes inflate and collapse into the moving sludge.
    vec2 cell=floor(p/71.0),local=fract(p/71.0);
    float seed=LiqHash(cell+17.3);
    vec2 center=0.25+0.5*vec2(LiqHash(cell+7.7),LiqHash(cell+39.1));
    float life=max(0.0,sin(timer*1.7+seed*31.0));
    float dome=1.0-smoothstep(0.0,0.19,max(0.0,length(local-center)));
    waves+=dome*dome*life*0.32*step(0.62,seed);
#else
    float waves=sin(dot(p,vec2(0.049,0.031))-timer*1.9+phase)*0.12;
    waves+=sin(dot(p,vec2(-0.036,0.068))-timer*2.4+phase*0.7)*0.05;
#endif
    waves*=1.0-smoothstep(4.0,7.0,liqLod);
    return clamp(art*0.78+0.11+waves,0.03,0.97);
}

vec2 LiqSurfaceHit(vec2 top,vec2 slope,float fade)
{
    // Intersect a height slab, then interpolate the crossing. A real traversal
    // avoids the old fixed-point offset collapsing back towards a flat sample.
    vec2 travel=slope*LIQUID_DEPTH*fade;
    float layer=1.0;
    vec2 uv=top-travel;
    float above=layer-LiqField(uv);
    for(int i=0;i<7;i++)
    {
        float nextLayer=layer-1.0/7.0;
        vec2 nextUV=top-travel*nextLayer;
        float below=nextLayer-LiqField(nextUV);
        if(below<=0.0)return mix(uv,nextUV,clamp(above/max(above-below,0.00001),0.0,1.0));
        uv=nextUV;layer=nextLayer;above=below;
    }
    return uv;
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
    float reliefFade=1.0-smoothstep(4.0,12.0,footprint);
#if LIQUID_KIND == 0
    vec2 velocity=vec2(42.0,-19.0);
#elif LIQUID_KIND == 1
    vec2 velocity=vec2(16.0,-7.0);
#else
    vec2 velocity=vec2(29.0,-13.0);
#endif
    vec2 top=world-timer*velocity;
    vec2 hit=LiqSurfaceHit(top,slope,reliefFade);
    float h=LiqField(hit);
    float stepSize=max(0.6,min(3.0,footprint));
    vec2 gradient=vec2(LiqField(hit+vec2(stepSize,0))-LiqField(hit-vec2(stepSize,0)),
                       LiqField(hit+vec2(0,stepSize))-LiqField(hit-vec2(0,stepSize)))*LIQUID_DEPTH/(2.0*stepSize);
    // The matching normal asset supplies fine relief below the finite-difference scale.
    gradient+=LiqMapGradient(hit)*0.22*reliefFade;
    vec3 g=tangent*gradient.x+bitangent*gradient.y;g-=n*dot(g,n);
    vec3 bumpedNormal=normalize(n-g);
    // Refraction and independent cross-currents visibly separate the layers.
    vec2 middle=world+slope*LIQUID_DEPTH*1.2+gradient*9.0-timer*(velocity*1.75+vec2(-11.0,17.0));
    vec2 deep=world+slope*LIQUID_DEPTH*2.8+gradient*16.0-timer*(velocity*0.63+vec2(16.0,9.0));
    float m=LiqField(middle*1.29+vec2(139.3,317.1));
    float d=LiqField(deep*1.83+vec2(739.7,183.2));
    float open=1.0-smoothstep(0.28,0.78,h);
    vec3 hue=LiqSourceHue();
    float macro=LiqNoise(world/773.0+vec2(18.2,47.6));
    vec3 color;
#if LIQUID_KIND == 0
    color=hue*(0.045+pow(h,1.35)*0.44);
    color=mix(color,hue*(0.05+m*0.36+d*0.18),0.20+open*0.48);
    color*=0.82+macro*0.33;
    mat.Specular=mix(hue,vec3(1.0),0.55)*0.46;
    mat.Glossiness=52.0;mat.SpecularLevel=0.42;
#elif LIQUID_KIND == 1
    float skin=smoothstep(0.34,0.64,h)*smoothstep(0.17,0.62,macro);
    color=hue*(0.05+h*0.20+open*(m*0.19+d*0.07));
    color=mix(color,hue*(0.055+h*0.28),skin*0.72);
    mat.Specular=mix(hue,vec3(1.0),0.15)*mix(0.38,0.10,skin);
    mat.Glossiness=mix(38.0,12.0,skin);mat.SpecularLevel=0.32;
#else
    color=hue*(0.025+pow(h,1.6)*0.66+open*(m*0.27+d*0.10));
    color*=0.77+macro*0.40;
    mat.Specular=mix(hue,vec3(1.0),0.25)*0.27;
    mat.Glossiness=58.0;mat.SpecularLevel=0.33;
#endif
    // A broad environment reflection and height shading keep the moving relief
    // readable in ordinary sector lighting too. These are albedo contributions,
    // attenuated by the sector; they do not make the liquids emissive.
    vec3 environment=normalize(n*0.88+tangent*0.31+bitangent*0.36);
    float diffuse=clamp(dot(bumpedNormal,environment),0.0,1.0);
    vec3 halfway=normalize(environment-ray);
    float reflection=pow(max(0.0,dot(bumpedNormal,halfway)),24.0);
    float fresnel=pow(1.0-clamp(abs(dot(-ray,bumpedNormal)),0.0,1.0),3.0);
    float occlusion=mix(0.61,1.0,smoothstep(0.10,0.64,h));
    color*=occlusion*(0.55+diffuse*0.65);
#if LIQUID_KIND == 0
    color+=mix(hue,vec3(0.64,0.72,0.79),0.48)*(reflection*0.25+fresnel*0.11);
#elif LIQUID_KIND == 1
    color+=mix(hue,vec3(0.61,0.65,0.38),0.25)*(reflection*0.16+fresnel*0.05)*(1.0-skin*0.65);
#else
    color+=mix(hue,vec3(0.71,0.51,0.49),0.24)*(reflection*0.20+fresnel*0.07);
#endif
    mat.Base=vec4(clamp(color,0.0,0.96),getTexel(vTexCoord.st).a);
    mat.Normal=bumpedNormal;
    mat.Bright=vec4(0.0,0.0,0.0,1.0);
}
