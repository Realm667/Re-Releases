// Shared soft scattering. Model slices are weighted by facing, so their
// combined brightness stays stable as the player walks around the lamp.
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
#if RAY_VOLUME == 1
    vec3 view = normalize(vec3(eye.x,0.,eye.z)+vec3(.00001,0.,0.));
    float facing = abs(dot(normalize(vWorldNormal.xyz),view));
    alpha *= facing*facing/3.; // six radial planes: sum(cos^2) = 3
#endif
    // getTexel applies the engine's stencil tint, sector desaturation and
    // texture color modifiers. Returning white here would erase map colors.
    return vec4(getTexel(uv).rgb,alpha*flow);
}
