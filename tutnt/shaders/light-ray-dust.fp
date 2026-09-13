// A soft grain, without the rectangular stencil or fire halo animation.
vec4 ProcessTexel()
{
    float radius = length(vTexCoord.st*2.-1.);
    float mask = 1.-smoothstep(.12,1.,radius);
    return vec4(getTexel(vTexCoord.st).rgb,mask*mask);
}
