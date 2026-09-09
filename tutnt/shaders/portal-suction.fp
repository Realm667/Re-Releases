void main()
{
    vec2 uv=TexCoord;
    float aspect=float(textureSize(InputTexture,0).x)/float(textureSize(InputTexture,0).y);
    vec2 metric=vec2(aspect,1.0);
    vec2 d=(uv-focus)*metric;
    float r=length(d);
    float angle=atan(d.y,d.x);
    // Broken filaments travel inward. Unequal angular frequencies keep the
    // pull irregular; the image never rotates or shakes as a whole.
    float lane=pow(max(0.0,sin(angle*17.0+sin(angle*7.0)*1.8+phase*.35)),12.0);
    float wave=sin(r*42.0+phase*8.0+sin(angle*5.0)*1.4);
    float envelope=smoothstep(.02,.16,r)*(1.0-smoothstep(.35,.95,r));
    float edge=min(min(uv.x,1.0-uv.x),min(uv.y,1.0-uv.y));
    envelope*=smoothstep(0.0,.055,edge);
    float pull=amount*envelope*(.010+.009*wave+.014*lane);
    vec2 shift=d/max(r,.001)*pull/metric;
    vec3 color=texture(InputTexture,uv+shift).rgb;
    // A short directional smear reinforces acceleration into the opening.
    color=mix(color,texture(InputTexture,uv+shift*1.9).rgb,amount*envelope*.22);
    float filament=lane*pow(max(0.0,wave),7.0)*envelope*amount;
    color+=vec3(.13,.064,.006)*filament;
    FragColor=vec4(color,1.0);
}
