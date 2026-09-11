// Per-face material extension. Metadata uses map X,Y,Z coordinates.
// Integer lattice hashing stays identical on both sides of a noise cell edge.
float envHash(vec2 p) {
 uvec2 q=uvec2(ivec2(floor(p)));uint h=q.x*1664525u+q.y*1013904223u;
 h^=h>>16u;h*=2246822519u;h^=h>>13u;
 return float(h&16777215u)/16777216.0;
}
float envNoise(vec2 p) {
 vec2 i=floor(p),f=fract(p); f=f*f*(3.0-2.0*f);
 return mix(mix(envHash(i),envHash(i+vec2(1,0)),f.x),mix(envHash(i+vec2(0,1)),envHash(i+1.0),f.x),f.y);
}
float envData(int i) {
 vec3 b=floor(texelFetch(envMeta,ivec2(i,0),0).rgb*255.0+.5);
 return dot(b,vec3(65536.0,256.0,1.0));
}
// Canvas draw coordinates start at the top; raw GPU texelFetch starts at the bottom.
float envCell(int index) { return texelFetch(envState,ivec2(index%256,255-index/256),0).r; }
void SetupMaterial(inout Material mat) {
 mat.Base=getTexel(vTexCoord.st);mat.Normal=normalize(vWorldNormal.xyz);
 vec3 origin=vec3(envData(3),envData(4),envData(5))/16.0-65536.0;
 vec3 axis=vec3(envData(6),envData(7),envData(8))/32767.0-1.0;
 vec3 world=pixelpos.xzy,delta=world-origin;
 vec2 extent=vec2(envData(9),envData(10))/16.0;
 int kind=int(envData(11));
 vec2 uv=(kind==0?delta.xy:vec2(dot(delta,axis),delta.z))/max(extent,vec2(.001));
 if(any(lessThan(uv,vec2(-.002))) || any(greaterThan(uv,vec2(1.002))))return;
 ivec2 count=ivec2(envData(1),envData(2));
 ivec2 cell=clamp(ivec2(uv*vec2(count)),ivec2(0),count-1);
 int base=int(envData(0));
 vec2 grid=clamp(uv,0.0,1.0)*vec2(count)-.5;
 ivec2 lo=ivec2(floor(grid)),hi=lo+1;
 vec2 blend=fract(grid);blend=blend*blend*(3.0-2.0*blend);
 lo=clamp(lo,ivec2(0),count-1);hi=clamp(hi,ivec2(0),count-1);
 float amount=mix(mix(envCell(base+lo.x+lo.y*count.x),envCell(base+hi.x+lo.y*count.x),blend.x),mix(envCell(base+lo.x+hi.y*count.x),envCell(base+hi.x+hi.y*count.x),blend.x),blend.y);
 // The native mirror renders the actual map behind this translucent floor.
 // Native alpha differs from 1 by only 1/255, selecting the translucent pass.
 // The material supplies the visible weight; dry texels remain visually opaque.
 float mirror=texelFetch(envState,ivec2(base%256,255-base/256),0).g;
 if(amount<.001)return;
 vec2 p=(kind==0?world.xy:vec2(dot(world,axis),world.z));
 float patches=smoothstep(.40,.66,envNoise(p*.040+vec2(17.3,43.7))+envNoise(p*.093)*.14);
 vec3 view=normalize(uCameraPos.xyz-pixelpos.xyz);
 float fresnel=.45+.55*pow(1.0-abs(dot(normalize(vWorldNormal.xyz),view)),2.0);
 float reflection=clamp(amount/.65,0.0,1.0)*patches*fresnel*.16;
 if(mirror>0.0)mat.Base.a=1.0-reflection;
 mat.Base.rgb*=1.0-amount*.10;
}
