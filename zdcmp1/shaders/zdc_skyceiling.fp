uniform float timer;

vec4 Process(vec4 color)
{
    vec2 uv = gl_TexCoord[0].st;
    vec4 slow = getTexel(uv + vec2(timer * 0.00007, timer * 0.00002));
    vec4 counter = getTexel(uv + vec2(-timer * 0.00003, timer * 0.00004));
    return mix(slow, counter, 0.12) * color;
}
