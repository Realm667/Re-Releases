// Torn infernal curtains, not a rotational noise funnel. The authored emission
// field supplies asymmetric folds; three independently deformed planes recede
// behind the opening. All animation remains in the actual wall material.
mat3 PortalBasis(vec3 n,vec3 p,vec2 uv)
{
    vec3 dx=dFdx(p),dy=dFdy(p);
    vec2 tx=dFdx(uv),ty=dFdy(uv);
    vec3 a=cross(dy,n),b=cross(n,dx);
    vec3 tangent=a*tx.x+b*ty.x,bitangent=a*tx.y+b*ty.y;
    float scale=inversesqrt(max(max(dot(tangent,tangent),dot(bitangent,bitangent)),0.000001));
    return mat3(tangent*scale,bitangent*scale,n);
}
vec4 PortalNoise(vec2 p) { return texture(flowField,p); }
vec2 PortalWarp(vec2 uv,float t,float depth)
{
    vec2 p=uv*2.0-1.0;
    // Opposing, uneven streams and local shear prevent a common orbit.
    vec2 a=PortalNoise(uv*0.82+vec2(t*0.016,-t*0.023)+depth*0.31).gb-0.5;
    vec2 b=PortalNoise(uv*1.73+vec2(-t*0.019,t*0.011)-a*0.7+depth).rg-0.5;
    float drag=sin(t*0.61+p.y*3.1+depth*2.7);
    vec2 motion=a*0.085+b*0.035;
    motion.x+=0.025*sin(p.y*4.3+t*0.43)*sin(t*0.31+depth);
    motion.y+=0.022*drag*p.x;
    // The outer boundary is fixed; wisps tear and fold inside the frame.
    float edge=min(min(uv.x,1.0-uv.x),min(uv.y,1.0-uv.y));
    return uv+motion*smoothstep(0.0,0.12,edge);
}
vec3 PortalArt(vec2 uv)
{
    // Receding planes may leave the opening. Fade them instead of stretching
    // the outermost texel into horizontal bands at oblique viewing angles.
    float edge=min(min(uv.x,1.0-uv.x),min(uv.y,1.0-uv.y));
    return texture(hellCurtain,clamp(uv,vec2(0.002),vec2(0.998))).rgb
        *smoothstep(0.0,0.02,edge);
}
float PortalHeight(vec2 uv) { return PortalArt(uv).r; }
float PortalGlyph(vec2 uv,float index)
{
    if(any(lessThan(uv,vec2(0)))||any(greaterThan(uv,vec2(1))))return 0.0;
    vec4 c=texture(runeAtlas,vec2(uv.x,(mod(index,4.0)+uv.y)/4.0));
    return clamp((c.r-max(c.g,c.b))*3.0,0.0,1.0)*c.a;
}
float SealArc(vec2 p,float depth,float time)
{
    p.x+=.10*sin(p.y*2.+time*.13+depth);
    float r=length(p),a=atan(p.y,p.x)/6.2831853+.5+time*.014*(depth==0.?1.:-1.);
    float target=.43+depth*.20;
    float aa=max(fwidth(r),.002);
    float rings=(1.-smoothstep(.002,.002+aa,abs(r-target)))
        +(1.-smoothstep(.002,.002+aa,abs(r-target-.105)));
    float glyph=PortalGlyph(vec2(fract(a*20.),(r-target-.01)/.083),floor(a*20.));
    float cut=smoothstep(.05,.15,fract(a*3.+depth*.2))*(1.-smoothstep(.55,.72,fract(a*3.+depth*.2)));
    return (rings*.7+glyph)*cut;
}
void SetupMaterial(inout Material mat)
{
    vec2 uv=vTexCoord.st;
    vec3 wall=normalize(vWorldNormal.xyz);
    mat3 basis=PortalBasis(wall,pixelpos.xyz,uv);
    vec3 eye=transpose(basis)*normalize(pixelpos.xyz-uCameraPos.xyz);
    vec2 slope=clamp(eye.xy/max(abs(eye.z),0.38),vec2(-1.8),vec2(1.8));
    float t=timer;
    float pulse=pow(max(0.0,sin(t*6.2831853/7.0)),10.0);
    vec3 color=vec3(0.0005,0.0001,0.0002);
    vec2 surfaceUV=uv;
    for(int i=2;i>=0;i--)
    {
        float depth=float(i)*0.5;
        vec2 q=0.5+(uv-0.5)*(1.0+depth*0.45);
        q+=slope*depth*0.13;
        q+=vec2(0.035*sin(t*0.21+depth*3.0),0.02*cos(t*0.29+depth*2.0))*depth;
        q=PortalWarp(q,t,depth);
        vec3 art=pow(PortalArt(q),vec3(1.35));
        float opacity=smoothstep(0.015,0.21,art.r);
        float fire=smoothstep(0.055,0.30,art.g);
        // Warm amber reference: dark bronze folds, gold/orange veins, small
        // yellow cores. Keep the void black instead of filling it with fire.
        float energy=max(art.r,max(art.g,art.b));
        vec3 tint=mix(vec3(.68,.19,.008),vec3(1.,.59,.075),smoothstep(.08,.5,energy));
        vec3 lit=tint*energy*(.68-depth*.30)*(.88+.20*pulse);
        lit+=vec3(.17,.085,.008)*fire*pulse;
        color=mix(color,lit,opacity)+lit*(1.0-opacity)*0.35;
        if(i==0) surfaceUV=q;
    }
    // Surface relief follows these same torn folds, not unrelated noise.
    vec2 eps=vec2(0.003,0.0);
    float hx=PortalHeight(surfaceUV+eps)-PortalHeight(surfaceUV-eps);
    float hy=PortalHeight(surfaceUV+eps.yx)-PortalHeight(surfaceUV-eps.yx);
    vec3 normal=normalize(vec3(-hx*2.5,-hy*2.5,1.0));
    mat.Normal=normalize(basis*normal);

    vec2 p=uv*2.0-1.0;
    float edge=min(min(uv.x,1.0-uv.x),min(uv.y,1.0-uv.y));
    vec4 noise=PortalNoise(uv*3.2+vec2(t*0.045,-t*0.067));
    float tear=0.005+0.012*noise.b;
    float seam=exp(-abs(edge-tear)*220.0)*(0.25+0.75*noise.g);
    float edgeGlow=exp(-max(edge,0.0)*42.0)*0.12;
    float branches=pow(max(0.0,1.0-abs(noise.r*2.0-1.0)),24.0)
        *exp(-max(edge,0.0)*20.0)*(0.25+0.35*pulse);
    color+=vec3(0.88,0.40,0.030)*(seam*(0.70+0.45*pulse)+edgeGlow+branches);
    // Partial rune rings float at two depths; their dark gaps retain entry visibility.
    for(int i=0;i<2;i++)
    {
        float depth=float(i);
        vec2 ringP=p+slope*(.045+.055*depth);
        float ink=SealArc(ringP,depth,t);
        color+=vec3(.85,.37,.028)*ink*(.64-.18*depth);
    }
    mat.Base=vec4(clamp(color,0.0,1.0),1.0);
    mat.Bright=vec4(vec3(0.86),1.0);
}
