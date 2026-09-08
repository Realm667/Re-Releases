// Broad density falloff and a small spatial blur soften the charcoal silhouette.
float smokeDensity(vec2 q)
{
    return dot(getTexel(clamp(q,0.002,0.998)).rgb,vec3(0.333333));
}
vec4 ProcessTexel()
{
    vec2 uv=vTexCoord.st;
    vec2 warp=vec2(sin(uv.y*19.0+timer*0.47),cos(uv.x*21.0-timer*0.39))*0.014;
    vec2 q=uv+warp;
    vec2 dx=vec2(0.009,0.0),dy=vec2(0.0,0.009);
    float d=smokeDensity(q)*0.25;
    d+=(smokeDensity(q+dx)+smokeDensity(q-dx)+smokeDensity(q+dy)+smokeDensity(q-dy))*0.125;
    d+=(smokeDensity(q+dx+dy)+smokeDensity(q+dx-dy)+smokeDensity(q-dx+dy)+smokeDensity(q-dx-dy))*0.0625;
    float edge=smoothstep(0.0,0.16,min(min(uv.x,uv.y),min(1.0-uv.x,1.0-uv.y)));
    return vec4(mix(vec3(0.11,0.11,0.12),vec3(0.24,0.24,0.25),clamp(d,0.0,1.0)),smoothstep(0.004,0.55,d)*edge);
}
