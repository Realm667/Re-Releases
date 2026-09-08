// Neutral pressure steam. Nine filtered taps soften the fine density contours.
vec4 ProcessTexel()
{
    vec2 uv=vTexCoord.st;
    float phase=(pixelpos.x+pixelpos.y+pixelpos.z)*0.025;
    vec2 warp=vec2(sin(uv.y*16.0+timer*1.15+phase),
        sin(uv.x*19.0-timer*0.93+phase))*0.012;
    vec2 q=clamp(uv+warp,0.012,0.988);
    const float radius=0.0065;
    // Normalized 3x3 Gaussian kernel; also works with nearest world filtering.
    vec3 c=getTexel(q).rgb*0.25;
    c+=(getTexel(q+vec2(radius,0.0)).rgb+getTexel(q-vec2(radius,0.0)).rgb
        +getTexel(q+vec2(0.0,radius)).rgb+getTexel(q-vec2(0.0,radius)).rgb)*0.125;
    c+=(getTexel(q+vec2(radius,radius)).rgb+getTexel(q-vec2(radius,radius)).rgb
        +getTexel(q+vec2(radius,-radius)).rgb+getTexel(q+vec2(-radius,radius)).rgb)*0.0625;
    float density=dot(c,vec3(0.333333));
    float border=smoothstep(0.0,0.075,min(min(uv.x,uv.y),min(1.0-uv.x,1.0-uv.y)));
    float alpha=smoothstep(0.006,0.44,density)*border;
    // #999999 is the upper material tone, before scene lighting/transparency.
    vec3 color=mix(vec3(0.46),vec3(0.60),smoothstep(0.03,0.70,density));
    return vec4(color,alpha);
}
