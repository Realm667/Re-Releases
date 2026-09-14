float Glyph(vec2 uv,float index)
{
    if(any(lessThan(uv,vec2(0)))||any(greaterThan(uv,vec2(1))))return 0.0;
    vec4 c=texture(runeAtlas,vec2(uv.x,(mod(index,4.0)+uv.y)/4.0));
    return c.r*c.a; // Original coverage, independent of the colored PNG.
}
float Ring(float r,float target,float w)
{
    return 1.0-smoothstep(w,w+max(fwidth(r),0.002),abs(r-target));
}
void SetupMaterial(inout Material mat)
{
    vec2 uv=fract(vTexCoord.st),sealUV=(uv-.5)/.82+.5,p=(sealUV-.5)*2.;
    SetMaterialProps(mat,vTexCoord.st);
    float r=length(p),a=atan(p.y,p.x),turn=(a+3.14159265)/6.2831853;
    float spin=turn+timer*.011;
    float glyphs=Glyph(vec2(fract(spin*16.),(r-.73)/.17),floor(spin*16.));
    float segments=smoothstep(.04,.09,fract(spin*4.))*(1.-smoothstep(.91,.96,fract(spin*4.)));
    vec4 art=getTexel((sealUV-.5)/.69+.5);
    float seal=max(art.r,max(art.g,art.b))*art.a*(1.-smoothstep(.64,.7,r));
    float ink=seal*.95+(Ring(r,.71,.003)+Ring(r,.93,.004)+glyphs)*segments;
    float halo=exp(-abs(r-.93)*60.)*.07;
    vec3 gold=mix(vec3(1.,.30,.014),vec3(1.,.68,.15),clamp(ink-.3,0.,1.));
    float stone=.012+.012*sin(p.x*41.)*sin(p.y*37.);
    mat.Base=vec4(vec3(stone*.8,stone*.65,stone*.5)+gold*(ink*.85+halo),1.);
    // A non-emissive native rusty steel rim surrounds the smaller seal.
    float edge=min(min(uv.x,uv.y),min(1.-uv.x,1.-uv.y));
    float rim=1.-smoothstep(.085,.10,edge);
    vec3 steel=texture(padMetal,uv).rgb;
    float bevel=smoothstep(.0,.015,edge)*(1.-.35*smoothstep(.065,.09,edge));
    steel*=.58+.42*bevel;
    vec2 corner=min(uv,1.-uv)-vec2(.045);
    float rivet=1.-smoothstep(.010,.014,length(corner));
    steel=mix(steel,vec3(.30,.19,.11)*(1.-corner.y*15.),rivet);
    mat.Base.rgb=mix(mat.Base.rgb,steel,rim);
    mat.Bright=vec4(vec3(clamp(ink+halo,0.,1.)*(1.-rim)),1.);
}
