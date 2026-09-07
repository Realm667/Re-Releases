vec4 ProcessTexel()
{
    vec4 c=getTexel(vTexCoord.st);
    float light=max(c.r,max(c.g,c.b));
    // Fullbright visual thinkers require the palette in the material itself.
#if EMBER_COLOR == 1
    c.rgb=vec3(light*0.28,light,light*0.12);
#elif EMBER_COLOR == 2
    c.rgb=vec3(light*0.12,light*0.48,light);
#else
    c.rgb=vec3(light,light*0.79,light*0.39);
#endif
    return c;
}
