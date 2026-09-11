// Warm hold then a slow 2.6-second fade, overlapping the gravitational pull.
vec3 AmberExposure(vec3 scene,float r,float age)
{
 if(age>=140.0)return scene;
 float swell=smoothstep(1.0,14.0,age)*(1.0-smoothstep(49.0,140.0,age))*amount;
 // Let the singularity turn black while the surrounding view retains its glow.
 swell*=1.0-smoothstep(65.0,95.0,age)*(1.0-smoothstep(.35,.72,r));
 float halo=exp(-r*r*.65),heart=exp(-r*r*3.0);
 vec3 veil=(vec3(1.0,.38,.055)*(.20+.46*halo)+vec3(1.0,.78,.32)*heart*.12)*swell;
 return 1.0-(1.0-scene)*(1.0-veil);
}
// Saved-clock gravitational pull followed by one outward refraction front.
void main()
{
 vec2 uv=TexCoord;
 if(ending>0.0)
 {
  vec3 scene=texture(InputTexture,uv).rgb;
  float luminance=clamp(dot(scene,vec3(.2126,.7152,.0722)),0.0,1.0);
  // Shadows disappear first; flames and bright energy persist into the last half.
  float finish=.72+.28*sqrt(luminance);
  float keep=1.0-smoothstep(0.0,finish,ending);
  FragColor=vec4(scene*keep,1.0);return;
 }
 float aspect=float(textureSize(InputTexture,0).x)/float(textureSize(InputTexture,0).y);
 vec2 metric=vec2(aspect,1.0),delta=(uv-focus)*metric;
 float r=length(delta)/max(radius,.001);
 float age=35.0+progress*175.0;
 if(age<70.0 || r>=1.8)
 {FragColor=vec4(AmberExposure(texture(InputTexture,uv).rgb,r,age),1.0);return;}
 vec2 direction=delta/max(length(delta),.001);
 float pull=clamp((age-70.0)/88.0,0.0,1.0);
 float edge=min(min(uv.x,1.0-uv.x),min(uv.y,1.0-uv.y));
 float fade=smoothstep(0.0,.04,edge)*(1.0-smoothstep(1.1,1.8,r));
 vec2 shift=vec2(0.0);
 if(age<158.0)
 {
  float gravity=pow(pull,1.4)*exp(-pow((r-.65)*1.4,2.0));
  // Sampling outward bends the scene inward; a small tangential component
  // reinforces orbital motion without rotating the player's camera.
  shift=(direction*.105+vec2(-direction.y,direction.x)*.032)*gravity*radius/metric;
 }
 else
 {
  float t=clamp((age-158.0)/35.0,0.0,1.0);
  float shell=exp(-pow((r-mix(.03,1.6,t))/.11,2.0));
  shift=direction/metric*shell*radius*.10*sin(t*3.14159265)*(1.0-t);
 }
 shift*=amount*fade;
 vec2 sampleUV=clamp(uv+shift,vec2(.001),vec2(.999));
 vec3 color=texture(InputTexture,sampleUV).rgb;
 color.r=texture(InputTexture,clamp(sampleUV+shift*.04,vec2(.001),vec2(.999))).r;
 color.b=texture(InputTexture,clamp(sampleUV-shift*.04,vec2(.001),vec2(.999))).b;
 FragColor=vec4(AmberExposure(color,r,age),1.0);
}
