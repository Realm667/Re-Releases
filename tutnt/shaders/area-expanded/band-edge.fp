// Finite midtextures wrap horizontally; their vertical clipping stays native.
vec4 ProcessTexel()
{
    vec2 uv=vTexCoord.st;
    float f=fract(uv.x);
    float w=1.0-smoothstep(0.0,0.016,min(f,1.0-f));
    vec4 c=getTexel(uv);
    if(w>0.0)c=mix(c,getTexel(uv+vec2(0.5,0.0)),w);
    return c;
}
