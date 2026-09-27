uniform float timer;

vec4 Process(vec4 color)
{
    vec2 uv = gl_TexCoord[0].st;
    vec2 ripple = vec2(sin(uv.y * 48.0 + timer * 0.035),
                       cos(uv.x * 42.0 - timer * 0.028)) * 0.009;
    vec4 water = getTexel(uv + ripple);
    return vec4(water.rgb * (0.98 + 0.02 * sin((uv.x + uv.y) * 80.0 + timer * 0.04)),
                water.a) * color;
}
