// Sample the actual QRUNT63 silhouette; do not replace it with a radial blob.
vec4 ProcessTexel()
{
    vec4 c=getTexel(vTexCoord.st);
    float ink=clamp((c.r-max(c.g,c.b))*2.8,0.0,1.0)*c.a;
    vec3 gold=mix(vec3(0.90,0.20,0.012),vec3(.95,.32,.022),smoothstep(0.1,0.95,ink));
    return vec4(gold*ink,ink);
}
