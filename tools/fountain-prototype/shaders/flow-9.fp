vec4 ProcessTexel()
{
    vec2 p=vTexCoord.st*2.0-1.0;
    float core=exp(-p.x*p.x*24.0)*(1.0-smoothstep(0.3,0.9,abs(p.y)));
    return vec4(0.32,0.40,0.45,core*(1.0-smoothstep(-0.5,0.8,p.y))*0.65);
}
