// Dedicated small combat puffs from the existing smoke-density atlas.
vec4 ProcessTexel()
{
    vec2 uv=vTexCoord.st;
    vec2 d=vec2(0.025);
    float density=dot(getTexel(uv).rgb,vec3(0.333333))*0.4;
    density+=(dot(getTexel(uv+vec2(d.x,0)).rgb,vec3(0.333333))
             +dot(getTexel(uv-vec2(d.x,0)).rgb,vec3(0.333333))
             +dot(getTexel(uv+vec2(0,d.y)).rgb,vec3(0.333333))
             +dot(getTexel(uv-vec2(0,d.y)).rgb,vec3(0.333333)))*0.15;
    float border=smoothstep(0.0,0.065,min(min(uv.x,uv.y),min(1.0-uv.x,1.0-uv.y)));
    float body=1.0-smoothstep(0.12,0.48,length(uv-vec2(0.5)));
    float alpha=max(smoothstep(0.003,0.23,density),body*0.6)*border;
    return vec4(mix(vec3(0.24,0.22,0.20),vec3(0.58),clamp(density*2.0,0.0,1.0)),alpha);
}
