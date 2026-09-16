// Short world-projected pressure front; scene-only, leaving weapon/HUD readable.
void main()
{
    vec2 uv=TexCoord;
    float aspect=float(textureSize(InputTexture,0).x)/float(textureSize(InputTexture,0).y);
    vec2 metric=vec2(aspect,1.0),d=(uv-focus)*metric;
    float r=length(d),width=max(.012,radius*.075);
    float front=exp(-pow((r-radius)/width,2.0));
    float back=exp(-pow((r-radius+width*1.7)/(width*1.4),2.0));
    float edge=smoothstep(0.0,.025,min(min(uv.x,uv.y),min(1.0-uv.x,1.0-uv.y)));
    vec2 shift=d/max(r,.001)/metric*(front-back*.55)*.014*strength*edge;
    vec3 scene=texture(InputTexture,clamp(uv+shift,vec2(.001),vec2(.999))).rgb;
    scene=mix(scene,vec3(.78,.86,.89),front*.09*strength);
    FragColor=vec4(scene,1.0);
}
