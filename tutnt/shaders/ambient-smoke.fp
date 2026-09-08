vec4 ProcessTexel()
{
    vec2 uv=vTexCoord.st;
    vec2 warp=vec2(sin(uv.y*19.0+timer*0.47),cos(uv.x*21.0-timer*0.39))*0.014;
    vec2 q=clamp(uv+warp,0.005,0.995);
    float d=dot(getTexel(q).rgb,vec3(0.333333));
    float erosion=0.022+0.018*sin(uv.x*27.0+uv.y*31.0+timer*0.63);
    float edge=smoothstep(0.0,0.06,min(min(uv.x,uv.y),min(1.0-uv.x,1.0-uv.y)));
    return vec4(mix(vec3(0.11,0.11,0.12),vec3(0.24,0.24,0.25),clamp(d,0.0,1.0)),smoothstep(erosion*0.6,0.20,d)*edge);
}
