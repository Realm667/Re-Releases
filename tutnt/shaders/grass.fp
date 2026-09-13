// Authentic low-resolution silhouettes and ground-matched limited palettes.
vec4 ProcessTexel()
{
    vec2 sourceSize = vec2(textureSize(tex, 0));
    vec2 grid = vec2(max(1.0, floor(32.0*sourceSize.x/sourceSize.y)),32.0);
    vec2 uv = (floor(vTexCoord.st*grid)+0.5)/grid;
    vec4 color = getTexel(uv);
    float value = clamp(dot(color.rgb,vec3(0.30,0.59,0.11))*1.7,0.0,1.0);
    value = floor(value*5.0+0.5)/5.0;
    float dry = step(color.g,color.r);
#ifdef BRIGHT_GRASS
    vec3 dark = vec3(23.0,39.0,18.0)/255.0;
    vec3 light = mix(vec3(91.0,156.0,65.0),vec3(109.0,139.0,68.0),dry)/255.0;
#else
    vec3 dark = vec3(17.0,19.0,13.0)/255.0;
    vec3 light = mix(vec3(70.0,74.0,49.0),vec3(76.0,71.0,52.0),dry)/255.0;
#endif
    color.rgb = mix(dark,light,value);
    // Stepped pixel silhouettes, with softness confined to the roots.
    color.a = step(0.4,color.a)*smoothstep(0.0,0.16,1.0-vTexCoord.t);
    return color;
}
