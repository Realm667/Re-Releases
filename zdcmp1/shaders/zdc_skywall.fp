uniform float timer;

vec4 Process(vec4 color)
{
    vec2 uv = gl_TexCoord[0].st;
    vec4 still = getTexel(uv);
    vec4 drifting = getTexel(vec2(uv.x + timer * 0.00010, uv.y));
    float cloudMask = 1.0 - smoothstep(0.18, 0.46, uv.y);
    return vec4(mix(still.rgb, drifting.rgb, 0.12 * cloudMask), still.a) * color;
}
