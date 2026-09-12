// Per-display CRT treatment. Base art and housing remain untouched outside rectangles.
// Probe images are actual room views; they approximate a reflection from the glass.
float crtData(int x,int y) {
 vec3 c=floor(texelFetch(crtState,ivec2(x,3-y),0).rgb*255.0+.5);
 return dot(c,vec3(65536.,256.,1.));
}
vec3 crtVector(int x,int y) {
 return vec3(crtData(x,y),crtData(x+1,y),crtData(x+2,y))/16.-65536.;
}
vec3 crtBlur(sampler2D source,vec2 uv) {
 // Explicit bilinear samples keep the reflection soft with unfiltered pixel art.
 vec2 size=vec2(textureSize(source,0));
 vec3 sum=vec3(0.);
 for(int y=-1;y<=1;y++)for(int x=-1;x<=1;x++){
  vec2 p=clamp(uv+vec2(x,y)*.023,vec2(.03),vec2(.97))*size-.5;
  ivec2 a=ivec2(floor(p));vec2 f=fract(p);
  sum+=mix(mix(texelFetch(source,a,0).rgb,texelFetch(source,a+ivec2(1,0),0).rgb,f.x),
           mix(texelFetch(source,a+ivec2(0,1),0).rgb,texelFetch(source,a+ivec2(1,1),0).rgb,f.x),f.y);
 }
 return sum/9.;
}
// Convex faceplate in world units: the center protrudes, the rim stays seated.
float crtHeight(vec2 p,float depth) {
 vec2 k=max(vec2(0.),1.-p*p);
 return depth*k.x*k.y;
}
vec2 crtFaceplate(vec2 p,vec2 uv,vec2 fraction,vec3 n,vec3 view,out vec3 curved) {
 curved=n;
 vec2 dx=dFdx(uv),dy=dFdy(uv);
 vec3 px=dFdx(pixelpos.xyz),py=dFdy(pixelpos.xyz);
 float det=dx.x*dy.y-dx.y*dy.x;
 if(abs(det)<1e-12)return p;
 // Actual texture scale/rotation, including floor consoles and mirrored UVs.
 vec3 halfU=(px*dy.y-py*dx.y)/det*fraction.x*.5;
 vec3 halfV=(py*dx.x-px*dy.x)/det*fraction.y*.5;
 float width=length(halfU),height=length(halfV);
 if(min(width,height)<1e-4)return p;
 vec3 tangent=halfU/width,bitangent=halfV/height;
 float facing=dot(view,n);
 float fade=1.-smoothstep(320.,768.,distance(pixelpos.xyz,uCameraPos.xyz));
 float depth=CRT_BULGE*2.*min(width,height)*fade*smoothstep(.08,.22,facing);
 if(depth<1e-4)return p;
 vec2 ray=vec2(dot(view,tangent)/width,dot(view,bitangent)/height)/max(facing,.08);
 // Find the first intersection while tracing from the eye toward the base plane.
 float hi=depth,lo=0.;
 for(int i=1;i<=12;i++){
  float z=depth*(1.-float(i)/12.);
  if(z<=crtHeight(p+ray*z,depth)){lo=z;break;}
  hi=z;
 }
 for(int i=0;i<5;i++){
  float z=(lo+hi)*.5;
  if(z>crtHeight(p+ray*z,depth))hi=z;else lo=z;
 }
 vec2 hit=clamp(p+ray*((lo+hi)*.5),vec2(-1.),vec2(1.));
 vec2 gradient=-2.*depth*hit*(1.-hit.yx*hit.yx);
 curved=normalize(n-tangent*gradient.x/width-bitangent*gradient.y/height);
 return hit;
}
vec3 crtReflection(vec3 n,vec3 curved,vec3 view,float enabled) {
 if(enabled<.5)return vec3(0.);
 vec3 world=pixelpos.xzy;
 // Disable feedback inside either environment camera's own render.
 for(int i=0;i<2;i++)if(crtData(6,i)>0. && distance(uCameraPos.xzy,crtVector(0,i))<12.)return vec3(0.);
 int best=-1;float score=1e9;
 for(int i=0;i<2;i++){
  if(crtData(6,i)<1.)continue;
  vec3 origin=crtVector(0,i),forward=crtVector(3,i)/4096.;
  vec3 delta=world-origin;
  float plane=abs(dot(delta,forward)+4.);
  float d=length(delta);
  if(dot(n.xzy,forward)>.90 && plane<12. && d<256. && d<score){score=d;best=i;}
 }
 if(best<0)return vec3(0.);
 vec3 forward=normalize(crtVector(3,best)/4096.);
 vec3 right=abs(forward.z)>.9?vec3(0.,-1.,0.):normalize(vec3(forward.y,-forward.x,0.));
 vec3 up=normalize(cross(right,forward));
 vec3 ray=reflect(-view.xzy,curved.xzy);
 float facing=dot(ray,forward);
 if(facing<.15)return vec3(0.);
 vec2 uv=vec2(dot(ray,right),dot(ray,up))/(max(facing,.15)*3.4641016)+.5;
 float edge=1.-smoothstep(.43,.49,max(abs(uv.x-.5),abs(uv.y-.5)));
 if(edge<=0.)return vec3(0.);
 vec3 room=best==0?crtBlur(crtProbe0,uv):crtBlur(crtProbe1,uv);
 float fresnel=1.6*(.18+.12*pow(1.-clamp(dot(view,curved),0.,1.),2.));
 return room*edge*fresnel*(1.-smoothstep(160.,256.,score));
}
void SetupMaterial(inout Material mat) {
 vec2 uv=vTexCoord.st;
 SetMaterialProps(mat,uv);
 vec3 control=texelFetch(crtState,ivec2(0,0),0).rgb;
 if(control.r<.5)return;
 const vec2 pixels=CRT_SIZE;
 const vec4 boxes[3]=vec4[3](CRT_RECT0,CRT_RECT1,CRT_RECT2);
 vec2 texel=fract(uv)*pixels;
 vec4 box=vec4(0.);bool found=false;
 for(int i=0;i<CRT_COUNT;i++){
  vec4 b=boxes[i];
  if(all(greaterThanEqual(texel,b.xy)) && all(lessThan(texel,b.zw))){box=b;found=true;break;}
 }
 if(!found)return;
 vec2 size=box.zw-box.xy,local=(texel-box.xy)/size,glass=local*2.-1.;
 // Rounded glass mask and a quiet vignette, independently for each small display.
 vec2 q=abs(glass)-vec2(.91);
 float rounded=length(max(q,0.))-.09;
 float aa=max(max(fwidth(local.x),fwidth(local.y))*2.,.005);
 float mask=1.-smoothstep(-aa,aa,rounded);
 if(mask<=0.)return;
 vec3 n=normalize(vWorldNormal.xyz),view=normalize(uCameraPos.xyz-pixelpos.xyz),curved;
 vec2 face=crtFaceplate(glass,uv,size/pixels,n,view,curved);
 vec2 warped=face*(1.+.010*dot(face,face));
 vec2 samplePixel=clamp(box.xy+(warped*.5+.5)*size,box.xy+.5,box.zw-.5);
 vec2 coord=uv+(samplePixel-texel)/pixels;
 vec3 original=getTexel(coord).rgb;
 vec2 dx=vec2(1./pixels.x,0.),dy=vec2(0.,1./pixels.y);
 vec3 halo=(getTexel(coord+dx).rgb+getTexel(coord-dx).rgb+getTexel(coord+dy).rgb+getTexel(coord-dy).rgb)*.25;
 float distanceFade=1.-smoothstep(320.,768.,distance(pixelpos.xyz,uCameraPos.xyz));
 // Fade the frequency before it becomes undersampled, including oblique views.
 float line=(CRT_SCAN_X==1?samplePixel.x:samplePixel.y)*2.;
 float resolved=1.-smoothstep(.35,.8,fwidth(line));
 float phase=control.g>.5?timer*.22:0.;
 float scan=1.-.10*resolved*distanceFade*(.5+.5*cos(6.2831853*(line+phase)));
 float vignette=1.-.12*pow(max(abs(glass.x),abs(glass.y)),4.);
 float lit=CRT_LIT;
 float luminance=max(max(original.r,original.g),original.b);
 float gain=1.+lit*2.5*(1.-sqrt(clamp(luminance,0.,1.)));
 vec3 screen=(original*gain+halo*lit*.12)*scan*vignette;
 mat.Normal=normalize(mix(mat.Normal,curved,mask));
 vec3 reflected=crtReflection(n,curved,view,control.b)*distanceFade;
 reflected*=1.-clamp(max(max(screen.r,screen.g),screen.b)*.7,0.,.7);
 mat.Base.rgb=mix(mat.Base.rgb,screen+reflected,mask);
 // Native white glass brightmaps provide fullbright; retain the softer glow fallback.
 mat.Glow=vec4(screen+reflected,mask*(lit>.5?.68:.12));
}
