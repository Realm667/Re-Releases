// Procedural, locally animated water surface; 9.44 and 2.0 are build constants.
float hash21(vec2 p) { return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
float noise2(vec2 p)
{
    vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);
    return mix(mix(hash21(i),hash21(i+vec2(1,0)),f.x),mix(hash21(i+vec2(0,1)),hash21(i+vec2(1,1)),f.x),f.y);
}
vec4 ProcessTexel()
{
    vec2 p=vTexCoord.st*2.0-1.0;
    float t=timer*2.7+9.44;
    float phase=2.0;
    float n=noise2(vec2(p.y*5.0-t,p.x*3.0+9.44));
    float center=0.12*sin(p.y*5.0+t)+0.05*sin(p.y*13.0-t*1.4);
    float width=phase<0.5 ? 0.32+0.13*n : phase<1.5 ? 0.23+0.16*n : 0.40;
    float x=abs(p.x-center);
    float mask=1.0-smoothstep(width*0.55,width,x);
    float ends=1.0-smoothstep(0.55,0.96,abs(p.y));
    if(phase>1.5) { mask=1.0-smoothstep(0.38,1.0,length(vec2((p.x-0.07*p.y)/0.48,p.y/0.80))); ends=1.0; }
    float breaks=phase<0.5 ? 0.85+0.15*n : phase<1.5 ? smoothstep(0.25,0.55,n) : 1.0;
    float grain=noise2(vec2(p.x*14.0+9.44,p.y*18.0-t*3.0));
    float rim=smoothstep(width*0.30,width*0.72,x)*(1.0-smoothstep(width*0.72,width,x));
    float glint=pow(max(0.0,sin(p.y*17.0-t*6.0+grain*4.0)),12.0)*0.20;
    vec3 col=mix(vec3(0.35,0.41,0.46),vec3(0.82,0.86,0.88),clamp(rim*0.70+grain*0.30+glint,0.0,1.0));
    float alpha=mask*ends*breaks*(0.65+0.35*grain);
    return vec4(col,alpha);
}
