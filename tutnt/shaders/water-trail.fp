// Feather the trace along its length and across its width, without additive glow.
vec4 ProcessTexel()
{
    vec2 uv=vTexCoord.st;
    vec4 s=getTexel(uv);
    float d=dot(s.rgb,vec3(0.2126,0.7152,0.0722));
    float tail=smoothstep(0.08,0.70,uv.y);
    float sides=1.0-smoothstep(0.015,0.09,abs(uv.x-0.5));
    float head=1.0-smoothstep(0.68,0.77,uv.y);
    vec3 tint=mix(vec3(0.22,0.28,0.34),vec3(0.55,0.62,0.68),clamp(d*2.2,0.0,1.0));
    return vec4(min(tint*1.35,vec3(0.55,0.62,0.68)),sqrt(s.a)*smoothstep(0.001,0.05,d)*tail*sides*head);
}
