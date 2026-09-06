void main()
{
    vec2 zoomed = (TexCoord - 0.5) * (1.0 - waterFactor * 2.0) + 0.5;
    float phase = InputTimeGame * 1.75;
    vec2 offset = waterFactor * sin(6.28318530718 * zoomed.yx + phase);
    FragColor = texture(InputTexture, clamp(zoomed + offset, vec2(0.0), vec2(1.0)));
}
