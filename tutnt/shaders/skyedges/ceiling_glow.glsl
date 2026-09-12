// Live sector ceiling glow for model surfaces. The state canvas is authored
// in top-down UI coordinates; raw GPU texels use the opposite vertical axis.
float SkyGlowNumber(vec3 pixel) { return dot(floor(pixel*255.0+0.5),vec3(65536.0,256.0,1.0)); }
vec3 SkyGlowCell(int index) { return texelFetch(skyGlowState,ivec2(index%256,255-index/256),0).rgb; }
void SkyEdgeCeilingGlow(inout Material mat)
{
    int base=int(SkyGlowNumber(texelFetch(skyGlowMeta,ivec2(0),0).rgb))*5;
    float range=SkyGlowNumber(SkyGlowCell(base+1))/256.0;
    if(range<=0.0)return;
    vec2 slope=vec2(SkyGlowNumber(SkyGlowCell(base+2)),SkyGlowNumber(SkyGlowCell(base+3)))/1048576.0-8.0;
    float height=(SkyGlowNumber(SkyGlowCell(base+4))-8388608.0)/256.0;
    vec3 world=pixelpos.xzy;
    float distance=max(dot(slope,world.xy)+height-world.z,0.0);
    // Bright augments the light color before it multiplies the original
    // textured surface, matching wall glow without painting over its relief.
    mat.Bright.rgb+=desaturate(vec4(SkyGlowCell(base)*clamp(1.0-distance/range,0.0,1.0),1.0)).rgb;
}
