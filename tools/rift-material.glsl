// Dark cloud ceiling anchored to the real TNT04CN beam endpoint.
// The beam itself is level geometry; no beam is drawn by this material.
vec4 RiftKey(vec4 c)
{
 c.a=1.0-smoothstep(.03,.18,c.b-max(c.r,c.g));
 c.b=min(c.b,max(c.r,c.g));c.rgb*=c.a;return c;
}
vec4 RiftSample(sampler2D layer,vec2 uv,bool key)
{
 vec2 sz=vec2(textureSize(layer,0)),d=1.0/sz;
 vec2 p=uv*sz-.5,f=fract(p),b=(floor(p)+.5)/sz;
 vec2 lo=clamp(b,d*.5,1.0-d*.5),hi=clamp(b+d,d*.5,1.0-d*.5);
 vec4 a=texture(layer,lo),c=texture(layer,vec2(hi.x,lo.y));
 vec4 e=texture(layer,vec2(lo.x,hi.y)),g=texture(layer,hi);
 if(key){a=RiftKey(a);c=RiftKey(c);e=RiftKey(e);g=RiftKey(g);}
 return mix(mix(a,c,f.x),mix(e,g,f.x),f.y);
}
vec3 RiftWrap(vec2 uv)
{
 uv=vec2(fract(uv.x),clamp(uv.y,0.0,1.0));
 float seam=.5*(1.0-smoothstep(0.0,.035,min(uv.x,1.0-uv.x)));
 return mix(RiftSample(surroundmap,uv,false).rgb,RiftSample(surroundmap,vec2(1.0-uv.x,uv.y),false).rgb,seam);
}
vec3 RiftSurround(vec3 ray)
{
 float lon=atan(-ray.z,-ray.x),lat=asin(clamp(ray.y,-1.0,1.0));
 vec3 color=RiftWrap(vec2(lon/6.283185307+.5+timer*.000035,.60-lat/3.141592654*.90));
 float cap=smoothstep(.55,.85,ray.y);
 color=mix(color,RiftWrap(vec2(.5+ray.x*.25,.25+ray.z*.25)),cap);
 return color*.85*smoothstep(-.30,.35,ray.y);
}
vec4 RiftRockLayer(vec4 behind,vec3 ray,vec3 cameraOffset,vec3 forward,vec3 right,vec3 up,
                   vec2 span,vec4 bounds,float light,float motion,float phase,float distance,float period)
{
 float depth=dot(ray,forward);
 float plane=distance-dot(cameraOffset,forward);
 if(depth<=.01 || plane<=0.0)return behind;
 // Intersect a fixed world-space card, giving nearby debris stronger parallax.
 vec3 hit=cameraOffset+ray*(plane/depth);
 vec2 p=vec2(dot(hit,right),-dot(hit,up))/(distance*span);
 // A true closed ellipse: quadrature at one frequency, opposite signed periods.
 float theta=timer*(6.283185307/period)+phase;
 p+=motion*vec2(-cos(theta),.65*sin(theta));
 float angle=.014*sin(timer*.023+phase),c=cos(angle),s=sin(angle);
 vec2 uv=vec2(c*p.x-s*p.y,s*p.x+c*p.y)+.5;
 float edge=min(min(uv.x,1.0-uv.x),min(uv.y,1.0-uv.y));
 if(edge<=0.0)return behind;
 vec4 rock=RiftSample(rockmap,mix(bounds.xy,bounds.zw,uv),true)*smoothstep(0.0,.025,edge);
 float luma=dot(rock.rgb,vec3(.2126,.7152,.0722));
 rock.rgb=mix(vec3(luma)*vec3(1.05,.94,.82),rock.rgb,.25)*light*smoothstep(-.25,.30,ray.y);
 return behind*(1.0-rock.a)+rock;
}
void SetupMaterial(inout Material mat)
{
 float s=1.0-2.0*vTexCoord.x,t=1.0-2.0*vTexCoord.y;
 vec3 ray=normalize(@RAY@);
 vec3 color=RiftSurround(ray);
 // Renderer coordinates are (world X, world Z, world Y).
 // The visible upper T4_BM2 cylinder is in the stacked room at (10624,-192).
 // Its ceiling is 20000. Sector portal 1000/1001 translates by (10496,128,0).
 // Undo that translation so both portal passes sample one continuous ceiling.
 vec3 eye=uCameraPos.xyz;
 if(eye.x>6000.0)eye.xz-=vec2(10496.0,128.0);
 float distanceToCeiling=(20000.0-eye.y)/max(ray.y,.001);
 vec2 ceilingPoint=eye.xz-ray.xz*distanceToCeiling;
 vec2 uv=vec2(.5,.425)+(ceilingPoint-vec2(128.0,-320.0))/30000.0;
 float edge=min(min(uv.x,1.0-uv.x),min(uv.y,1.0-uv.y));
 float weight=smoothstep(0.0,.13,edge)*smoothstep(.015,.10,ray.y)*step(0.0,distanceToCeiling);
 if(weight>0.0)
 {
  // The hole stays fixed over the beam. Only distant cloud detail drifts slightly.
  vec2 offset=uv-vec2(.5,.425);
  float moving=smoothstep(.12,.28,length(offset));
  vec2 drift=.0015*moving*vec2(sin(timer*.024+uv.y*7.0),sin(timer*.017+uv.x*8.0));
  vec3 clouds=RiftSample(nebulamap,uv+drift,false).rgb;
  color=mix(color,clouds,weight);
 }
 // Seven independent fields: original debris, three mountains, three clusters.
 vec4 rocks=vec4(0.0);
 // Same portal-normalized eye as the cloud ceiling, in the sky ray's axes.
 vec3 rockEye=vec3(-eye.x,eye.y,-eye.z)-vec3(-128.0,3241.0,320.0);
@ROCKS@
 // Keep the opening's central beam endpoint unobstructed, through both portals.
 rocks*=smoothstep(.15,.23,length(uv-vec2(.5,.425)));
 color=WarComets(color,ray);
 color=color*(1.0-rocks.a)+rocks.rgb;
 mat.Base=vec4(color,1.0);mat.Normal=normalize(vWorldNormal.xyz);
}
