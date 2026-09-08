vec4 ProcessTexel() {
 vec2 uv=vTexCoord.st;
 vec2 q=clamp(uv+vec2(sin(uv.y*15.0+timer*.63),sin(uv.x*17.0-timer*.49))*.009,.008,.992);
 float d=dot(getTexel(q).rgb,vec3(.333333));
 float edge=smoothstep(0.,.15,min(min(uv.x,uv.y),min(1.-uv.x,1.-uv.y)));
 return vec4(vec3(0.8),smoothstep(.008,.40,d)*edge);
}