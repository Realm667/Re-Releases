// Preserve the source alpha, soft gray-blue edges and dark translucent interior.
vec4 ProcessTexel()
{
    vec2 uv=vTexCoord.st;
    vec4 s=getTexel(uv);
    float d=dot(s.rgb,vec3(0.2126,0.7152,0.0722));
    float edge=smoothstep(0.0,0.025,min(min(uv.x,uv.y),min(1.0-uv.x,1.0-uv.y)));
    vec3 tint=mix(vec3(0.22,0.28,0.34),vec3(0.55,0.62,0.68),clamp(d*2.2,0.0,1.0));
    return vec4(min(tint*1.15,vec3(0.55,0.62,0.68)),sqrt(s.a)*smoothstep(0.002,0.09,d)*edge);
}
