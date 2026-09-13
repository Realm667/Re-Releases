void main()
{
    vec4 scene = texture(InputTexture, TexCoord);
    vec3 color = clamp(scene.rgb, 0.0, 1.0);
    float luminance = dot(color, vec3(0.2126, 0.7152, 0.0722));
    float shadows = 1.0 - smoothstep(0.0, 0.5, luminance);
    float highlights = smoothstep(0.5, 1.0, luminance);
    vec3 weights = vec3(shadows, 1.0 - shadows - highlights, highlights);
    float gain = dot(weights, clamp(toneAmounts, vec3(-1.0), vec3(1.0)));
    float peak = max(color.r, max(color.g, color.b));
    // A bounded exposure curve preserves black, white and RGB ratios. Using
    // the strongest channel for the shoulder avoids colored-light clipping.
    // Positive exposure throughout [-100%, +100%]: no 0/0 at white.
    // One stop in either direction, with smooth monotonic tonal transitions.
    float exposure = exp2(gain);
    float scale = exposure / (1.0 + peak * (exposure - 1.0));
    FragColor = vec4(color * scale, scene.a);
}
