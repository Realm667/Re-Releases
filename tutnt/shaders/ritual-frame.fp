// Keep authored RGBA colors; only the independent mask controls fullbright ink.
void SetupMaterial(inout Material mat)
{
    mat.Base=getTexel(vTexCoord.st);
    mat.Bright=vec4(texture(runeMask,vTexCoord.st).rrr,1.0);
}
