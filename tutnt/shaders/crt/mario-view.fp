// TNT02 Mario secret view filter. Ported from Timothy Lottes' public-domain
// CRT scan-line shader: https://github.com/libretro/glsl-shaders/blob/master/crt/shaders/crt-lottes.glsl
// UZDoom scene pass uses InputTexture/TexCoord; no Libretro vertex/preset state.
vec2 virtualSize;

vec3 Fetch(vec2 p, vec2 offset)
{
    vec2 cell = floor(p * virtualSize + offset) + vec2(0.5);
    return pow(max(texture(InputTexture, clamp(cell / virtualSize, vec2(0.0), vec2(1.0))).rgb, vec3(0.0)), vec3(2.2));
}

float Gaussian(float distance, float hardness)
{
    return exp2(hardness * distance * distance);
}

vec3 Horizontal(vec2 p, float row)
{
    float dx = 0.5 - fract(p.x * virtualSize.x);
    float a = Gaussian(dx - 1.0, -2.5);
    float b = Gaussian(dx, -2.5);
    float c = Gaussian(dx + 1.0, -2.5);
    return (Fetch(p, vec2(-1.0, row)) * a
          + Fetch(p, vec2( 0.0, row)) * b
          + Fetch(p, vec2( 1.0, row)) * c) / (a + b + c);
}

vec2 Warp(vec2 p)
{
    p = p * 2.0 - 1.0;
    p *= vec2(1.0 + p.y * p.y * 0.008, 1.0 + p.x * p.x * 0.012);
    return p * 0.5 + 0.5;
}

vec3 Mask(vec2 pixel)
{
    // Lottes' RGB shadow mask, tempered for a modern high-resolution screen.
    float slot = mod(floor(pixel.x) + floor(pixel.y) * 3.0, 6.0);
    vec3 mask = vec3(0.82);
    if (slot < 2.0) mask.r = 1.10;
    else if (slot < 4.0) mask.g = 1.10;
    else mask.b = 1.10;
    return mask;
}

void main()
{
    vec2 outputSize = vec2(textureSize(InputTexture, 0));
    virtualSize = vec2(min(outputSize.x, 640.0),
                       min(outputSize.y, round(640.0 * outputSize.y / max(outputSize.x, 1.0))));
    // Fit the gently curved picture inside the view; no black corner cutouts.
    vec2 p = (Warp(TexCoord) - 0.5) / vec2(1.008, 1.012) + 0.5;

    float dy = 0.5 - fract(p.y * virtualSize.y);
    vec3 color =
          Horizontal(p, -1.0) * Gaussian(dy - 1.0, -4.0)
        + Horizontal(p,  0.0) * Gaussian(dy,       -4.0)
        + Horizontal(p,  1.0) * Gaussian(dy + 1.0, -4.0);

    // Restrained phosphor spread from adjacent lines.
    vec3 bloom = (Horizontal(p, -1.0) + Horizontal(p, 1.0)) * 0.5;
    color = color * 1.22 + bloom * 0.10;
    color *= Mask(gl_FragCoord.xy);

    // Equal falloff along all four edges, including their midpoints.
    vec2 edge = abs(TexCoord * 2.0 - 1.0);
    float edgeDistance = max(edge.x, edge.y);
    float vignette = 1.0 - 0.14 * smoothstep(0.62, 1.0, edgeDistance);
    color *= vignette;
    FragColor = vec4(pow(max(color, vec3(0.0)), vec3(1.0 / 2.2)), 1.0);
}
