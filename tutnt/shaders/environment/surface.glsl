// Shared material extension; metadata stores one surface's world-space grid.
float envData(int i)
{
 vec3 b=floor(texelFetch(envMeta,ivec2(i,0),0).rgb*255.0+.5);
 return dot(b,vec3(65536.0,256.0,1.0));
}
float envCell(int index)
{ return texelFetch(envState,ivec2(index%256,index/256),0).r; }
void SetupMaterial(inout Material mat)
{
 ENV_ORIGINAL_BODY
 vec3 origin=vec3(envData(3),envData(4),envData(5))/16.0-65536.0;
 vec3 axis=vec3(envData(6),envData(7),envData(8))/32767.0-1.0;
 // Renderer coordinates are X,Z,Y; metadata uses map X,Y,Z.
 vec3 world=pixelpos.xzy;
 vec3 delta=world-origin;
 vec2 extent=vec2(envData(9),envData(10))/16.0;
 int kind=int(envData(11));
 vec2 uv=(kind==0?delta.xy:vec2(dot(delta,axis),delta.z))/max(extent,vec2(.001));
 if(any(lessThan(uv,vec2(0))) || any(greaterThan(uv,vec2(1))))return;
 ivec2 count=ivec2(envData(1),envData(2));
 // Nearest sampling prevents wet pixels bleeding through the edge of a roof.
 ivec2 cell=clamp(ivec2(uv*vec2(count)),ivec2(0),count-1);
 float amount=envCell(int(envData(0))+cell.x+cell.y*count.x);
 if(amount<.001)return;
 if(envData(13)>.5)
 {
  float waterZ=envData(12)/16.0-65536.0;
  if(world.z>waterZ)return;
  vec2 p=world.xy*.035+world.z*.006;
  float a=sin(p.x*1.7+sin(p.y+timer*.38))+sin(p.y*1.5-timer*.32);
  float b=sin(p.x*1.2-p.y*.8+timer*.27);
  float caustic=pow(max(0.0,1.0-abs(a+b)*1.6),5.0);
  float depth=clamp((waterZ-world.z)/256.0,0.0,1.0);
  mat.Base.rgb+=vec3(.055,.085,.085)*caustic*amount*(1.0-depth);
  return;
 }
 float metal=envData(14);
 mat.Base.rgb*=1.0-amount*mix(.16,.07,metal);
 vec3 n=normalize(mat.Normal);vec3 view=normalize(uCameraPos.xyz-pixelpos.xyz);
 float facing=pow(1.0-abs(dot(n,view)),3.0);
 // Restrained wet sheen; actual point-light response comes from material normals/specular.
 mat.Specular=mix(mat.Specular,vec3(.22+.22*metal),amount);
 mat.Glossiness=max(mat.Glossiness,mix(2.0,5.0,metal)*amount);
 mat.SpecularLevel=max(mat.SpecularLevel,.55*amount);
 mat.Base.rgb+=vec3(.012,.016,.019)*facing*amount;
}
