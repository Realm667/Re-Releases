vec4 ProcessTexel()
{
    vec2 uv=vTexCoord.st;
    vec3 s=getTexel(uv).rgb;
    float d=max(s.r,max(s.g,s.b));
    float edge=smoothstep(0.0,0.025,min(min(uv.x,uv.y),min(1.0-uv.x,1.0-uv.y)));
    return vec4(mix(vec3(0.17,0.20,0.22),vec3(0.82,0.87,0.90),sqrt(d)),smoothstep(0.015,0.25,d)*edge);
}
