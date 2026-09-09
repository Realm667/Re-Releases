// One bounded pass before bloom/HUD: only the outer 18% of the view is affected.
vec3 sceneAt(vec2 uv)
{
    vec2 halfPixel=0.5/vec2(textureSize(InputTexture,0));
    return texture(InputTexture,clamp(uv,halfPixel,1.0-halfPixel)).rgb;
}

vec3 armor(vec2 uv,vec3 scene)
{
    // Use the exact metal artwork shared by the objective and ability plaques.
    // Sample its unadorned center; bevels and rivets follow their bronze palette.
    vec2 size=vec2(textureSize(InputTexture,0));
    vec2 extent=vec2(size.x/size.y*540.0,540.0);
    vec2 p=floor(uv*extent)+0.5;
    vec2 b=min(p,extent-p);
    float cut=min(min(b.x-22.0,b.y-24.0),(b.x+b.y-92.0)*0.707107);
    if(cut>=5.0) return scene;
    vec2 texUV=(vec2(60.0,193.0)+mod(p*2.0,vec2(1550.0,697.0)))/vec2(1672.0,941.0);
    vec3 metal=texture(armorTexture,texUV).rgb*1.75+vec3(0.025,0.022,0.018);
    bool horizontal=b.y<b.x;
    float along=horizontal?p.x:p.y;
    float sideLength=horizontal?extent.x:extent.y;
    float panel=sideLength/max(1.0,floor(sideLength/115.0));
    float seam=abs(mod(along+panel*0.5,panel)-panel*0.5);
    if(seam<1.0) metal*=0.24;
    else if(seam<2.0) metal+=vec3(0.13,0.09,0.04);
    // Inset gasket, dark channel and two bevel faces around the view opening.
    if(cut>=0.0) metal=vec3(0.035,0.028,0.020)*(1.0-cut/6.0);
    else if(cut>-2.0) metal=vec3(0.62,0.46,0.27);
    else if(cut>-4.0) metal=vec3(0.22,0.16,0.09);
    else if(cut>-8.0) metal=mix(metal,vec3(0.30,0.24,0.16),0.55);
    float outer=min(b.x,b.y);
    if(outer<2.0) metal=vec3(0.20,0.15,0.09);
    else if(outer<3.0) metal=vec3(0.47,0.33,0.18);
    // Square-headed rivets set into round sockets, plus reinforced corner bolts.
    vec2 bolt=vec2(mod(along,panel)-panel*0.5,(horizontal?b.y:b.x)-10.0);
    if(b.x<52.0 && b.y<52.0) bolt=b-vec2(28.0);
    float radius=length(bolt);
    if(radius<5.0 && cut<-5.0)
    {
        metal=vec3(0.08,0.06,0.04);
        if(max(abs(bolt.x),abs(bolt.y))<2.8)
            metal=bolt.x+bolt.y<0.0?vec3(0.66,0.50,0.28):vec3(0.30,0.21,0.12);
        if(abs(bolt.y)<0.6 && abs(bolt.x)<2.0) metal*=0.3;
    }
    return mix(scene,metal,strength*(1.0-smoothstep(3.0,5.0,cut)));
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
