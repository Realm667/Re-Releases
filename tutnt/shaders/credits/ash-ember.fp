// Approved mockup 03. Linear plane-depth DOF, ash grade, warm halation, fine grain.
float cellDepth(ivec2 cell) {
 int i=clamp(cell.y,0,8)*16+clamp(cell.x,0,15);
 vec4 depthWords[9]=vec4[9](depth0,depth1,depth2,depth3,depth4,depth5,depth6,depth7,depth8);
 float v=depthWords[i/16][(i/4)%4];
 float q=mod(floor(v/exp2(float((i%4)*6))),64.0);
 return 8.0*exp2(q*(10.0/63.0));
}
float planeDepth(vec2 uv) {
 vec2 p=clamp((uv-viewport.xy)/viewport.zw,0.0,1.0)*vec2(16,9)-.5;
 ivec2 a=ivec2(floor(p));vec2 f=fract(p);
 return mix(mix(cellDepth(a),cellDepth(a+ivec2(1,0)),f.x),mix(cellDepth(a+ivec2(0,1)),cellDepth(a+ivec2(1,1)),f.x),f.y);
}
float coc(float z) {return smoothstep(.26,1.15,abs(z-focusDistance)/max(z,8.0));}
vec3 readScene(vec2 uv) {return texture(InputTexture,clamp(uv,viewport.xy,viewport.xy+viewport.zw)).rgb;}
void main() {
 vec3 original=texture(InputTexture,TexCoord).rgb;
 vec2 local=(TexCoord-viewport.xy)/viewport.zw;
 if(any(lessThan(local,vec2(0))) || any(greaterThan(local,vec2(1)))) {FragColor=vec4(original,1);return;}
 vec2 size=vec2(textureSize(InputTexture,0)),pixel=1.0/size;
 float circle=coc(planeDepth(TexCoord)),radius=aperture*circle*size.y*viewport.w/720.0;
 vec3 color=original;float weight=1.0;
 if(radius>.35) {
  // Fixed disk samples; no temporal feedback, camera-history ghosting or focus pumping.
  for(int i=0;i<24;i++) {
   float a=float(i)*2.39996323,r=sqrt((float(i)+.5)/24.0);
   vec2 uv=TexCoord+vec2(cos(a),sin(a))*r*radius*pixel;
   vec3 sampleColor=readScene(uv);
   // In-focus bright cores should not bleed out across their depth silhouettes.
   float w=mix(.12,1.0,smoothstep(.05,.5,coc(planeDepth(uv))))/(1.0+dot(sampleColor-original,sampleColor-original)*3.0);
   color+=sampleColor*w;weight+=w;
  }
 }
 color/=weight;
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
 float vignette=1.0-.14*smoothstep(.15,.70,dot(local-.5,local-.5));
 color*=vignette;
 float grain=fract(sin(dot(gl_FragCoord.xy+grainTime,vec2(12.9898,78.233)))*43758.5453)-.5;
 color+=grain*.003*clamp(luma*4.0,0.0,1.0);
 FragColor=vec4(mix(original,clamp(color,0.0,1.0),strength),1.0);
}
