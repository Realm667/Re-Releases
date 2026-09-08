// Atlas stores smoke density on black; all four shapes share this material.
vec4 ProcessTexel()
{
    vec2 uv=vTexCoord.st;
    vec2 warp=vec2(sin(uv.y*15.0+timer*0.63),sin(uv.x*17.0-timer*0.49))*0.009;
    vec2 q=clamp(uv+warp,0.008,0.992);
    // Integrate fine strands even when the player's texture filter is disabled.
    vec3 sampleColor=getTexel(q).rgb*0.40;
    sampleColor+=(getTexel(q+vec2(0.003,0.0)).rgb+getTexel(q-vec2(0.003,0.0)).rgb
                 +getTexel(q+vec2(0.0,0.003)).rgb+getTexel(q-vec2(0.0,0.003)).rgb)*0.15;
    float density=dot(sampleColor,vec3(0.333333));
    float border=smoothstep(0.0,0.055,min(min(uv.x,uv.y),min(1.0-uv.x,1.0-uv.y)));
    float alpha=smoothstep(0.008,0.40,density)*border;
    // Visible smoke color peaks at #999999; density/opacity remain unchanged.
    vec3 smokeColor=mix(vec3(0.20,0.18,0.16),vec3(0.60),clamp(density,0.0,1.0));
    return vec4(smokeColor,alpha);
}
