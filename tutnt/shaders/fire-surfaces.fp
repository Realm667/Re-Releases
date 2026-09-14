// Crossfade all three native frames while the UV field rises and curls.
vec4 FireFrame(int frame,vec2 uv) {
 if(frame==0)return texture(fireFrame0,fract(uv));
 if(frame==1)return texture(fireFrame1,fract(uv));
 return texture(fireFrame2,fract(uv));
}
void SetupMaterial(inout Material mat) {
 vec2 uv=vTexCoord.st;
 SetMaterialProps(mat,uv);
 float t=timer;
 vec2 bend=vec2(sin(uv.y*15.0+t*2.1)+.45*sin(uv.y*31.0-t*1.3),
                .4*sin(uv.x*18.0+t*1.7))*.018;
 vec2 flow=uv+bend+vec2(0.0,t*.055);
 float stepTime=t*4.375;
 int frame=int(mod(floor(stepTime),3.0));
 float blend=smoothstep(0.0,1.0,fract(stepTime));
 vec4 flame=mix(FireFrame(frame,flow),FireFrame((frame+1)%3,flow),blend);
 flame.rgb*=.94+.06*sin(t*3.2+uv.y*8.0);
 mat.Base=flame;
 float hot=smoothstep(.12,.65,max(flame.r,max(flame.g,flame.b)));
 mat.Glow=vec4(flame.rgb,hot*.8);
}
