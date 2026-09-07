vec4 ProcessTexel()
{
    vec4 c=getTexel(vTexCoord.st);
    float shade=clamp(dot(c.rgb,vec3(0.333))*2.4,0.0,1.0);
    c.rgb=mix(vec3(0.17,0.15,0.13),vec3(0.57,0.52,0.45),shade);
    return c;
}
