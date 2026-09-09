// One bounded pass before bloom/HUD: only the outer 18% of the view is affected.
vec3 sceneAt(vec2 uv)
{
    vec2 halfPixel=0.5/vec2(textureSize(InputTexture,0));
    return texture(InputTexture,clamp(uv,halfPixel,1.0-halfPixel)).rgb;
}

vec3 armor(vec2 uv,vec3 scene)
{
    // Original SBAR material, identical to UTNHFTIL/UTNHBT in TEXTURES.
    // Indexed STBAR follows PLAYPAL automatically, including the HUD greys.
    vec2 size=vec2(textureSize(InputTexture,0));
    vec2 extent=vec2(size.x/size.y*540.0,540.0);
    vec2 p=floor(uv*extent)+0.5;
    vec2 b=min(p,extent-p);
    float cut=min(min(b.x-22.0,b.y-24.0),(b.x+b.y-92.0)*0.707107);
    if(cut>=5.0) return scene;
    // Keep the source pixels crisp, at the same visual grain as the status bar.
    vec2 repeatPixel=mod(floor(p/2.0),32.0);
    vec2 tile=vec2(228.0,5.0)+min(repeatPixel,31.0-repeatPixel);
    vec3 surface=texture(armorTexture,(tile+0.5)/vec2(320.0,32.0)).rgb;
    float outer=min(b.x,b.y);
    float depth=min(outer,-cut);
    if(depth>=0.0 && depth<8.0)
    {
        // Sample the four actual SBAR bevel rows, mirrored at the view opening.
        // No synthetic bronze highlight or separate decorative rivet palette.
        float along=b.y<b.x?p.x:p.y;
        vec2 bevel=vec2(8.0+mod(floor(along/2.0),4.0),floor(depth/2.0));
        surface=texture(armorTexture,(bevel+0.5)/vec2(320.0,32.0)).rgb;
    }
    if(cut>=0.0) surface=vec3(0.018)*(1.0-cut/6.0);
    return mix(scene,surface,strength*(1.0-smoothstep(3.0,5.0,cut)));
}

void main()
{
    vec2 uv=TexCoord;
    vec3 col=texture(InputTexture,uv).rgb;
    if(abilityMode==6) { FragColor=vec4(armor(uv,col),1.0); return; }
    vec2 border=min(uv,1.0-uv);
    float edge=1.0-smoothstep(0.0,0.18,min(border.x,border.y));
    if(edge<=0.0) { FragColor=vec4(col,1.0); return; }
    if(abilityMode==1 && distortion>0.0)
    {
        // Dense radial taps toward the vanishing point produce speed streaks,
        // with a completely sharp center and no dependence on weapon cadence.
        vec2 ray=(uv-0.5)*0.105*edge*distortion;
        vec3 streak=col;
        for(int i=1;i<12;i++) streak+=sceneAt(uv-ray*(float(i)/11.0));
        col=mix(col,streak/12.0,edge*0.86*strength);
    }
    else if(abilityMode==4 && distortion>0.0)
    {
        // A subtle optical veil: compact Gaussian blur, much softer than Rage.
        vec2 stepUV=vec2(0.0028*edge)*vec2(float(textureSize(InputTexture,0).y)/float(textureSize(InputTexture,0).x),1.0);
        float weights[5]=float[](1.0,4.0,6.0,4.0,1.0);
        vec3 soft=vec3(0.0);
        for(int y=-2;y<=2;y++) for(int x=-2;x<=2;x++)
            soft+=sceneAt(uv+vec2(x,y)*stepUV)*weights[x+2]*weights[y+2]/256.0;
        col=mix(col,soft,edge*0.72*strength);
    }
    float opacity=(0.10+0.38*pulse)*edge*strength;
    col=mix(col,signalColor,opacity);
    FragColor=vec4(col,1.0);
}
