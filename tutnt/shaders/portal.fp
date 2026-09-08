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
        // Deep folds stay blood-red; only isolated veins reach orange.
        vec3 lit=art*(0.57-depth*0.30)*(0.83+0.30*pulse);
        lit+=vec3(0.14,0.006,0.001)*fire*pulse;
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
    color+=vec3(0.72,0.019,0.003)*(seam*(0.70+0.45*pulse)+edgeGlow+branches);
    mat.Base=vec4(clamp(color,0.0,1.0),1.0);
    mat.Bright=vec4(vec3(0.86),1.0);
}
