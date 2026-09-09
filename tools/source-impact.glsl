// A short expanding refraction front in the scene pass, before HUD composition.
void main()
{
    vec2 uv=TexCoord;
    float aspect=float(textureSize(InputTexture,0).x)/float(textureSize(InputTexture,0).y);
    vec2 metric=vec2(aspect,1.0);
    vec2 delta=(uv-focus)*metric;
    float r=length(delta)/max(radius,.001);
    float front=mix(.08,1.4,progress);
    float shell=exp(-pow((r-front)/.12,2.0));
    float recoil=sin(r*21.0-progress*12.0)*exp(-r*r*5.0)*.22;
    float envelope=sin(progress*3.14159265)*(1.0-progress);
    float edge=min(min(uv.x,1.0-uv.x),min(uv.y,1.0-uv.y));
    float fade=smoothstep(0.0,.04,edge)*(1.0-smoothstep(1.35,1.65,r));
    vec2 direction=delta/max(length(delta),.001);
    vec2 shift=direction/metric*(shell+recoil)*radius*.065*amount*envelope*fade;
    vec2 sampleUV=clamp(uv+shift,vec2(.001),vec2(.999));
    vec3 color=texture(InputTexture,sampleUV).rgb;
    // Restrained spectral separation confined to the travelling light front.
    color.r=texture(InputTexture,clamp(sampleUV+shift*.06,vec2(.001),vec2(.999))).r;
    color.b=texture(InputTexture,clamp(sampleUV-shift*.06,vec2(.001),vec2(.999))).b;
    FragColor=vec4(color,1.0);
}
