// A single world-space cloud sheet crosses every cube face without UV seams.
// Purely cosmetic renderer time: never changes the shared weather/game clock.
vec4 ProcessTexel()
{
    vec2 baseSize = vec2(textureSize(basemap,0));
    vec2 baseUV = (clamp(vTexCoord.st,0.0,1.0)*(baseSize-1.0)+0.5)/baseSize;
    vec4 base = texture(basemap, baseUV);
    // Engine coordinates: Doom X, height, Doom Y. Authored camera centres.
    vec3 centre = pixelpos.z < 0.0 ? vec3(3812.0,156.0,-2272.0)
                                  : vec3(2848.0,308.0,2272.0);
    vec3 ray = normalize(pixelpos.xyz-centre);
    // Above the tallest landscape silhouette; hills and horizon stay fixed.
    float sky = smoothstep(0.55,0.82,ray.y);
    vec2 plane = ray.xz/max(ray.y,0.25)*0.26+vec2(0.5);
    // One tile in 200 seconds. The two skies use their own authored cloud mask.
    vec2 uv = fract(plane+vec2(timer*0.005, timer*0.0012));
    vec2 size = vec2(textureSize(cloudmap,0));
    uv = (uv*(size-1.0)+0.5)/size;
    float cloud = texture(cloudmap,uv).r;
    // A thin translucent cloud layer; preserve outdoor/hell colour and lighting.
    base.rgb *= 1.0+(cloud-0.5)*0.32*sky;
    return base;
}
