// Periodize a narrow border only. The interior uses the generated texel unchanged.
vec4 ProcessTexel()
{
    vec2 uv=vTexCoord.st;
    vec2 f=fract(uv);
    vec2 w=vec2(1.0)-smoothstep(vec2(0.0),vec2(0.016),min(f,vec2(1.0)-f));
    vec4 c=getTexel(uv);
    if(w.x>0.0)c=mix(c,getTexel(uv+vec2(0.5,0.0)),w.x);
    if(w.y>0.0)
    {
        vec4 d=getTexel(uv+vec2(0.0,0.5));
        if(w.x>0.0)d=mix(d,getTexel(uv+vec2(0.5,0.5)),w.x);
        c=mix(c,d,w.y);
    }
    return c;
}
