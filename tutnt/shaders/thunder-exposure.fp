void main()
{
 vec4 c=texture(InputTexture,TexCoord);
 // Scene pass leaves the HUD intact. Local roof trace gates the brief near-flash lift.
 vec3 lift=c.rgb*(1.0+amount*.65)+vec3(.16,.16,.155)*amount*amount;
 FragColor=vec4(clamp(lift,0.0,1.0),c.a);
}
