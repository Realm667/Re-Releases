// Local world geometry supplies depth testing; no screen-space halo or depth grid.
float CaveHash(vec3 p)
{
    p=fract(p*.1031);p+=dot(p,p.yzx+33.33);
    return fract((p.x+p.y)*p.z);
}
float CaveNoise(vec3 p)
{
    vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
    return mix(mix(mix(CaveHash(i),CaveHash(i+vec3(1,0,0)),f.x),
                   mix(CaveHash(i+vec3(0,1,0)),CaveHash(i+vec3(1,1,0)),f.x),f.y),
               mix(mix(CaveHash(i+vec3(0,0,1)),CaveHash(i+vec3(1,0,1)),f.x),
                   mix(CaveHash(i+vec3(0,1,1)),CaveHash(i+vec3(1,1,1)),f.x),f.y),f.z);
}
vec4 ProcessTexel()
{
    vec2 uv=vTexCoord.st;
#ifdef CAVERN_GRAIN
    float grain=1.-smoothstep(.12,1.,length((uv-.5)*2.));
    return vec4(.51,.45,.37,grain*grain);
#endif
    // Engine material coordinates are X/Z horizontally, Y vertically.
    vec3 p=pixelpos.xyz/vec3(160.,105.,160.);
    p.y-=timer*.22;
    float n=CaveNoise(p)*.7+CaveNoise(p*2.07+11.3)*.3;
#ifdef CAVERN_SMOKE
    float radius=length((uv-.5)*2.);
    float mask=1.-smoothstep(.18,1.,radius);
    return vec4(vec3(.31,.265,.22),mask*mask*(.35+n*.65));
#else
    float height=1.-uv.y;
    float side=1.-smoothstep(.2,1.,abs(uv.x*2.-1.));
    float vertical=smoothstep(0.,.035,height)*(1.-smoothstep(.08,1.,height));
    // Broad luminous bed, with gentle rising folds rather than isolated flames.
    float density=side*vertical*(.62+.38*n);
    vec3 tint=getTexel(vec2(.9453125,.58203125)).rgb;
    tint/=max(.001,max(tint.r,max(tint.g,tint.b)));
    return vec4(tint,density);
#endif
}
