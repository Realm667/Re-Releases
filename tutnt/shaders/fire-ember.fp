vec4 ProcessTexel()
{
    vec4 c=getTexel(vTexCoord.st);
    float light=max(c.r,max(c.g,c.b));
    c.rgb=vec3(light,light*0.79,light*0.39);
    return c;
}
