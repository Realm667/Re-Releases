// Compact emission halo with a smooth zero border; no scene brightness filter.
vec4 ProcessTexel()
{
    vec2 p=(vTexCoord.st-vec2(0.5))*2.0;
    float r2=dot(p,p);
    float edge=1.0-smoothstep(0.64,1.0,r2);
    float halo=(0.72*exp(-5.5*r2)+0.28*exp(-18.0*r2))*edge;
    // getTexel applies the VisualThinker's object tint; constant white RGB
    // bypasses that engine step and washes every projectile color out.
    return vec4(getTexel(vTexCoord.st).rgb,halo);
}
