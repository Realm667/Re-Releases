// Same bounded, camera-aligned distance estimate as underwater, at 8192 units.
float blurDepthCell(ivec2 cell)
{
 int i=clamp(cell.y,0,3)*8+clamp(cell.x,0,7), group=i/4;
 float encodedValue=group<4?depthA[group]:depthB[group-4];
 float q=mod(floor(encodedValue/exp2(float((i%4)*6))),64.0);
 return q*q*(8192.0/3969.0);
}
float blurDepth(vec2 uv)
{
 vec2 p=clamp((uv-viewRect.xy)/viewRect.zw,0.0,1.0)*vec2(8,4)-.5;
 ivec2 i=ivec2(floor(p)); vec2 f=fract(p);
 return mix(mix(blurDepthCell(i),blurDepthCell(i+ivec2(1,0)),f.x),
            mix(blurDepthCell(i+ivec2(0,1)),blurDepthCell(i+ivec2(1,1)),f.x),f.y);
}
void main()
{
 vec4 original=texture(InputTexture,TexCoord);
 if(any(lessThan(TexCoord,viewRect.xy)) || any(greaterThan(TexCoord,viewRect.xy+viewRect.zw)))
 { FragColor=original; return; }
 float amount=blurSettings.x*smoothstep(blurSettings.y,blurSettings.y+1280.0,blurDepth(TexCoord));
 if(amount<=0.0) { FragColor=original; return; }
 vec2 px=1.0/vec2(textureSize(InputTexture,0));
 float radius=6.0*amount;
 vec3 color=original.rgb*4.0; float weight=4.0;
 for(int y=-1;y<=1;y++)for(int x=-1;x<=1;x++)
 {
  if(x==0 && y==0)continue;
  vec2 uv=clamp(TexCoord+vec2(x,y)*px*radius,viewRect.xy+px*.5,viewRect.xy+viewRect.zw-px*.5);
  vec3 sampleColor=texture(InputTexture,uv).rgb;
  // Preserve strong silhouettes as in the underwater filter.
  float w=exp(-dot(sampleColor-original.rgb,sampleColor-original.rgb)*5.0);
  color+=sampleColor*w; weight+=w;
 }
 FragColor=vec4(color/weight,original.a);
}
