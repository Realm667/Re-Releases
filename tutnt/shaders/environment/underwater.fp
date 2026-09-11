vec3 envRay(vec2 uv) {
 return normalize(rayForward+rayRight*uv.x+rayUp*uv.y);
}
float envDepthCell(ivec2 cell) {
 int i=clamp(cell.y,0,3)*8+clamp(cell.x,0,7),group=i/4;
 float encodedValue=group<4?depthA[group]:depthB[group-4];
 float factor=exp2(float((i%4)*6));
 float q=mod(floor(encodedValue/factor),64.0);
 return q*q*(2048.0/3969.0);
}
float envDepth(vec2 uv) {
 vec2 p=clamp((uv-viewRect.xy)/viewRect.zw,0.0,1.0)*vec2(8,4)-.5;
 ivec2 i=ivec2(floor(p));vec2 f=fract(p);
 return mix(mix(envDepthCell(i),envDepthCell(i+ivec2(1,0)),f.x),mix(envDepthCell(i+ivec2(0,1)),envDepthCell(i+ivec2(1,1)),f.x),f.y);
}
void main() {
 vec2 px=1.0/vec2(textureSize(InputTexture,0));
 float distance=envDepth(TexCoord);
 float radius=.65+3.8*smoothstep(48.0,384.0,distance)+1.4*smoothstep(384.0,1024.0,distance);
 vec3 center=texture(InputTexture,TexCoord).rgb,color=center*4.0;float weight=4.0;
 for(int y=-1;y<=1;y++)for(int x=-1;x<=1;x++) {
  if(x==0 && y==0)continue;
  vec3 sampleColor=texture(InputTexture,clamp(TexCoord+vec2(x,y)*px*radius,vec2(0),vec2(1))).rgb;
  // Keep strong foreground silhouettes from smearing into their background.
  float w=exp(-dot(sampleColor-center,sampleColor-center)*5.0);
  color+=sampleColor*w;weight+=w;
 }
 color/=weight;
 float d=clamp(waterDensity+distance/18000.0,0.0,.22);
 vec3 filtered=color*mix(vec3(1.0),waterTint,.15);
 FragColor=vec4(mix(filtered,waterTint*.15,d),1.0);
}
