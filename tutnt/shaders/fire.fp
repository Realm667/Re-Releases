// Sprite-local pixel fire. Source pixels and alpha remain in the PNG; this
// shader bends the tongues, lifts ripples and derives the two spectral colors.
vec4 ProcessTexel()
{
    vec2 uv=vTexCoord.st;
    float h=1.0-uv.y;
    float phase=(pixelpos.x+pixelpos.z)*0.031;
    float t=timer*(FIRE_COLOR==2 ? 1.45 : FIRE_COLOR==1 ? 1.85 : 2.15)+phase;
    // Anchored at the bottom, increasingly turbulent toward the free tips.
    float bend=h*h;
    uv.x+=bend*(0.036*sin(t*2.0+h*8.0)+0.022*sin(t*3.7-h*15.0));
    uv.y+=bend*0.018*sin(t*2.8+h*12.0);
    // Match the original game sprites' texel density even at close range.
    uv=(floor(uv*vec2(48.0,80.0))+0.5)/vec2(48.0,80.0);
    if (uv.x<0.0 || uv.x>1.0 || uv.y<0.0 || uv.y>1.0) return vec4(0.0);
    vec4 c=getTexel(uv);
    c.a=smoothstep(0.22,0.72,c.a);
    // A thin break travels up the free tips and releases a short-lived wisp.
    float tear=0.63+fract(t*0.23)*0.55+0.035*sin(uv.x*24.0+t);
    c.a*=smoothstep(0.010,0.035,abs(h-tear));
    float heat=dot(c.rgb,vec3(0.24,0.66,0.10));
#if FIRE_COLOR == 1
    vec3 edge=vec3(0.025,0.24,0.045);
    vec3 mid=vec3(0.19,0.88,0.065);
    vec3 core=vec3(0.85,1.0,0.48);
    c.rgb=heat<0.55 ? mix(edge,mid,smoothstep(0.10,0.55,heat)) : mix(mid,core,smoothstep(0.55,0.93,heat));
#elif FIRE_COLOR == 2
    vec3 edge=vec3(0.018,0.065,0.40);
    vec3 mid=vec3(0.055,0.45,0.96);
    vec3 core=vec3(0.64,0.93,1.0);
    c.rgb=heat<0.55 ? mix(edge,mid,smoothstep(0.10,0.55,heat)) : mix(mid,core,smoothstep(0.55,0.93,heat));
#endif
    c.rgb*=0.96+0.04*sin(t*3.5+h*18.0);
    return c;
}
