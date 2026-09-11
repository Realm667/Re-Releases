// Tangent-space Parallax Occlusion Mapping. Material-specific depth in world units.
// Color texture unchanged; height and normal textures are independent data.
// An overlay can leave old material programs in the engine's compile list.
// Keep their old height convention until the new definitions replace them.
#ifndef ORGANIC_BASE_HEIGHT
#define ORGANIC_BASE_HEIGHT 1.0
#define ORGANIC_TRACE_TOP 0.0
#define ORGANIC_TRACE_BOTTOM 1.0
#define ORGANIC_LEGACY_HEIGHT
#endif
const float RockDepth=ORGANIC_DEPTH;
// Data maps stay bilinear even when the player selects unfiltered pixel art.
vec4 RockRawData(sampler2D dataMap,vec2 uv,vec2 gx,vec2 gy)
{
    vec2 fullSize=vec2(textureSize(dataMap,0));
    vec2 dx=gx*fullSize,dy=gy*fullSize;
    int lod=int(max(0.0,floor(0.5*log2(max(max(dot(dx,dx),dot(dy,dy)),1.0)))));
    ivec2 size=textureSize(dataMap,lod);
    vec2 p=uv*vec2(size)-0.5;
    ivec2 a=ivec2(floor(p));
    vec2 f=fract(p);
    ivec2 q=((a%size)+size)%size;
    ivec2 r=(q+ivec2(1))%size;
    return mix(mix(texelFetch(dataMap,q,lod),texelFetch(dataMap,ivec2(r.x,q.y),lod),f.x),
               mix(texelFetch(dataMap,ivec2(q.x,r.y),lod),texelFetch(dataMap,r,lod),f.x),f.y);
}
// Preserve the existing area-expansion border mixing for color and data.
vec2 OrganicEdgeWeight(vec2 uv)
{
    vec2 w=vec2(0.0);
#if defined(ORGANIC_TILE_EDGE) || defined(ORGANIC_BAND_EDGE)
    vec2 f=fract(uv);
    w=vec2(1.0)-smoothstep(vec2(0.0),vec2(0.016),min(f,vec2(1.0)-f));
#ifdef ORGANIC_BAND_EDGE
    w.y=0.0;
#endif
#endif
    return w;
}
vec4 RockData(sampler2D dataMap,vec2 uv,vec2 gx,vec2 gy)
{
    vec4 c=RockRawData(dataMap,uv,gx,gy);
#if defined(ORGANIC_TILE_EDGE) || defined(ORGANIC_BAND_EDGE)
    vec2 w=OrganicEdgeWeight(uv);
    if(w.x>0.0)c=mix(c,RockRawData(dataMap,uv+vec2(.5,0),gx,gy),w.x);
    if(w.y>0.0){
        vec4 d=RockRawData(dataMap,uv+vec2(0,.5),gx,gy);
        if(w.x>0.0)d=mix(d,RockRawData(dataMap,uv+vec2(.5,.5),gx,gy),w.x);
        c=mix(c,d,w.y);
    }
#endif
    return c;
}
void OrganicColor(inout Material mat,vec2 uv)
{
#if defined(ORGANIC_TILE_EDGE) || defined(ORGANIC_BAND_EDGE)
    vec2 w=OrganicEdgeWeight(uv);vec4 c=getTexel(uv);
    if(w.x>0.0)c=mix(c,getTexel(uv+vec2(.5,0)),w.x);
    if(w.y>0.0){
        vec4 d=getTexel(uv+vec2(0,.5));
        if(w.x>0.0)d=mix(d,getTexel(uv+vec2(.5,.5)),w.x);
        c=mix(c,d,w.y);
    }
    mat.Base=c;
#endif
}
#ifdef ORGANIC_METAL
void SetupMetalResponse(inout Material mat,vec2 uv,vec2 gx,vec2 gy)
{
    vec2 surface=RockData(organicSurface,uv,gx,gy).rg;
    mat.Specular=vec3(surface.r);
    mat.SpecularLevel=.55;mat.Glossiness=surface.g*32.0;
}
#endif
float ReadRockDepth(vec2 uv,vec2 gx,vec2 gy)
{
#ifdef ORGANIC_LEGACY_HEIGHT
    return 1.0-RockData(organicHeight,uv,gx,gy).r;
#else
    // Gray 127 is the geometric wall/floor plane; negative depth protrudes.
    return 2.0*(127.0/255.0-RockData(organicHeight,uv,gx,gy).r);
#endif
}
void SetupOrganicMaterial(inout Material mat)
{
    vec2 uv=vTexCoord.st,gx=dFdx(uv),gy=dFdy(uv);
    vec3 n=normalize(vWorldNormal.xyz);
    vec3 dpdx=dFdx(pixelpos.xyz),dpdy=dFdy(pixelpos.xyz);
    float determinantUV=gx.x*gy.y-gx.y*gy.x;
    SetMaterialProps(mat,uv);
    OrganicColor(mat,uv);
#ifdef ORGANIC_METAL
    SetupMetalResponse(mat,uv,gx,gy);
#endif
    if(abs(determinantUV)<1e-12)return;
    vec3 tu=(dpdx*gy.y-dpdy*gx.y)/determinantUV;
    vec3 tv=(dpdy*gx.x-dpdx*gy.x)/determinantUV;
    vec2 worldSize=vec2(length(tu),length(tv));
    vec3 t=normalize(tu),b=normalize(tv);
    vec3 view=normalize(uCameraPos.xyz-pixelpos.xyz);
    float vz=max(dot(view,n),0.08);
    float distanceToEye=length(uCameraPos.xyz-pixelpos.xyz);
    float fade=(1.0-smoothstep(512.0,1024.0,distanceToEye))*smoothstep(0.08,0.30,dot(view,n));
    if(fade<=0.0)
    {
        mat.Normal=normalize(mix(n,mat.Normal,1.0-smoothstep(1024.0,1536.0,distanceToEye)));
#ifdef ORGANIC_ICE
        mat.Specular=vec3(.30);mat.SpecularLevel=.65;mat.Glossiness=20.0;
#endif
        return;
    }
    // Bound grazing-angle displacement and gradually fade in the distance.
    vec2 slope=vec2(dot(view,t),dot(view,b))/max(vz,0.18);
    vec2 ray=slope*RockDepth*fade/worldSize;
    int steps=int(mix(32.0,16.0,clamp(vz,0.0,1.0)));
    float top=ORGANIC_TRACE_TOP,bottom=ORGANIC_TRACE_BOTTOM;
    float stepDepth=(bottom-top)/float(steps),layer=top;
    vec2 hit=uv-ray*layer;
    for(int i=0;i<32;i++)
    {
        if(i>=steps || layer>=ReadRockDepth(hit,gx,gy))break;
        layer+=stepDepth;hit=uv-ray*layer;
    }
    float low=max(top,layer-stepDepth),high=layer;
    for(int j=0;j<5;j++)
    {
        float mid=(low+high)*0.5;
        if(mid<ReadRockDepth(uv-ray*mid,gx,gy))low=mid;else high=mid;
    }
    // Interpolation makes a constant neutral region land exactly on zero.
    float dl=ReadRockDepth(uv-ray*low,gx,gy),dh=ReadRockDepth(uv-ray*high,gx,gy);
    float denominator=(high-low)-(dh-dl);
    layer=abs(denominator)>1e-8 ? mix(low,high,clamp((dl-low)/denominator,0.0,1.0)) : high;
    hit=uv-ray*layer;
    float artworkHeight=ORGANIC_BASE_HEIGHT-layer;
    SetMaterialProps(mat,hit);
    OrganicColor(mat,hit);
    // Green-up normal data, transformed using the undisplaced surface basis.
    vec3 nn=RockData(normaltexture,hit,gx,gy).xyz*2.0-1.0;
    nn.y=-nn.y;
    mat.Normal=normalize(t*nn.x+b*nn.y+n*nn.z);
    mat.Specular=vec3(0.0);mat.SpecularLevel=0.0;
#ifdef ORGANIC_METAL
    SetupMetalResponse(mat,hit,gx,gy);
#endif
    vec3 sky=normalize(vec3(0.48,0.76,-0.44));
    float sz=max(dot(sky,n),0.12);
    vec2 lightRay=vec2(dot(sky,t),dot(sky,b))*RockDepth*fade/(worldSize*sz);
    float occlusion=0.0;
    if(dot(sky,n)>0.08)
    {
        for(int i=1;i<=10;i++)
        {
            float rise=(layer-top)*float(i)/10.0;
            float blocker=ReadRockDepth(hit+lightRay*rise,gx,gy);
            occlusion=max(occlusion,smoothstep(0.02,0.12,(layer-rise)-blocker));
        }
    }
    float flatLight=0.32+0.68*max(dot(n,sky),0.0);
    float bumpLight=0.32+0.68*max(dot(mat.Normal,sky),0.0);
    float shade=clamp(bumpLight/max(flatLight,0.35),0.46,1.8);
    shade*=mix(1.0,0.58,occlusion);
    shade*=mix(0.72,1.0,smoothstep(0.15,0.75,artworkHeight));
    mat.Base.rgb*=mix(1.0,shade,fade*ORGANIC_SHADE);
#ifdef ORGANIC_ICE
    // Broad ice faces catch light; recessed frost remains more diffuse.
    float clearIce=smoothstep(.28,.76,artworkHeight);
    mat.Specular=vec3(mix(.18,.42,clearIce));
    mat.SpecularLevel=.65;mat.Glossiness=mix(12.0,28.0,clearIce);
    float fresnel=pow(1.0-clamp(dot(mat.Normal,view),0.0,1.0),4.0);
    float skyFacing=smoothstep(-.1,.65,reflect(-view,mat.Normal).y);
    // A subdued environment approximation, shaded with the sector, never emissive.
    mat.Base.rgb+=vec3(.10,.13,.16)*fresnel*skyFacing*fade;
#endif
}
