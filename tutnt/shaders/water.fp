// Preserve the painted slate palette instead of remapping every edge to silver.
vec4 ProcessTexel()
{
    vec2 uv=vTexCoord.st;
    vec3 s=getTexel(uv).rgb;
    float d=max(s.r,max(s.g,s.b));
    float edge=smoothstep(0.0,0.025,min(min(uv.x,uv.y),min(1.0-uv.x,1.0-uv.y)));
    return vec4(min(s*1.10,vec3(0.55,0.63,0.69)),smoothstep(0.035,0.18,d)*edge);
}
