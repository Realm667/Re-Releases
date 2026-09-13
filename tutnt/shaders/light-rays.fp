// Shared soft scattering. Model slices are weighted by facing, so their
// combined brightness stays stable as the player walks around the lamp.
float RayNumber(vec3 color)
{
    return dot(floor(color*255.+.5),vec3(65536.,256.,1.))/16.;
}
float RayGeometry(vec3 world,vec2 uv)
{
    // Recover the common attachment point from the authored UVs. This also
    // works for negative scale and rolled sheets without changing map actors.
    vec2 tx=dFdx(uv),ty=dFdy(uv);
    float determinant=tx.x*ty.y-tx.y*ty.x;
    if(abs(determinant)<1e-10)return 1.;
    vec3 dx=dFdx(world),dy=dFdy(world);
    vec3 du=(dx*ty.y-dy*tx.y)/determinant;
    vec3 dv=(dy*tx.x-dx*ty.x)/determinant;
    vec3 origin=world-du*(uv.x-.5)-dv*(uv.y-17./256.);
    for(int row=0;row<32;row++)
    {
        int line=31-row; // Canvas draw rows and GPU texel rows have opposite origins.
        vec3 state=texelFetch(rayData,ivec2(3,line),0).rgb;
        if(state.r<.5)break;
        vec3 source=vec3(RayNumber(texelFetch(rayData,ivec2(0,line),0).rgb),
                         RayNumber(texelFetch(rayData,ivec2(2,line),0).rgb),
                         RayNumber(texelFetch(rayData,ivec2(1,line),0).rgb))-65536.;
        if(length(origin-source)>2.)continue;
        vec3 axis=normalize((texelFetch(rayData,ivec2(4,line),0).rgb*2.-1.).xzy);
        float limit=RayNumber(texelFetch(rayData,ivec2(5,line),0).rgb);
        float remaining=limit-dot(world-source,axis);
        return mix(1.,smoothstep(0.,6.,remaining),state.g);
    }
    return 1.;
}
vec4 ProcessTexel()
{
    vec2 uv = vTexCoord.st;
    vec3 world = pixelpos.xyz;
    float phase = dot(world, vec3(.017, .009, .013));
    float flow = .92 + .14*sin(world.y*.22 + phase + timer*1.1)
                     + .07*sin(world.x*.16 - world.z*.14 - timer*.73);
    float alpha;
#if RAY_SHAPE == 0
    // The legacy alpha profile is authoritative for width, length and source
    // attachment. Do not grow the cone while replacing its representation.
    vec2 maskUV = uv;
#if RAY_VOLUME == 1
    // Radial slices compress their profile in projection. Compensate within
    // the original geometry envelope (RMS projected width = sqrt(3/4)).
    maskUV.x = .5+(uv.x-.5)*.8660254;
#endif
    alpha = getTexel(maskUV).a;
    alpha *= smoothstep(0.,.025,uv.x)*(1.-smoothstep(.975,1.,uv.x));
#else
    // Directed/rolled light sheets keep the authored mask and footprint.
    vec2 d = vec2(.004);
    alpha = getTexel(uv).a*.5;
    alpha += (getTexel(uv+vec2(d.x,0)).a + getTexel(uv-vec2(d.x,0)).a
            + getTexel(uv+vec2(0,d.y)).a + getTexel(uv-vec2(0,d.y)).a)*.125;
    alpha *= smoothstep(0.,.02,uv.y) * (1.-smoothstep(.98,1.,uv.y));
#endif
    vec3 eye = uCameraPos.xyz-world;
    // Per-fragment fade also works when the camera enters a large sheet.
    alpha *= smoothstep(4.,28.,length(eye));
    alpha *= RayGeometry(world,uv);
#if RAY_VOLUME == 1
    vec3 view = normalize(vec3(eye.x,0.,eye.z)+vec3(.00001,0.,0.));
    float facing = abs(dot(normalize(vWorldNormal.xyz),view));
    alpha *= facing*facing/6.; // twelve radial planes: sum(cos^2) = 6
    // Looking directly along a stack of slices must not reveal a radial star.
    alpha *= smoothstep(.025,.12,length(eye.xz)/max(length(eye),.001));
#else
    // Sheets disappear continuously at grazing angles, preserving their
    // front-facing footprint instead of exposing a hard illuminated edge.
    // Sprite vertices have no usable supplied normal in the native renderer.
    vec3 sheetNormal=normalize(cross(dFdx(world),dFdy(world)));
    alpha *= smoothstep(.015,.12,abs(dot(sheetNormal,normalize(eye))));
#endif
    // getTexel applies the engine's stencil tint, sector desaturation and
    // texture color modifiers. Returning white here would erase map colors.
    return vec4(getTexel(uv).rgb,alpha*flow);
}
