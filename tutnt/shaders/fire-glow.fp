// Analytic soft halo: no visible texture contour and no additional bitmap.
vec4 ProcessTexel()
{
    vec2 p=(vTexCoord.st-0.5)*2.0;
    float r2=dot(p,p);
    float edge=1.0-smoothstep(0.65,1.0,sqrt(r2));
    float halo=exp(-r2*4.2)*0.52;
    float core=exp(-r2*23.0)*0.80;
    vec3 outer=vec3(1.0,0.32,0.035);
    vec3 inner=vec3(1.0,0.88,0.42);
#if GLOW_COLOR == 1
    outer=vec3(0.16,0.85,0.035); inner=vec3(0.60,1.0,0.28);
#elif GLOW_COLOR == 2
    outer=vec3(0.025,0.28,1.0); inner=vec3(0.30,0.78,1.0);
#endif
    return vec4((outer*halo+inner*core)*edge,1.0);
}
