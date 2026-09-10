// Compact emission halo with a smooth zero border; no scene brightness filter.
vec4 ProcessTexel()
{
    vec2 p=(vTexCoord.st-vec2(0.5))*2.0;
    float r2=dot(p,p);
    float edge=1.0-smoothstep(0.64,1.0,r2);
    float halo=(0.72*exp(-5.5*r2)+0.28*exp(-18.0*r2))*edge;
    return vec4(vec3(1.0),halo);
}
