// A soft tapered ribbon; color matches the orange rune particles.
vec4 ProcessTexel()
{
    vec2 uv=vTexCoord.st;
    float head=1.0-uv.y;
    float width=mix(.10,.42,head);
    float x=(uv.x-.5)/width;
    float mask=exp(-x*x*5.0)*smoothstep(0.0,.12,uv.y)*smoothstep(0.0,.24,head);
    mask*=mix(.25,1.0,head);
    return vec4(vec3(.95,.25,.012)*mask,mask);
}
