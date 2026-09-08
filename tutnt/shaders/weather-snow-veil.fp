vec4 ProcessTexel()
{
    vec2 uv=vTexCoord.st;
    vec2 q=uv+vec2(sin(uv.y*11.0+timer*.37),sin(uv.x*13.0-timer*.29))*.012;
    // Wide anisotropic filter: broad softness plus a wind-aligned smear.
    float d=dot(getTexel(clamp(q,vec2(.001),vec2(.999))).rgb,vec3(.333333))*.24;
    d+=dot(getTexel(clamp(q+vec2(.045,.014),vec2(.001),vec2(.999))).rgb,vec3(.333333))*.18;
    d+=dot(getTexel(clamp(q-vec2(.045,.014),vec2(.001),vec2(.999))).rgb,vec3(.333333))*.18;
    d+=dot(getTexel(clamp(q+vec2(.090,.020),vec2(.001),vec2(.999))).rgb,vec3(.333333))*.12;
    d+=dot(getTexel(clamp(q-vec2(.090,.020),vec2(.001),vec2(.999))).rgb,vec3(.333333))*.12;
    d+=dot(getTexel(clamp(q+vec2(.135,.030),vec2(.001),vec2(.999))).rgb,vec3(.333333))*.08;
    d+=dot(getTexel(clamp(q-vec2(.135,.030),vec2(.001),vec2(.999))).rgb,vec3(.333333))*.08;
    vec2 edge=min(uv,1.0-uv);
    float envelope=smoothstep(0.,.28,edge.x)*smoothstep(0.,.32,edge.y);
    float ellipse=1.0-smoothstep(.45,1.18,length((uv-.5)*vec2(1.6,2.0)));
    return vec4(vec3(.8),smoothstep(.003,.65,d)*envelope*ellipse*.78);
}
