// Ash & Ember: temporally stabilized blur mask with broad world-distance ramps.
float cellBlur(ivec2 cell) {
 int i=clamp(cell.y,0,8)*16+clamp(cell.x,0,15);
 vec4 words[12]=vec4[12](blur0,blur1,blur2,blur3,blur4,blur5,blur6,blur7,blur8,blur9,blur10,blur11);
 float v=words[i/12][(i/3)%4];
 return mod(floor(v/exp2(float((i%3)*8))),256.0)/255.0;
}
float sceneBlur(vec2 uv) {
 vec2 p=clamp((uv-viewport.xy)/viewport.zw,0.0,1.0)*vec2(16,9)-.5;
 ivec2 a=ivec2(floor(p));vec2 f=fract(p);
 return mix(mix(cellBlur(a),cellBlur(a+ivec2(1,0)),f.x),mix(cellBlur(a+ivec2(0,1)),cellBlur(a+ivec2(1,1)),f.x),f.y);
}
vec3 readScene(vec2 uv) {
 // Explicit bilinear reconstruction also works with the game's nearest texture filter.
 vec2 size=vec2(textureSize(InputTexture,0));
 vec2 p=clamp(uv*size,viewport.xy*size+.5,(viewport.xy+viewport.zw)*size-.5)-.5;
 ivec2 a=ivec2(floor(p)),last=ivec2(size)-1;vec2 f=fract(p);
 return mix(mix(texelFetch(InputTexture,a,0).rgb,texelFetch(InputTexture,min(a+ivec2(1,0),last),0).rgb,f.x),
            mix(texelFetch(InputTexture,min(a+ivec2(0,1),last),0).rgb,texelFetch(InputTexture,min(a+ivec2(1,1),last),0).rgb,f.x),f.y);
}
void main() {
 vec3 original=texture(InputTexture,TexCoord).rgb;
 vec2 local=(TexCoord-viewport.xy)/viewport.zw;
 if(any(lessThan(local,vec2(0))) || any(greaterThan(local,vec2(1)))) {FragColor=vec4(original,1);return;}
 vec2 size=vec2(textureSize(InputTexture,0)),pixel=1.0/size;
 float circle=sceneBlur(TexCoord),radius=lookParams.x*circle*size.y*viewport.w/720.0;
 vec3 color=original*.5;float weight=.5;
 if(radius>.35) {
  // Fixed disk samples; no temporal feedback, camera-history ghosting or focus pumping.
  for(int i=0;i<32;i++) {
   float a=float(i)*2.39996323,r=sqrt((float(i)+.5)/32.0);
   vec2 uv=TexCoord+vec2(cos(a),sin(a))*r*radius*pixel;
   vec3 sampleColor=readScene(uv);
   // Color-independent weights avoid sharp bright cores punching through the blur.
   float w=(1.0-.65*r*r)*mix(.35,1.0,smoothstep(.0,.4,sceneBlur(uv)));
   color+=sampleColor*w;weight+=w;
  }
 }
 color=mix(original,color/weight,smoothstep(.35,1.35,radius));
 vec3 glow=vec3(0);
 for(int i=0;i<8;i++) {
  float a=float(i)*.78539816;
  vec3 s=readScene(TexCoord+vec2(cos(a),sin(a))*pixel*(5.0+circle*4.0)*size.y/720.0);
  float warm=smoothstep(.05,.25,s.r-max(s.g*.9,s.b*1.15));
  glow+=s*smoothstep(.48,.95,max(s.r,max(s.g,s.b)))*warm;
 }
 float peak=max(color.r,max(color.g,color.b));
 float warm=smoothstep(.10,.55,(color.r-max(color.g*.95,color.b*1.15))/max(.02,peak))*smoothstep(.025,.30,peak);
 color=pow(max(color,vec3(0)),vec3(.91))*1.14;
 float luma=dot(color,vec3(.2126,.7152,.0722));
 color=mix(vec3(luma),color,.52+.46*warm);
 color*=mix(vec3(.94,.975,1.01),vec3(1.025,1.0,.97),warm);
 // A soft shoulder retains hue and detail in the bright flame, rather than clipping.
 color=color*1.18/(1.0+color*.18);
 color+=glow*.018;
 // A restrained amber veiling glare follows only the authored post-credit pulse.
 vec2 flare=(local-sparkAccent.xy)*vec2(sparkAccent.w,1.0);
 float veil=.014+.055*exp(-dot(flare,flare)*5.0)+.035*exp(-abs(flare.y)*110.0-abs(flare.x)*7.0);
 color+=vec3(1.0,.39,.08)*sparkAccent.z*veil;
 float vignette=1.0-.14*smoothstep(.15,.70,dot(local-.5,local-.5));
 color*=vignette;
 float grain=fract(sin(dot(gl_FragCoord.xy+lookParams.y,vec2(12.9898,78.233)))*43758.5453)-.5;
 color+=grain*.003*clamp(luma*4.0,0.0,1.0);
 FragColor=vec4(mix(original,clamp(color,0.0,1.0),lookParams.z),1.0);
}
