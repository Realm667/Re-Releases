uniform float timer;

vec4 Process(vec4 color)
{
    vec2 uv = gl_TexCoord[0].st;
    vec4 nearLayer = getTexel(uv);
    vec4 farLayer = getTexel(vec2(uv.x + timer * 0.00018, uv.y));
    return vec4(mix(nearLayer.rgb, farLayer.rgb, 0.12), nearLayer.a) * color;
}
