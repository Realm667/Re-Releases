// Shared world projection removes UV discontinuities at wall/model joins.
void SetupMaterial(inout Material mat)
{
    vec3 n=normalize(vWorldNormal.xyz);
    vec3 w=pow(abs(n),vec3(6.));w/=max(dot(w,vec3(1.)),.001);
    vec3 p=pixelpos.xyz;
    // Twice the original feature size; broad distortion breaks straight repeats.
    p+=18.*sin(p.yzx/311.)+11.*sin(p.zxy/173.);
    p/=1024.;
    vec2 ux=p.zy,uy=p.xz,uz=p.xy;
    mat.Base=getTexel(ux)*w.x+getTexel(uy)*w.y+getTexel(uz)*w.z;
    vec3 nx=texture(rockNormal,ux).xyz*2.-1.;
    vec3 ny=texture(rockNormal,uy).xyz*2.-1.;
    vec3 nz=texture(rockNormal,uz).xyz*2.-1.;
    vec3 detail=vec3(0.,-nx.y,nx.x)*w.x+vec3(ny.x,0.,-ny.y)*w.y+vec3(nz.x,-nz.y,0.)*w.z;
    mat.Normal=normalize(n+detail*.48);
    vec3 light=normalize(vec3(.48,.76,-.44));
    float base=.5+.5*max(dot(n,light),0.);
    float bump=.5+.5*max(dot(mat.Normal,light),0.);
    mat.Base.rgb*=clamp(bump/base,.65,1.3);
    mat.Specular=vec3(0.);mat.SpecularLevel=0.;
}
