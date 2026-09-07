// Black-backed fragment artwork is converted to translucent gas in the material.
// Particle motion/lifetime creates the fire; this only adds small internal flow.
vec4 ProcessTexel()
{
    vec2 uv=vTexCoord.st;
    float phase=(pixelpos.x+pixelpos.z)*0.019;
    float t=timer*(FIRE_COLOR==2 ? 1.3 : 1.9)+phase;
    uv.x+=0.012*sin(uv.y*17.0+t*2.0);
    uv.y+=0.008*sin(uv.x*13.0-t*2.7);
    if (uv.x<0.0 || uv.x>1.0 || uv.y<0.0 || uv.y>1.0) return vec4(0.0);
    // Integrate a few neighboring texels to avoid sparkly aliasing even when
    // the player uses nearest-neighbor filtering for the world textures.
    vec2 d=vec2(0.0032);
    vec4 c=getTexel(uv)*0.36;
    c+=(getTexel(uv+vec2(d.x,0.0))+getTexel(uv-vec2(d.x,0.0))
       +getTexel(uv+vec2(0.0,d.y))+getTexel(uv-vec2(0.0,d.y)))*0.16;
    float intensity=max(c.r,max(c.g,c.b));
    float heat=clamp(c.g/max(0.10,c.r),0.0,1.0);
    c.a*=(1.0-smoothstep(0.66,0.94,uv.y)); // Soften the sheet at birth, avoiding a straight cut.
    c.a*=smoothstep(0.012,0.40,intensity);
    c.rgb=c.rgb/max(0.25,intensity);
    c.rgb=mix(vec3(0.90,0.20,0.025),vec3(1.0,0.69,0.12),smoothstep(0.08,0.58,heat));
    c.rgb=mix(c.rgb,vec3(1.0,0.93,0.60),smoothstep(0.53,0.87,heat));
#if FIRE_COLOR == 1
    c.rgb=mix(vec3(0.07,0.58,0.08),vec3(0.66,1.0,0.40),heat*heat);
#elif FIRE_COLOR == 2
    c.rgb=mix(vec3(0.035,0.24,0.82),vec3(0.55,0.90,1.0),heat*heat);
#endif
    return c;
}
