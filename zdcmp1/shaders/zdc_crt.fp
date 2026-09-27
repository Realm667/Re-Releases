uniform float timer;

vec4 Process(vec4 color)
{
    vec2 uv = gl_TexCoord[0].st;
    vec4 screen = getTexel(uv);
    float scanline = 0.96 + 0.04 * sin(uv.y * 650.0);
    float flicker = 0.98 + 0.02 * sin(timer * 0.41 + uv.y * 12.0);
    float sweep = 0.025 * exp(-80.0 * abs(fract(uv.y + timer * 0.003) - 0.5));
    return vec4(screen.rgb * (scanline * flicker + sweep), screen.a) * color;
}
