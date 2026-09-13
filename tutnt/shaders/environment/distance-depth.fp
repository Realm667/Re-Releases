// Assemble a dense distance mask in alpha without modifying scene RGB.
float cellDistance(ivec2 cell)
{
 int i=clamp(cell.y,0,2)*24+clamp(cell.x,0,23), packedIndex=i/3;
 vec4 group=packedIndex<4?depth0:packedIndex<8?depth1:packedIndex<12?depth2:packedIndex<16?depth3:packedIndex<20?depth4:depth5;
 float q=mod(floor(group[packedIndex%4]/exp2(float((i%3)*8))),256.0);
 return max(q*q*(16384.0/65025.0),1.0);
}
float axialDistance(ivec2 cell)
{
 vec2 uv=vec2(cell.x/23.0,(cell.y+settings.x*2.0)/18.0);
 vec2 slope=(uv*2.0-1.0)*settings.zw;
 return cellDistance(cell)*inversesqrt(1.0+dot(slope,slope));
}
void main()
{
 vec4 original=texture(InputTexture,TexCoord);
 vec2 uv=(TexCoord-viewRect.xy)/viewRect.zw;
 if(any(lessThan(uv,vec2(0))) || any(greaterThan(uv,vec2(1))))
 { FragColor=vec4(original.rgb,0.0); return; }
 float row=uv.y*18.0-settings.x*2.0;
 if(row<0.0 || row>2.0) { FragColor=original; return; }
 vec2 p=vec2(uv.x*23.0,row);
 ivec2 i=min(ivec2(floor(p)),ivec2(22,1));vec2 f=p-vec2(i);
 vec4 d=vec4(axialDistance(i),axialDistance(i+ivec2(1,0)),axialDistance(i+ivec2(0,1)),axialDistance(i+ivec2(1,1)));
 float low=min(min(d.x,d.y),min(d.z,d.w)),high=max(max(d.x,d.y),max(d.z,d.w));
 // Perspective-correct on planar geometry. Use color guidance at major depth edges.
 float z;
 if(high>low*1.75)
 {
  // Joint color/depth upsampling: a coarse actor hit must not leave a sharp
  // rectangle on the distant wall behind its silhouette.
  float weighted=0.0,total=0.0;
  for(int n=0;n<4;n++)
  {
   vec2 corner=vec2(n%2,n/2);
   vec2 node=(vec2(i)+corner+vec2(0,settings.x*2.0))/vec2(23,18);
   vec3 reference=texture(InputTexture,viewRect.xy+node*viewRect.zw).rgb;
   vec3 delta=reference-original.rgb;
   float cost=dot(delta,delta)/(0.04+dot(original.rgb,original.rgb))
             +.025*dot(f-corner,f-corner);
   float weight=exp(-32.0*cost);
   weighted+=d[n]*weight;total+=weight;
  }
  z=total>1e-8?weighted/total:high;
 }
 else
  z=1.0/mix(mix(1.0/d.x,1.0/d.y,f.x),mix(1.0/d.z,1.0/d.w,f.x),f.y);
 vec2 slope=(uv*2.0-1.0)*settings.zw;
 float distance=min(z*sqrt(1.0+dot(slope,slope)),16384.0);
 FragColor=vec4(original.rgb,sqrt(distance/16384.0));
}
