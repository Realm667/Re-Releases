// Two separable Gaussian passes, before native weapon sprites are drawn.
// Alpha carries radial view distance, not a color-based guess about silhouettes.
void main()
{
 vec4 original=texture(InputTexture,TexCoord);
 float distance=original.a*original.a*16384.0;
 float amount=settings.x*smoothstep(settings.y,settings.y+1280.0,distance);
 bool finalPass=settings.w>0.0;
 vec2 uv=(TexCoord-viewRect.xy)/viewRect.zw;
 if(amount<=0.0 || any(lessThan(uv,vec2(0))) || any(greaterThan(uv,vec2(1))))
 { FragColor=vec4(original.rgb,finalPass?1.0:original.a);return; }
 vec2 px=1.0/vec2(textureSize(InputTexture,0));
 vec2 stepUV=settings.zw*px*(6.0*amount/4.0);
 vec3 color=original.rgb;float weight=1.0;
 for(int i=-4;i<=4;i++)
 {
  if(i==0)continue;
  vec2 pos=clamp(TexCoord+float(i)*stepUV,viewRect.xy+px*.5,viewRect.xy+viewRect.zw-px*.5);
  vec4 tap=texture(InputTexture,pos);
  float sampleDistance=tap.a*tap.a*16384.0;
  float edge=1.0-smoothstep(.12,.35,abs(sampleDistance-distance)/max(distance,64.0));
  float w=exp(-float(i*i)/8.0)*edge;
  color+=tap.rgb*w;weight+=w;
 }
 FragColor=vec4(color/weight,finalPass?1.0:original.a);
}
