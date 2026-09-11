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
// Integer lattice hashing stays identical on both sides of a noise cell edge.
float hash(vec2 p) {
 uvec2 q=uvec2(ivec2(floor(p)));uint h=q.x*1664525u+q.y*1013904223u;
 h^=h>>16u;h*=2246822519u;h^=h>>13u;
 return float(h&16777215u)/16777216.0;
}
float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+1.0),f.x),f.y);}
// A single final-pass warm bloom/haze treatment, confined to the heat mask.
// Warm bright pixels contribute glow; dim scenery only receives a trace of haze.
float lavaLuminance(vec3 color) {
 float warm=smoothstep(.04,.22,color.r-color.b)*smoothstep(.02,.16,color.r-color.g*.75);
 return warm*smoothstep(.10,.65,max(color.r,max(color.g,color.b)))*min(2.0,dot(color,vec3(.5,.4,.1)));
}
vec3 finishLava(vec3 color,float mask) {
 vec2 pixel=1.0/vec2(textureSize(InputTexture,0));
 float glow=lavaLuminance(texture(InputTexture,TexCoord).rgb)*.4;
 glow+=lavaLuminance(texture(InputTexture,clamp(TexCoord+pixel*vec2(4,4),0.0,1.0)).rgb)*.15;
 glow+=lavaLuminance(texture(InputTexture,clamp(TexCoord+pixel*vec2(-4,4),0.0,1.0)).rgb)*.15;
 glow+=lavaLuminance(texture(InputTexture,clamp(TexCoord+pixel*vec2(4,-4),0.0,1.0)).rgb)*.15;
 glow+=lavaLuminance(texture(InputTexture,clamp(TexCoord+pixel*vec2(-4,-4),0.0,1.0)).rgb)*.15;
 return color+mask*(vec3(1.0,.44,.12)*glow*.09+vec3(.018,.007,.0015));
}
void main() {
 if(sourceDelta.w<=0.0) {
  FragColor=texture(InputTexture,TexCoord);
  if(sourceRadius.w<.5)FragColor.a=0.0;
  if(sourceRadius.w>4.5){FragColor.rgb=finishLava(FragColor.rgb,FragColor.a);FragColor.a=1.0;}
  return;
 }
 vec3 radius=abs(sourceRadius.xyz);
 vec3 ray=envRay(TexCoord),rd=ray/radius,origin=-sourceDelta.xyz/radius;
 float b=dot(origin,rd),a=dot(rd,rd),c=dot(origin,origin)-1.0,disc=b*b-a*c;
 float strength=0.0;
 if(disc>0.0) {
  float nearHit=max(0.0,(-b-sqrt(disc))/a),farHit=(-b+sqrt(disc))/a;
  // Conservative nearest cell clips the plume at foreground geometry.
  vec2 grid=clamp((TexCoord-viewRect.xy)/viewRect.zw,0.0,1.0)*vec2(8,4)-.5;
  ivec2 cell=ivec2(floor(grid));
  float depth=min(min(envDepthCell(cell),envDepthCell(cell+ivec2(1,0))),min(envDepthCell(cell+ivec2(0,1)),envDepthCell(cell+ivec2(1,1))));
  float thickness=max(0.0,min(farHit,depth-4.0)-nearHit);
  strength=smoothstep(0.0,35.0,thickness);
 }
 vec2 p=TexCoord*vec2(textureSize(InputTexture,0))/55.0;
 float t=InputTimeGame*.7;
 vec2 turbulence=vec2(noise(p+vec2(t,-t*2.1)),noise(p*1.63+vec2(-t*.4,-t*1.8)))-.5;
 // Carry the strongest mask through consecutive RGBA16F passes.
 // Overlapping plumes must not multiply the approved distortion amplitude.
 float previous=sourceRadius.w<.5?0.0:texture(InputTexture,TexCoord).a;
 float combined=max(previous,strength*sourceDelta.w);
 vec2 shift=turbulence*7.0*(combined-previous)/vec2(textureSize(InputTexture,0));
 FragColor=texture(InputTexture,clamp(TexCoord+shift,0.0,1.0));
 if(sourceRadius.w>4.5)FragColor.rgb=finishLava(FragColor.rgb,combined);
 FragColor.a=sourceRadius.w>4.5?1.0:combined;

}
