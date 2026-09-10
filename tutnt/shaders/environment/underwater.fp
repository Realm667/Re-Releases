void main()
{
 vec3 color=texture(InputTexture,TexCoord).rgb;
 float d=clamp(waterDensity,0.0,.38);
 // A camera medium treatment, not false depth reconstruction or sun caustics.
 vec3 filtered=color*mix(vec3(1.0),waterTint,.22);
 filtered=mix(filtered,waterTint*.15,d);
 FragColor=vec4(filtered,1.0);
}
