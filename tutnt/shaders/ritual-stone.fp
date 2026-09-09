// Recolor only red ink/emission. Native stone pixels and alpha remain intact.
void SetupMaterial(inout Material mat)
{
    vec4 c=getTexel(vTexCoord.st);
    float ink=clamp((c.r-max(c.g,c.b))*3.5,0.0,1.0);
    vec3 gold=mix(vec3(.52,.12,.007),vec3(.83,.25,.015),ink);
    mat.Base=vec4(mix(c.rgb,gold,ink),c.a);
    mat.Bright=vec4(vec3(ink),1.0);
}
