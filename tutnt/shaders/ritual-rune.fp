// Truecolor PNG already contains the thermal ramp; never reduce or recolor it.
vec4 ProcessTexel()
{
    vec4 c=getTexel(vTexCoord.st);
    return vec4(c.rgb*c.a,c.a);
}
