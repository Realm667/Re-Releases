// Soft, uneven mist at authored island undersides; top edges remain clear.
float HazeHash(vec3 p) { p=fract(p*.1031);p+=dot(p,p.yzx+33.33);return fract((p.x+p.y)*p.z); }
float HazeNoise(vec3 p) {
 vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
 return mix(mix(mix(HazeHash(i),HazeHash(i+vec3(1,0,0)),f.x),mix(HazeHash(i+vec3(0,1,0)),HazeHash(i+vec3(1,1,0)),f.x),f.y),mix(mix(HazeHash(i+vec3(0,0,1)),HazeHash(i+vec3(1,0,1)),f.x),mix(HazeHash(i+vec3(0,1,1)),HazeHash(i+vec3(1,1,1)),f.x),f.y),f.z);
}
void SetupMaterial(inout Material mat) {
 float v=vTexCoord.y;
 vec3 p=pixelpos.xyz/vec3(100.,64.,100.);p.y-=timer*.10;
 float n=.7*HazeNoise(p)+.3*HazeNoise(p*2.13+7.);
 float envelope=smoothstep(0.,.34,v)*(1.-smoothstep(.65,1.,v));
 vec3 color=mix(vec3(.32,.095,.018),vec3(.96,.35,.055),n*.65+v*.20);
 // Joined contours share their corners; turbulence is continuous in world space.
 mat.Base=vec4(color,envelope*smoothstep(.12,.82,n)*.65);
 mat.Normal=normalize(vWorldNormal.xyz);
}
