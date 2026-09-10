vec4 ProcessTexel()
{
 vec2 uv=vTexCoord.st;
 float cone=mix(.12,.48,uv.y);
 float edge=1.0-smoothstep(cone*.5,cone,abs(uv.x-.5));
 float ends=smoothstep(0.0,.08,uv.y)*(1.0-smoothstep(.60,1.0,uv.y));
 float mote=.92+.08*sin(uv.y*34.0-timer*.5+sin(uv.x*29.0));
 return vec4(.68,.75,.82,edge*ends*mote*.07);
}
