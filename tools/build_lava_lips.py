"""Generate rounded lava spill lips from every QLAVA -> LAVA lower-wall edge.

No WADs are rewritten. Re-run automatically through build_utnt.py after map or
lava shader edits. Geometry is a 4-unit liquid meniscus over the existing edge;
the collision surface, sector tags, terrain and wall textures remain original.
"""
from pathlib import Path
import argparse, collections, json, math, os, re, struct, tempfile

FLOORS=('QLAVA','QLAVA2','QLAVASB')
FALLS=('LAVA','LAVAHR')

def parse(path):
    d=path.read_bytes();magic,n,o=struct.unpack_from('<4sII',d)
    if magic not in (b'PWAD',b'IWAD'):raise ValueError(path)
    lumps={k.rstrip(b'\0').decode():d[a:a+b] for a,b,k in [struct.unpack_from('<II8s',d,o+i*16) for i in range(n)]}
    text=lumps.get('TEXTMAP',b'').decode()
    # Keep quoted strings intact when removing UDMF comments.
    text=re.sub(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*.*?\*/',lambda m:m[0] if m[0].startswith('"') else '',text,flags=re.S)
    return {k:[dict(re.findall(r'(\w+)\s*=\s*([^;]+);',s)) for s in re.findall(r'\b'+k+r'\s*\{([^}]+)\}',text)] for k in ('vertex','sector','sidedef','linedef')}

def tex(s,k):return s.get(k,'-').strip('"').upper()
def point(v):return (float(v['x']),float(v['y']))
def plus(a,b,f=1):return (a[0]+b[0]*f,a[1]+b[1]*f)
def sub(a,b):return plus(a,b,-1)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def norm(a):
    length=math.hypot(*a)
    return (a[0]/length,a[1]/length)
def height(s,p):
    if 'floorplane_c' in s:
        a,b,c,d=(float(s.get('floorplane_'+x,0)) for x in 'abcd')
        return -(a*p[0]+b*p[1]+d)/c
    return float(s.get('heightfloor',0))

def detect(b):
    result=[]
    for i,l in enumerate(b['linedef']):
        ids=[int(l.get('sidefront',-1)),int(l.get('sideback',-1))]
        if min(ids)<0:continue
        for face in range(2):
            low=b['sidedef'][ids[face]];high=b['sidedef'][ids[1-face]]
            lo=b['sector'][int(low['sector'])];hi=b['sector'][int(high['sector'])]
            if tex(low,'texturebottom') not in FALLS or tex(hi,'texturefloor') not in FLOORS:continue
            a,c=(point(b['vertex'][int(l[v])]) for v in ('v1','v2'))
            if face:a,c=c,a
            length=math.dist(a,c)
            if length<0.01:continue
            drop=min(height(hi,p)-height(lo,p) for p in (a,c))
            if drop<=0:continue
            t=norm(sub(c,a));normal=(t[1],-t[0]) # visible fall side is right
            r=min(4.0,drop/16,length/8)
            result.append(dict(line=i,face=face,high=int(high['sector']),low=int(low['sector']),
                a=a,b=c,normal=normal,radius=r,length=length,floor=tex(hi,'texturefloor'),fall=tex(low,'texturebottom'),
                h0=height(hi,a),h1=height(hi,c),sector=hi))
    # Miter adjacent edges in the same lava pool. Identical cross-section
    # vertices at joins avoid cracks, including diagonal lines.
    ends=collections.defaultdict(list)
    for e in result:
        for p in ('a','b'):ends[e['high'],e[p]].append(e)
    # A connected rim shares one radius, including shallow/short segments.
    changed=True
    while changed:
        changed=False
        for peers in ends.values():
            if len(peers)!=2:continue
            radius=min(x['radius'] for x in peers)
            for e in peers:
                if e['radius']!=radius:e['radius']=radius;changed=True
    for e in result:
        for p in ('a','b'):
            peers=ends[e['high'],e[p]]
            n=e['normal'];m=n
            if len(peers)==2:
                other=next(x for x in peers if x is not e)
                den=1+dot(n,other['normal'])
                if den>0.4:m=tuple(x/den for x in plus(n,other['normal']))
            e['m'+p]=m
    return result

def profile(r):
    # Upper/lower easing meet the exact original materials outside the lip.
    pts=[]
    for i in range(9):
        u=i/8;ease=u*u*(3-2*u)
        pts.append((-8*r+7*r*u,0.035+r*ease,0.28*u))
    for i in range(1,13):
        a=math.pi*i/24
        pts.append((-r+2*r*math.sin(a),-r+2*r*math.cos(a)+0.035,0.28+0.32*i/12))
    for i in range(1,13):
        u=i/12;ease=u*u*(3-2*u)
        pts.append((r*(1-ease)+0.035,-r-11*r*u,0.60+0.40*u))
    return pts

def mesh(e):
    mid=tuple((a+b)/2 for a,b in zip(e['a'],e['b']));h=(e['h0']+e['h1'])/2
    rows=profile(e['radius']);verts=[];uv=[];normals=[];faces=[]
    steps=max(1,math.ceil(e['length']/96))
    # OBJ uses Y up and mirrored Z in UZDoom's loader.
    for j in range(steps+1):
        u=j/steps;p=plus(e['a'],sub(e['b'],e['a']),u)
        m=plus(e['ma'],sub(e['mb'],e['ma']),u)
        for k,(d,z,v) in enumerate(rows):
            w=plus(p,m,d)
            verts.append((w[0]-mid[0],height(e['sector'],w)-h+z,-(w[1]-mid[1])))
            uv.append((u,1-v))
            before=rows[max(0,k-1)];after=rows[min(len(rows)-1,k+1)]
            dd,dz=after[0]-before[0],after[1]-before[1]
            n=norm(m);nx,ny,nz=-dz*n[0],-dz*n[1],dd
            if k==0:nx,ny,nz=0,0,1
            if k==len(rows)-1:nx,ny,nz=n[0],n[1],0
            sx=height(e['sector'],plus(w,(1,0)))-height(e['sector'],w)
            sy=height(e['sector'],plus(w,(0,1)))-height(e['sector'],w)
            nx-=nz*sx;ny-=nz*sy
            length=math.sqrt(nx*nx+ny*ny+nz*nz)
            normals.append((nx/length,nz/length,-ny/length))
    n=len(rows)
    for j in range(steps):
        for k in range(n-1):
            a=j*n+k+1;b=a+n
            faces.extend(((a,b,b+1),(a,b+1,a+1)))
    lines=['# Generated lava meniscus: no gameplay geometry.','s 1']
    lines+=['v %.6f %.6f %.6f'%v for v in verts]
    lines+=['vt %.6f %.6f'%v for v in uv]
    lines+=['vn %.6f %.6f %.6f'%v for v in normals]
    lines+=['f '+' '.join(f'{v}/{v}/{v}' for v in f) for f in faces]
    return '\n'.join(lines)+'\n',mid,h,len(faces)

def shader(root):
    surface=(root/'tutnt/shaders/lava-surface.fp').read_text()
    fall=(root/'tutnt/shaders/lava-fall.fp').read_text()
    entry='void SetupMaterial(inout Material mat)'
    if surface.count(entry)!=1 or fall.count(entry)!=1:
        raise ValueError('Lava shader entry point changed; update the lip generator.')
    surface=surface.replace('void SetupMaterial(inout Material mat)','void LipSurface(inout Material mat)')
    surface=surface.replace('vec2 world=LavaWorldPosition();','vec2 world=pixelpos.xz;')
    fall=fall.replace('void SetupMaterial(inout Material mat)','void LipFall(inout Material mat)')
    fall=fall.replace('getTexel(', 'LipFallTexel(')
    # Preserve texture manipulation for PLAYPAL, sector tint and desaturation.
    fetch='''vec4 LipFallTexel(vec2 uv)
{
    vec4 c=texture(fallTexture,uv);
    int flags=int(uTextureAddColor.a);
    if(flags!=0)c=ApplyTextureManipulation(c,flags);
    c.rgb+=uAddColor.rgb;
    c*=uObjectColor;
    return desaturate(c);
}
'''
    wrapper='''
void SetupMaterial(inout Material mat)
{
    float v=clamp(vTexCoord.t,0.0,1.0);
    LipSurface(mat);
    Material falling=mat;
    LipFall(falling);
    // Both ends evaluate the existing shaders at their original world position.
    // The same QLAVA pattern continues over the convex nose before stretching
    // and dissolving into the downward curtain, without a luminous seam line.
    float blend=smoothstep(0.18,0.94,v);
    mat.Base=mix(mat.Base,falling.Base,blend);
    mat.Base.a*=smoothstep(0.0,0.05,v)*(1.0-smoothstep(0.95,1.0,v));
    mat.Bright=mix(mat.Bright,falling.Bright,blend);
    mat.Normal=normalize(mix(mat.Normal,falling.Normal,blend));
    LavaFarVisibility=mix(LavaFarVisibility,1.0,blend);
}
'''
    return '// Generated from the current two lava shaders.\n'+surface+'\n'+fetch+fall+wrapper

def generate(root,extra_maps=(),check=False):
    root=Path(root);out={};records=[];actors=[];models=[];definitions=[]
    textures=[]
    for floor in FLOORS:
        for fall in FALLS:
            alias='LL'+str(FLOORS.index(floor))+str(FALLS.index(fall))
            textures.append(f'Texture "{alias}", 64, 64 {{ Patch "{floor}", 0, 0 }}')
            definitions.append(f'Material Texture "{alias}" {{ Shader "shaders/lava-lips.fp" Texture crustHeight "materials/lava/crust-height.png" Texture fallTexture "{fall}" Speed 1.0 }}')
    for path in sorted(list((root/'tutnt/maps').glob('*.wad'))+list(extra_maps)):
        b=parse(path);edges=detect(b);rows=[]
        for e in edges:
            model,mid,h,triangles=mesh(e)
            stem=f'{path.stem.lower()}-{e["line"]}-{e["face"]}'
            cls='UTNTLavaLip_'+stem.replace('-','_')
            alias='LL'+str(FLOORS.index(e['floor']))+str(FALLS.index(e['fall']))
            out['tutnt/models/lava-lips/'+stem+'.obj']=model
            actors.append(f'class {cls} : UTNTLavaLip {{ Default {{ RenderRadius {math.ceil(e["length"]/2+64)}; }} }}')
            models.append(f'Model {cls}\n{{\n Path "models/lava-lips/"\n Model 0 "{stem}.obj"\n Skin 0 "{alias}"\n Scale 1 1 1.2\n DontCullBackfaces\n FrameIndex LALP A 0 0\n}}')
            row=[cls,e['line'],e['face'],e['high'],e['low'],*e['a'],*e['b'],*mid,h,e['h0'],e['h1'],e['floor'],e['fall'],e['radius']]
            rows.append('|'.join(str(x) for x in row))
            records.append(dict(map=path.stem.upper(),line=e['line'],face=e['face'],high=e['high'],low=e['low'],radius=e['radius'],triangles=triangles,a=e['a'],b=e['b'],height=h))
        if rows:out[f'tutnt/lavalips/{path.stem.lower()}.txt']='\n'.join(rows)+'\n'
    out['tutnt/zscript/lava-lips-generated.zc']='// Generated; rebuild after map edits.\n'+'\n'.join(actors)+'\n'
    out['tutnt/MODELDEF.lava-lips']='\n'.join(models)+'\n'
    out['tutnt/GLDEFS.lava-lips']='\n'.join(definitions)+'\n'
    out['tutnt/TEXTURES.lava-lips']='\n'.join(textures)+'\n'
    out['tutnt/shaders/lava-lips.fp']=shader(root)
    # Visible only if models are disabled: transparent fallback, no marker sprite.
    import base64
    out['tutnt/sprites/LALPA0.png']=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR4nGNgAAIAAAUAAarVyFEAAAAASUVORK5CYII=')
    manifest={'rule':{'floors':FLOORS,'lower_walls':FALLS},'edge_count':len(records),'edges':records}
    out['tools/lava-lips-manifest.json']=json.dumps(manifest,indent=2)+'\n'
    inventory=root/'tools/lava-lips-outputs.json'
    previous=json.loads(inventory.read_text()) if inventory.exists() else []
    # Remove only obsolete files explicitly recorded by this generator. Resolve
    # every deletion under its owned geometry/registry directories first.
    stale=[]
    for rel in previous:
        if rel in out:continue
        if not re.fullmatch(r'tutnt/(?:models/lava-lips/[\w-]+\.obj|lavalips/[\w-]+\.txt)',rel):continue
        p=(root/rel).resolve();p.relative_to(root.resolve())
        if p.exists():stale.append(p)
    out['tools/lava-lips-outputs.json']=json.dumps(sorted(out),indent=2)+'\n'
    changed=[]
    for rel,data in out.items():
        p=root/rel;data=data.encode() if isinstance(data,str) else data
        if not p.exists() or p.read_bytes()!=data:
            changed.append(rel)
            if not check:
                p.parent.mkdir(parents=True,exist_ok=True)
                fd,tmp=tempfile.mkstemp(prefix='.lavalip-',dir=p.parent)
                try:
                    with os.fdopen(fd,'wb') as f:f.write(data)
                    os.replace(tmp,p)
                finally:
                    if os.path.exists(tmp):os.unlink(tmp)
    if check and (changed or stale):raise RuntimeError('Stale lava lip assets: '+', '.join(changed[:8]))
    if not check:
        for p in stale:p.unlink()
    return {'edges':len(records),'maps':dict(collections.Counter(x['map'] for x in records)),'triangles':sum(x['triangles'] for x in records),'updated':len(changed)}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent.parent);p.add_argument('--check',action='store_true');a=p.parse_args()
    print(json.dumps(generate(a.root,check=a.check),indent=2))
