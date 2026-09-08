// A readable hot core; the old tiny core disappeared at ordinary play distances.
vec4 Process(vec4 color)
{
    vec2 p=vTexCoord.st*2.0-1.0;
    float r=length(p);
    float core=exp(-r*r*22.0);
    float glow=exp(-r*r*5.5)*(1.0-smoothstep(.65,1.0,r));
    return vec4(vec3(1.0,.10,.009)*glow+vec3(.45,.7,.28)*core,glow)*color;
}
