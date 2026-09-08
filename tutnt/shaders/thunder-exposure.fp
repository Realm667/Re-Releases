void main()
{
 vec4 c=texture(InputTexture,TexCoord);
 // Scene pass leaves the HUD intact. Local roof trace gates this subtle lift.
 vec3 lift=c.rgb*(1.0+amount*.18)+vec3(.012,.018,.030)*amount;
 FragColor=vec4(clamp(lift,0.0,1.0),c.a);
}
