float SampleIce(vec2 uv)
{
    return texture(frostTexture,clamp(uv,vec2(0.001),vec2(0.999))).r;
}
void main()
{
    vec2 uv=TexCoord;
    float aspect=float(textureSize(InputTexture,0).x)/float(textureSize(InputTexture,0).y);
    vec2 payloadDrops[14]=vec2[](drop0,drop1,drop2,drop3,drop4,drop5,drop6,drop7,drop8,drop9,drop10,drop11,drop12,drop13);
    vec2 p=uv*vec2(aspect,1.0),offset=vec2(0);
    float overlay=0.0,tone=0.5,waterBlur=0.0;
    if(wetAmount>0.001) for(int i=0;i<14;i++)
    {
        if(i>=dropCount) break;
        vec2 payload=payloadDrops[i];
        vec3 d=vec3(mod(payload.x,4096.0)/4095.0,floor(payload.x/4096.0)/4095.0*1.1-0.05,
                    mod(payload.y,64.0)/63.0*0.04);
        vec3 s=vec3(mod(floor(payload.y/64.0),64.0)/63.0,
                    1.0+mod(floor(payload.y/4096.0),32.0)/31.0*2.0,
                    floor(payload.y/131072.0)/127.0*0.28);
        vec2 center=d.xy*vec2(aspect,1.0);
        float radius=d.z;
        float deposit=s.x*wetAmount;
        vec2 q=(p-center)/vec2(radius,radius*s.y);
        q.x*=1.0+q.y*0.08;
        float r2=dot(q,q);
        if(r2<1.4884)
        {
            float radial=sqrt(r2);
            vec2 surface=q/max(1.0,radial);
            vec3 normal=normalize(vec3(surface*0.88,sqrt(max(0.04,1.0-dot(surface,surface)))));
            vec3 ray=refract(vec3(0,0,-1),normal,1.0/1.333);
            // Out-of-focus water has a broad, soft silhouette, without a sharp ring.
            float coverage=1.0-smoothstep(0.55,1.22,radial);
            offset+=ray.xy/max(abs(ray.z),0.25)*radius*3.6*coverage*deposit/vec2(aspect,1.0);
            waterBlur=max(waterBlur,coverage*deposit);
            // Requested 20% maximum graphic contribution, chiefly at curved edges.
            float rim=exp(-pow((radial-0.83)*4.5,2.0))*coverage;
            float weight=(rim*0.8+coverage*0.2)*deposit*0.20;
            float light=clamp(0.5+dot(normal,normalize(vec3(-0.5,0.8,0.2)))*0.5,0.0,1.0);
            if(weight>overlay) { overlay=weight; tone=light; }
        }
        float h=p.y-center.y;
        if(s.z>0.002 && h>0.0 && h<s.z)
        {
            float t=h/s.z;
            float path=center.x+sin(t*3.4+float(i))*0.001*t;
            float width=radius*0.40*(1.0-0.72*t);
            float x=(p.x-path)/max(width,0.0001);
            if(abs(x)<1.25)
            {
                float weight=(1.0-smoothstep(0.35,1.25,abs(x)))*(1.0-smoothstep(0.55,1.0,t))*deposit;
                float surface=clamp(x,-1.0,1.0);
                vec3 n=normalize(vec3(surface,0,sqrt(max(0.03,1.0-surface*surface))));
                offset.x+=refract(vec3(0,0,-1),n,1.0/1.333).x*width*12.0*weight/aspect;
                waterBlur=max(waterBlur,weight*0.65);
                if(weight*0.06>overlay) { overlay=weight*0.06; tone=0.58; }
            }
        }
    }
    vec2 waterCoord=waterBlur>0.001 ? clamp(uv+offset,vec2(0.003),vec2(0.997)) : uv;
    vec3 col=texture(InputTexture,waterCoord).rgb;
    if(waterBlur>0.001 && detailLevel>=2)
    {
        vec2 blur=vec2(0.0022)/vec2(aspect,1.0);
        vec3 softened=col*0.4;
        softened+=(texture(InputTexture,waterCoord+vec2(blur.x,0)).rgb
                  +texture(InputTexture,waterCoord-vec2(blur.x,0)).rgb
                  +texture(InputTexture,waterCoord+vec2(0,blur.y)).rgb
                  +texture(InputTexture,waterCoord-vec2(0,blur.y)).rgb)*0.15;
        col=mix(col,softened,waterBlur*0.75);
    }
    col=mix(col,vec3(tone),clamp(overlay,0.0,0.20));
    if(frostAmount>0.001)
    {
        // One unique full-frame image, never tiled. The visible crystal mask
        // stays sharp; filtered samples only shape the refractive normals.
        // Lower accumulation samples the thinner inner crystal frontier.
        // Stay inside the image: clamping outside it stretches edge texels
        // into visible horizontal/vertical streaks at light snow strengths.
        vec2 frostUV=(uv-0.5)*(0.84+frostAmount*0.16)+0.5;
        vec2 border=min(uv,1.0-uv);
        float extent=0.045+frostAmount*0.155;
        float edge=min(border.x,border.y);
        if(edge<extent)
        {
            // Dense 5x5 Gaussian taps avoid the separated-image artifacts of
            // a sparse wide kernel. Accumulate smooth normals in the same pass.
            vec2 stepUV=vec2(0.0025)/vec2(aspect,1.0);
            float weights[5]=float[](1.0,4.0,6.0,4.0,1.0);
            float ice=SampleIce(frostUV);
            vec2 gradient=vec2(0.0);
            for(int y=-2;y<=2;y++) for(int x=-2;x<=2;x++)
            {
                float value=SampleIce(frostUV+vec2(x,y)*stepUV);
                float weight=weights[x+2]*weights[y+2]/256.0;
                gradient+=vec2(x,y)*value*weight*2.0;
            }
            float field=1.0-smoothstep(extent*0.45,extent,edge);
            float coverage=smoothstep(0.018,0.65,ice)*field*sqrt(frostAmount);
            if(coverage>0.001)
            {
                vec2 coord=clamp(uv+gradient*coverage*0.10/vec2(aspect,1),vec2(0.006),vec2(0.994));
                vec3 blurred=texture(InputTexture,coord).rgb;
                if(detailLevel>=2)
                {
                    vec2 blur=vec2(0.0018*coverage)/vec2(aspect,1);
                    blurred=blurred*0.4+(texture(InputTexture,coord+blur).rgb+texture(InputTexture,coord-blur).rgb)*0.3;
                }
                // Apply accumulation once: the former nested mix squared weak frost.
                col=mix(col,blurred,1.0-exp(-coverage*3.0));
                col=mix(col,vec3(0.8),clamp(coverage*(0.30+ice*0.55)*0.50,0.0,0.43));
            }
        }
    }
    FragColor=vec4(col,1.0);
}
