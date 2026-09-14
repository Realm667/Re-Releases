// A short outward refraction wave and warm exposure pulse at machine failure.
void main() {
 vec2 uv=TexCoord;
 float aspect=float(textureSize(InputTexture,0).x)/float(textureSize(InputTexture,0).y);
 vec2 metric=vec2(aspect,1.0),d=(uv-focus)*metric;
 float r=length(d),a=age-210.0;
 float charge=smoothstep(35.0,105.0,age)*(1.0-smoothstep(160.0,210.0,age));
 vec2 shift=vec2(sin(uv.y*40.0+age*.5),cos(uv.x*35.0-age*.4))*.0015*charge;
 float ring=exp(-pow((r-a*.032)/.075,2.0))*step(0.0,a)*(1.0-smoothstep(24.0,50.0,a));
 shift+=d/max(r,.001)/metric*ring*.045;
 float edge=smoothstep(0.0,.025,min(min(uv.x,uv.y),min(1.0-uv.x,1.0-uv.y)));
 shift*=strength*edge;
 vec2 p=clamp(uv+shift,vec2(.001),vec2(.999));
 vec3 c=texture(InputTexture,p).rgb;
 c.r=texture(InputTexture,clamp(p+shift*.12,vec2(.001),vec2(.999))).r;
 c.b=texture(InputTexture,clamp(p-shift*.12,vec2(.001),vec2(.999))).b;
 float flash=step(0.0,a)*exp(-max(a,0.0)/7.0)*.82;
 float echo=step(18.0,a)*exp(-max(a-18.0,0.0)/6.0)*.24;
 float pre=exp(-pow((age-105.0)/3.5,2.0))*.28;
 vec3 light=vec3(1.0,.72,.37)*(flash+echo+pre)*strength;
 c=1.0-(1.0-c)*(1.0-light);
 FragColor=vec4(c,1.0);
}
