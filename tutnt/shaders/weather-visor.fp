
void main()
{
    vec2 uv=TexCoord;
    float aspect=float(textureSize(InputTexture,0).x)/float(textureSize(InputTexture,0).y);
    vec2 payloadDrops[14]=vec2[](drop0,drop1,drop2,drop3,drop4,drop5,drop6,drop7,drop8,drop9,drop10,drop11,drop12,drop13);
    vec2 p=uv*vec2(aspect,1.0),offset=vec2(0);
    float overlay=0.0,tone=0.5;
    if(wetAmount>0.001) for(int i=0;i<14;i++)
    {
        if(i>=dropCount) break;
        vec2 payload=payloadDrops[i];
        vec3 d=vec3(mod(payload.x,4096.0)/4095.0,floor(payload.x/4096.0)/4095.0*1.1-0.05,
                    mod(payload.y,64.0)/63.0*0.04);
        vec3 s=vec3(mod(floor(payload.y/64.0),64.0)/63.0,
                    1.0+mod(floor(payload.y/4096.0),32.0)/31.0*0.5,
                    floor(payload.y/131072.0)/127.0*0.13);
        vec2 center=d.xy*vec2(aspect,1.0);
        float radius=d.z;
        float deposit=s.x*wetAmount;
        vec2 q=(p-center)/vec2(radius,radius*s.y);
        q.x*=1.0+q.y*0.08;
        float r2=dot(q,q);
        if(r2<1.0)
        {
            vec3 normal=normalize(vec3(q*0.88,sqrt(max(0.04,1.0-r2))));
            vec3 ray=refract(vec3(0,0,-1),normal,1.0/1.333);
            float coverage=1.0-smoothstep(0.80,1.0,sqrt(r2));
            offset+=ray.xy/max(abs(ray.z),0.25)*radius*1.7*coverage*deposit/vec2(aspect,1.0);
            // Requested 20% maximum graphic contribution, chiefly at curved edges.
            float rim=exp(-pow((sqrt(r2)-0.86)*12.0,2.0));
            float weight=(rim*0.8+coverage*0.2)*deposit*0.20;
            float light=clamp(0.5+dot(normal,normalize(vec3(-0.5,0.8,0.2)))*0.5,0.0,1.0);
            if(weight>overlay) { overlay=weight; tone=light; }
        }
        float h=p.y-center.y;
        if(s.z>0.002 && h>0.0 && h<s.z)
        {
            float t=h/s.z;
            float path=center.x+sin(t*3.4+float(i))*0.002*t;
            float width=radius*0.15*(1.0-t);
            float x=(p.x-path)/max(width,0.0001);
            if(abs(x)<1.0)
            {
                float weight=(1.0-smoothstep(0.80,1.0,abs(x)))*(1.0-smoothstep(0.65,1.0,t))*deposit;
                vec3 n=normalize(vec3(x,0,sqrt(max(0.03,1.0-x*x))));
                offset.x+=refract(vec3(0,0,-1),n,1.0/1.333).x*width*4.0*weight/aspect;
                if(weight*0.03>overlay) { overlay=weight*0.03; tone=0.58; }
            }
        }
    }
    vec3 col=texture(InputTexture,clamp(uv+offset,vec2(0.001),vec2(0.999))).rgb;
    col=mix(col,vec3(tone),clamp(overlay,0.0,0.20));
    if(frostAmount>0.001)
    {
        // One unique full-frame image, sampled once: no tiled crystal texture.
        // Lower accumulation expands the sampling coordinates outwards so the
        // crystal frontier recedes towards the screen edges, while alpha fades.
        vec2 frostUV=(uv-0.5)*(1.0+(1.0-frostAmount)*0.30)+0.5;
        frostUV=clamp(frostUV,vec2(0.001),vec2(0.999));
        float ice=texture(frostTexture,frostUV).r;
        vec2 border=min(uv,1.0-uv);
        float extent=0.035+frostAmount*0.165;
        float edge=min(border.x,border.y);
        float field=1.0-smoothstep(extent*0.55,extent,edge);
        float coverage=smoothstep(0.018,0.65,ice)*field*frostAmount;
        if(coverage>0.001)
        {
            vec2 pixel=1.0/vec2(textureSize(frostTexture,0));
            vec2 gradient=vec2(texture(frostTexture,frostUV+vec2(pixel.x,0)).r-texture(frostTexture,frostUV-vec2(pixel.x,0)).r,
                               texture(frostTexture,frostUV+vec2(0,pixel.y)).r-texture(frostTexture,frostUV-vec2(0,pixel.y)).r);
            vec2 coord=clamp(uv+gradient*coverage*0.004/vec2(aspect,1),vec2(0.003),vec2(0.997));
            vec3 blurred=texture(InputTexture,coord).rgb;
            if(detailLevel>=2)
            {
                vec2 blur=vec2(0.0018*coverage)/vec2(aspect,1);
                blurred=blurred*0.4+(texture(InputTexture,coord+blur).rgb+texture(InputTexture,coord-blur).rgb)*0.3;
            }
            vec3 frost=mix(blurred,vec3(0.8),clamp(coverage*(0.30+ice*0.55),0.0,0.86));
            col=mix(col,frost,coverage);
        }
    }
    FragColor=vec4(col,1.0);
}
