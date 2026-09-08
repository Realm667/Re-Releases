// Four existing density shapes get a separate, neutral pressure-steam material.
vec4 ProcessTexel()
{
    vec2 uv=vTexCoord.st;
    float phase=(pixelpos.x+pixelpos.y+pixelpos.z)*0.025;
    vec2 warp=vec2(sin(uv.y*16.0+timer*1.15+phase),
        sin(uv.x*19.0-timer*0.93+phase))*0.012;
    vec2 q=clamp(uv+warp,0.009,0.991);
    vec3 c=getTexel(q).rgb*0.40;
    c+=(getTexel(q+vec2(0.0025,0.0)).rgb+getTexel(q-vec2(0.0025,0.0)).rgb
        +getTexel(q+vec2(0.0,0.0025)).rgb+getTexel(q-vec2(0.0,0.0025)).rgb)*0.15;
    float density=dot(c,vec3(0.333333));
    float border=smoothstep(0.0,0.06,min(min(uv.x,uv.y),min(1.0-uv.x,1.0-uv.y)));
    float alpha=smoothstep(0.014,0.42,density)*border;
    vec3 color=mix(vec3(0.53,0.54,0.55),vec3(0.92,0.92,0.90),smoothstep(0.03,0.70,density));
    return vec4(color,alpha);
}
