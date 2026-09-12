"""Build organic relief data and bindings without changing diffuse textures or maps.

Requires NumPy and Pillow. --check verifies all recorded inputs and outputs.
The regular UTNT build regenerates only this tool's outputs when inputs change.
"""
from pathlib import Path
import argparse, hashlib, io, json, math, os, re, struct
import numpy as np
from PIL import Image, ImageFilter
from material_geometry import authored_height
from material_traced_geometry import traced_height, NAMES as TRACED_NAMES

ROOT = Path(__file__).resolve().parent.parent
HEIGHT_NEUTRAL = 127/255
HEIGHT_GAIN = 2.0
# A shared material plane, never an independent per-image average.
PROFILE_BASE = dict(rock=.65, gravel=.60, soil=.50, grass=.50, snow=.50,
                    snowrock=.50, ice=.50, stonework=.88, brick=.88, metal=.15,
                    wood=.75, technical=.75, panel=.75, mortar=.75, authored=.5)


def encode_height(height, profile):
    encoded = HEIGHT_NEUTRAL+(height-PROFILE_BASE[profile])/HEIGHT_GAIN
    if np.min(encoded)<0 or np.max(encoded)>1:raise ValueError('Signed height would clip')
    return np.uint8(np.rint(encoded*255))


def height_depth(encoded):
    return HEIGHT_GAIN*(HEIGHT_NEUTRAL-np.asarray(encoded,dtype=np.float32)/255)


def rust_plate_height(rgb, logical, detail):
    lum = np.asarray(rgb,np.float32)/255 @ np.array([.2126,.7152,.0722],np.float32)
    crust = np.clip((lum-.07)/.20,0,1)
    raised = .36*crust*crust*(3-2*crust)
    # Rivet caps include the dark half of each head, not just painted highlights.
    if detail.get('rivets'):
        yy,xx=np.mgrid[:rgb.shape[0],:rgb.shape[1]]
        xx=(xx+.5)*logical[0]/rgb.shape[1];yy=(yy+.5)*logical[1]/rgb.shape[0]
        for cx,cy in detail['rivets']:
            dx=np.abs(xx-cx);dy=np.abs(yy-cy)
            dx=np.minimum(dx,logical[0]-dx);dy=np.minimum(dy,logical[1]-dy)
            cap=np.clip(1-(dx*dx+dy*dy)/(3.25*3.25),0,1)
            raised=np.maximum(raised,.62*cap*cap*(3-2*cap))
    return PROFILE_BASE['metal']+raised


def digest(data):
    return hashlib.sha256(data).hexdigest()

def texture_defs(mod):
    result = {}
    for p in sorted([*mod.glob('TEXTURES*'), *(mod/'textures/definitions').glob('TEXTURES*')], key=lambda p:p.name):
        if not p.is_file() or p.name.startswith('TEXTURES.environment'): continue
        text = p.read_text(errors='replace')
        for m in re.finditer(r'\b(Texture|Flat|WallTexture)\s+"?([\w.-]+)"?\s*,\s*(\d+)\s*,\s*(\d+)\s*\{([^{}]*)\}', text, re.I):
            body = m[5]
            patches = re.findall(r'\bPatch\s+"([^"]+)"\s*,\s*(-?\d+)\s*,\s*(-?\d+)', body, re.I)
            scales = []
            for axis in ('X','Y'):
                s = re.search(r'\b'+axis+r'Scale\s+([\d.]+)', body, re.I)
                scales.append(float(s[1]) if s else 1.0)
            result[m[2].upper()] = (int(m[3]),int(m[4]),scales,patches)
    return result

def patch_rgb(data, palette, flat=False):
    if data.startswith(b'\x89PNG'):
        image = Image.open(io.BytesIO(data)).convert('RGBA')
        a = np.asarray(image)
        if np.any(a[:,:,3] != 255): raise ValueError('Masked images need a dedicated relief profile')
        return a[:,:,:3]
    if flat:
        size = math.isqrt(len(data))
        if size*size != len(data): raise ValueError('Invalid native flat')
        return palette[np.frombuffer(data,np.uint8).reshape(size,size)]
    w,h = struct.unpack_from('<HH',data)
    if not 0<w<=8192 or not 0<h<=8192: raise ValueError('Invalid native patch')
    indices = np.zeros((h,w),np.uint8); filled = np.zeros((h,w),bool)
    for x in range(w):
        off = struct.unpack_from('<I',data,8+x*4)[0]; last = -1
        while data[off] != 255:
            top,n = data[off],data[off+1]
            if top<=last: top+=last
            indices[top:top+n,x] = np.frombuffer(data[off+3:off+3+n],np.uint8)
            filled[top:top+n,x] = True
            last=top;off+=n+4
    if not filled.all(): raise ValueError('Masked patches are outside this material group')
    return palette[indices]

def wrap_blur(a, radius):
    pad = int(radius*4+3)
    b = np.pad(a,((pad,pad),(pad,pad)),mode='wrap')
    im = Image.fromarray(np.uint8(np.clip(b,0,1)*255)).filter(ImageFilter.GaussianBlur(radius))
    return np.asarray(im,dtype=np.float32)[pad:-pad,pad:-pad]/255

def metal_height(rgb):
    # One pointwise transfer for every compatible panel, trim and floor.
    # Per-image contrast normalization would displace shared artwork differently.
    lum = np.asarray(rgb,np.float32)/255 @ np.array([.2126,.7152,.0722],np.float32)
    face = np.clip((lum-.015)/.265,0,1)
    return .15+.80*face*face*(3-2*face)


def metal_surface(rgb):
    color = np.asarray(rgb,np.float32)/255
    # Warm corrosion is matte; cool/neutral exposed metal catches broad light.
    rust = np.clip((color[:,:,0]-color[:,:,2]-.015)/.12,0,1)
    face = np.clip((metal_height(rgb)-.15)/.80,0,1)
    specular = (.07+.21*(1-rust))*(.55+.45*face)
    gloss = (8+16*(1-rust))/32
    return np.uint8(np.stack((specular,gloss,np.zeros_like(gloss)),axis=2)*255)


# Height comes from object masks and geometric layers, not local brightness relief.
STRUCTURE_PRESETS = {'wood': .45, 'technical': .55, 'panel': .50, 'mortar': .65}


def mask_distance(mask, iterations=8):
    distance=np.where(mask,iterations+1.0,0.0).astype(np.float32)
    for _ in range(iterations):
        distance=np.minimum.reduce([distance]+[
            np.roll(np.roll(distance,y,0),x,1)+math.hypot(x,y)
            for y,x in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]])
    return np.maximum(distance-.5,0)


def coherent_mask(mask, minimum):
    # Reject isolated paint/noise specks; preserve connected joints and channels.
    height,width=mask.shape;seen=np.zeros_like(mask);result=np.zeros_like(mask)
    for yy,xx in zip(*np.where(mask)):
        if seen[yy,xx]:continue
        stack=[(yy,xx)];seen[yy,xx]=True;component=[]
        while stack:
            y,x=stack.pop();component.append((y,x))
            for dy,dx in [(1,0),(-1,0),(0,1),(0,-1)]:
                ny,nx=(y+dy)%height,(x+dx)%width
                if mask[ny,nx] and not seen[ny,nx]:seen[ny,nx]=True;stack.append((ny,nx))
        if len(component)>=minimum:
            y,x=zip(*component);result[y,x]=True
    return result


def structure_height(rgb, profile, logical, detail):
    from PIL import ImageDraw
    height,width=rgb.shape[:2]
    yy,xx=np.mgrid[:height,:width]
    period=detail.get('period',logical)
    x=(xx+.5)*logical[0]/width%period[0];y=(yy+.5)*logical[1]/height%period[1]
    delta=np.zeros((height,width),np.float32)
    def smooth(v):
        v=np.clip(v,0,1);return v*v*(3-2*v)
    model=detail.get('model','toplit' if profile in ('technical','panel') else 'joints')
    if model=='toplit':
        # On these classified metal/pipe surfaces the baked light comes from above.
        # A bright upper slope and dark lower slope describe ONE raised body.
        lum=np.asarray(rgb,np.float32) @ np.array([.2126,.7152,.0722],np.float32)/255
        radius=max(1,int(round(detail.get('radius',4)*height/logical[1])))
        signal=np.zeros_like(delta);total=0
        for i in range(1,radius+1):
            weight=radius+1-i
            signal+=weight*(np.roll(lum,i,axis=0)-np.roll(lum,-i,axis=0));total+=weight
        signal/=total
        delta=np.sign(signal)*np.maximum(np.abs(signal)-.008,0)*detail.get('gain',3.0)
        delta=np.clip(delta,-.40,.20)
    if model in ('joints','channels'):
        lum=np.asarray(rgb,np.float32) @ np.array([.2126,.7152,.0722],np.float32)
        mask=lum<=detail.get('cutoff',6)
        # A constant material, even black, is a plane rather than a cavity.
        if not mask.all():
            if model=='channels':
                # Extend lit object tops into their painted lower shadow. This
                # preserves the body instead of cutting its shadow out of it.
                body=~mask
                for _ in range(detail.get('shadow_pixels',1)):
                    body |= np.roll(body,1,axis=0)
                mask=~body
            mask=coherent_mask(mask,detail.get('minimum_component',8))
            density=.5*(width/logical[0]+height/logical[1])
            distance=mask_distance(mask)/density
            delta=-detail.get('recess',STRUCTURE_PRESETS[profile])*smooth(distance/detail.get('bevel',1.0))
    # Authored lines use coordinates in a repeated source patch's map-unit space.
    for points,thickness,amount in detail.get('grooves',[]):
        dist=np.full_like(delta,1e6)
        for a,b in zip(points,points[1:]):
            ax,ay=a;bx,by=b;vx,vy=bx-ax,by-ay
            for sx in [-period[0],0,period[0]]:
                for sy in [-period[1],0,period[1]]:
                    t=np.clip(((x-ax-sx)*vx+(y-ay-sy)*vy)/max(vx*vx+vy*vy,1e-8),0,1)
                    dist=np.minimum(dist,np.hypot(x-ax-sx-vx*t,y-ay-sy-vy*t))
        delta=np.minimum(delta,-amount*(1-smooth((dist-thickness*.5)/.8)))
    for polygon,amount in detail.get('layers',[]):
        # Rasterize the shape, then give its whole body a bevel. Painted highlights
        # and shadows inside it therefore retain the same physical surface.
        im=Image.new('L',(int(period[0]),int(period[1])))
        ImageDraw.Draw(im).polygon([tuple(p) for p in polygon],fill=255)
        shape=np.asarray(im)[np.floor(y).astype(int),np.floor(x).astype(int)]>0
        distance=mask_distance(shape)/(.5*(width/logical[0]+height/logical[1]))
        field=amount*smooth(distance/1.1)
        delta=np.where(shape,field,delta)
    for cx,cy,radius,amount in detail.get('rivets',[]):
        dx=np.abs(x-cx);dy=np.abs(y-cy)
        dx=np.minimum(dx,period[0]-dx);dy=np.minimum(dy,period[1]-dy)
        cap=np.clip(1-(dx*dx+dy*dy)/(radius*radius),0,1)
        delta+=amount*np.sqrt(cap)
    for left,top,w,h in detail.get('neutral_regions',[]):
        delta[(x>=left)&(x<left+w)&(y>=top)&(y<top+h)]=0
    return PROFILE_BASE[profile]+np.clip(delta,-.72,.23)


def validate_compatibility(config):
    materials = {m['name']:m for m in config['materials']}
    if len(materials)!=len(config['materials']):raise ValueError('Duplicate material name')
    for m in materials.values():
        detail=m.get('height_detail')
        if detail and not ((detail.get('kind')=='traced-geometry' and detail.get('name') in TRACED_NAMES) or
                           (m['profile']=='metal' and detail.get('kind')=='raised-rust') or
                           (m['profile'] in STRUCTURE_PRESETS and detail.get('kind')=='surface-structure') or
                           (m['profile']=='authored' and detail.get('kind')=='authored-geometry')):
            raise ValueError('Unsupported height detail: '+m['name'])
    grouped = set()
    for name,group in config.get('compatibility_groups',{}).items():
        if group['profile']=='metal' and not 0<group['depth']<=6:
            raise ValueError('Metal compatibility groups must stay within 6 map units')
        for member in group['members']:
            if member in grouped:raise ValueError('Overlapping compatibility group: '+member)
            grouped.add(member)
            m=materials[member]
            if (m['profile'],m['depth'])!=(group['profile'],group['depth']):
                raise ValueError('Inconsistent compatibility group '+name+': '+member)
    if any(m['profile']=='metal' and m['name'] not in grouped for m in materials.values()):
        raise ValueError('Metal materials require a compatibility group')


def relief(rgb, profile, depth, logical, detail=None):
    lum = np.asarray(rgb,np.float32)/255 @ np.array([.2126,.7152,.0722],np.float32)
    soft = wrap_blur(lum,.9)
    lo,hi = np.quantile(soft,[.16,.91])
    face = np.clip((soft-lo)/max(hi-lo,.001),0,1)
    if detail and detail.get('kind')=='traced-geometry':
        h = PROFILE_BASE[profile]+traced_height(rgb,logical,detail)/depth
    elif profile == 'authored':
        h = PROFILE_BASE[profile]+authored_height(rgb,logical,detail)/depth
    elif profile in STRUCTURE_PRESETS:
        h = structure_height(rgb,profile,logical,detail or {})
    elif profile == 'metal':
        h = rust_plate_height(rgb,logical,detail) if detail else metal_height(rgb)
    elif profile in ('rock','gravel'):
        dist = np.where(face<.14,0,32).astype(np.float32)
        for _ in range(14):
            values = [dist]
            for y,x in ((0,1),(0,-1),(1,0),(-1,0),(1,1),(-1,1),(1,-1),(-1,-1)):
                values.append(np.roll(np.roll(dist,y,0),x,1)+math.hypot(x,y))
            dist = np.minimum.reduce(values)
        crown = np.sqrt(np.clip(dist/7.5,0,1))
        h = wrap_blur(.72*crown+.28*face,.8)*.92+.04
    elif profile in ('stonework','brick'):
        # Recess dark joints while retaining broad, nearly flat block faces.
        density = .5*(rgb.shape[1]/logical[0]+rgb.shape[0]/logical[1])
        joint = wrap_blur(face,max(.7,.55*density))
        plateau = np.clip((joint-.08)/.36,0,1)
        plateau = plateau*plateau*(3-2*plateau)
        detail = .20 if profile=='stonework' else .10
        h = .12+.80*((1-detail)*plateau+detail*face)
        h = wrap_blur(h,max(.6,.35*density))
    elif profile in ('snow','snowrock','ice'):
        # Filter in map units so expanded images retain the original relief scale.
        density = .5*(rgb.shape[1]/logical[0]+rgb.shape[0]/logical[1])
        rounded = wrap_blur(face,max(.8,2.0*density))
        broad = wrap_blur(face,max(1.2,5.0*density))
        if profile == 'snow':
            h = .16+.72*(.15*rounded+.85*broad)
        elif profile == 'snowrock':
            # Pale snow caps are rounded; darker exposed substrate stays recessed.
            cap = np.clip((rounded-.25)/.6,0,1)
            cap = cap*cap*(3-2*cap)
            h = .10+.80*(.55*cap+.30*broad+.15*rounded)
        else:
            # Continuous ice faces with shallow grooves, not separated stone crowns.
            h = .22+.64*(.65*rounded+.35*broad)
    elif profile in ('soil','grass'):
        # Fine ground: continuous shallow relief instead of separated rock crowns.
        broad = wrap_blur(face,2.5)
        h = wrap_blur(.55*face+.45*broad,1.0)*.72+.14
    else:
        raise ValueError('Unknown organic relief profile: '+profile)
    encoded = encode_height(h,profile)
    # Normals use the exact quantized field sampled by the shader.
    h = -height_depth(encoded)
    dx = (np.roll(h,-1,1)-np.roll(h,1,1))*.5*depth*h.shape[1]/logical[0]
    dy = (np.roll(h,-1,0)-np.roll(h,1,0))*.5*depth*h.shape[0]/logical[1]
    normal = np.stack((-dx,dy,np.ones_like(h)),axis=2)
    normal /= np.linalg.norm(normal,axis=2,keepdims=True)
    return encoded, np.uint8(np.clip(normal*.5+.5,0,1)*255)

def png_bytes(array):
    out=io.BytesIO();Image.fromarray(array).save(out,format='PNG')
    return out.getvalue()

def generate(root=ROOT, *, check=False, iwad=None):
    root=Path(root).resolve();mod=root/'tutnt'
    config_path=root/'tools/organic-materials/materials.json'
    manifest_path=root/'tools/organic-materials/generated.json'
    iwad=Path(iwad or os.environ.get('UTNT_IWAD',root.parents[1]/'DOOM2.WAD')).resolve()
    # Runtime builds with unchanged data require no IWAD image extraction.
    if manifest_path.exists():
        previous=json.loads(manifest_path.read_text())
        def source_path(k): return iwad if k=='@IWAD' else root/k
        valid = all(source_path(k).is_file() and digest(source_path(k).read_bytes())==v for k,v in previous['inputs'].items())
        valid = valid and all((root/k).is_file() and digest((root/k).read_bytes())==v for k,v in previous['outputs'].items())
        current_tables={p.relative_to(root).as_posix() for p in (mod/'environment').glob('*-surfaces.txt')}
        valid = valid and current_tables == set(previous['environment_tables'])
        if valid: return {'ok':True,'cached':True,'materials':len(previous['materials']),'bindings':previous['bindings']}
        if check: raise RuntimeError('Stale organic materials: run tools/build_organic_materials.py')
    elif check: raise RuntimeError('Organic material manifest missing')
    inputs={};outputs={}
    def read(p):
        p=Path(p);data=p.read_bytes()
        inputs['@IWAD' if p==iwad else p.relative_to(root).as_posix()] = digest(data)
        return data
    def emit(name,data):
        if isinstance(data,str):data=data.encode()
        outputs[name]=data
    read(root/'tools/build_organic_materials.py')
    geometry_digest=digest(read(root/'tools/material_geometry.py'))
    traced_digest=digest(read(root/'tools/material_traced_geometry.py')+geometry_digest.encode())
    config=json.loads(read(config_path))
    validate_compatibility(config)
    library={m['name']:m for m in json.loads(read(root/'tools/artwork/area-textures/materials.json'))}
    for p in sorted([*mod.glob('TEXTURES*'), *(mod/'textures/definitions').glob('TEXTURES*')], key=lambda p:p.name):
        if p.is_file() and not p.name.startswith('TEXTURES.environment'):read(p)
    definitions=texture_defs(mod)
    palette=np.frombuffer(read(mod/'PLAYPAL.pal')[:768],np.uint8).reshape(256,3)
    lumps=None
    def iw_flat(name, texture_name=None):
        nonlocal lumps
        if lumps is None:
            b=read(iwad);_,n,o=struct.unpack_from('<4sII',b)
            lumps={key.rstrip(b'\0').decode():b[a:a+size] for a,size,key in (struct.unpack_from('<II8s',b,o+i*16) for i in range(n))}
        if texture_name:
            data=lumps['TEXTURE1'];pn=lumps['PNAMES']
            names=[pn[4+i*8:12+i*8].rstrip(b'\0').decode() for i in range(struct.unpack_from('<I',pn)[0])]
            for i in range(struct.unpack_from('<I',data)[0]):
                off=struct.unpack_from('<I',data,4+i*4)[0]
                if data[off:off+8].rstrip(b'\0').decode()!=texture_name:continue
                w,h=struct.unpack_from('<HH',data,off+12);parts=[]
                for j in range(struct.unpack_from('<H',data,off+20)[0]):
                    x,y,index=struct.unpack_from('<hhH',data,off+22+j*10)
                    parts.append((patch_rgb(lumps[names[index].upper()],palette),x,y))
                return compose(w,h,parts)
        return patch_rgb(lumps[name],palette,True)
    files={}; file_rank={}
    for folder in ('flats','textures','patches'):
        for p in sorted((mod/folder).rglob('*')):
            if p.is_file() and p.suffix.lower() in ('.lmp','.png',''):
                key=p.stem.upper()
                rank=({'textures':0,'flats':1,'patches':2}[folder],0 if p.suffix.lower()=='.png' else 1)
                if key not in file_rank or rank<file_rank[key]:
                    files[key]=p;file_rank[key]=rank
    def compose(w,h,parts):
        rgb=np.zeros((h,w,3),np.uint8);filled=np.zeros((h,w),bool)
        for a,x,y in parts:
            left,top=max(0,x),max(0,y);right,bottom=min(w,x+a.shape[1]),min(h,y+a.shape[0])
            if right>left and bottom>top:
                rgb[top:bottom,left:right]=a[top-y:bottom-y,left-x:right-x];filled[top:bottom,left:right]=True
        if not filled.all():raise ValueError('Composite material has uncovered pixels')
        return rgb
    def resolve(name, fallback):
        if name in definitions:
            w,h,scales,patches=definitions[name]
            parts=[]
            for key,x,y in patches:
                path=mod/key
                if not path.exists():path=files.get(Path(key).stem.upper())
                if path is None:
                    if lumps is None:iw_flat('FLOOR0_1')
                    rgb=patch_rgb(lumps[key.upper()],palette)
                else:rgb=patch_rgb(read(path),palette,'flats' in path.relative_to(mod).parts)
                parts.append((rgb,int(x),int(y)))
            if len(parts)==1 and parts[0][1:]==(0,0):
                rgb=rgb[np.arange(h)%rgb.shape[0]][:,np.arange(w)%rgb.shape[1]]
            else:rgb=compose(w,h,parts)
            return rgb,(w/scales[0],h/scales[1])
        if fallback[0].startswith('DOOM2.WAD:') and (name not in file_rank or file_rank[name][0]==2):
            rgb=iw_flat(fallback[0].split(':')[1],name)
        elif name in files:
            path=files[name];rgb=patch_rgb(read(path),palette,'flats' in path.relative_to(mod).parts)
        elif fallback[0].startswith('DOOM2.WAD:'):rgb=iw_flat(fallback[0].split(':')[1],name)
        else:
            path=root/fallback[0].replace('\\','/');rgb=patch_rgb(read(path),palette,'flats' in path.relative_to(mod).parts)
        return rgb,(rgb.shape[1],rgb.shape[0])
    core=read(mod/'shaders/organic/relief.glsl').decode()
    environment=read(mod/'shaders/environment/surface.glsl').decode()
    assert environment.count('ENV_ORIGINAL_BODY')==1
    emit('tutnt/shaders/organic/material.fp','// Included source: '+digest(core.encode())+'\n#include "shaders/organic/relief.glsl"\nvoid SetupMaterial(inout Material mat){SetupOrganicMaterial(mat);}\n')
    # Include content must invalidate engines that key cached shaders by the wrapper.
    emit('tutnt/shaders/organic/environment.fp', '// Included sources: '+digest((core+environment).encode())+'\n#include "shaders/organic/relief.glsl"\n'
         '#define ENV_ORIGINAL_BODY SetupOrganicMaterial(mat);\n'
         '#define SetupMaterial OrganicEnvironment\n'
         '#include "shaders/environment/surface.glsl"\n'
         '#undef SetupMaterial\n#undef ENV_ORIGINAL_BODY\n'
         'void SetupMaterial(inout Material mat){OrganicEnvironment(mat);}\n')
    emit('tutnt/materials/organic/black.png',png_bytes(np.zeros((2,2,3),np.uint8)))
    bindings={};records=[];data_cache={}
    for m in config['materials']:
        if not 0<float(m['depth'])<=12:raise ValueError('Material depth must be in (0, 12]: '+m['name'])
        n=m['name'];entry=library.get(n,m);alias=entry.get('alias',n)
        band=alias.replace('X8','B') if alias.endswith('X8') else 'XB'+alias[2:]
        variants=list(dict.fromkeys([n]+[v for v in (alias,band) if v in definitions]))
        for v in variants:
            rgb,logical=resolve(v,entry['sources'])
            detail=m.get('height_detail')
            if detail and v!=n and detail.get('expanded_model'):
                detail=dict(detail['expanded_model'],kind='surface-structure')
            fingerprint=digest(rgb.tobytes()+json.dumps([logical,m['profile'],m['depth'],detail,traced_digest if detail and detail.get('kind')=='traced-geometry' else geometry_digest if m['profile']=='authored' else 'signed-127-v1']).encode())[:14]
            if fingerprint not in data_cache:
                h,nrm=relief(rgb,m['profile'],m['depth'],logical,detail)
                stem=f"materials/organic/{n.lower()}-{fingerprint}"
                emit('tutnt/'+stem+'-height.png',png_bytes(h));emit('tutnt/'+stem+'-normal.png',png_bytes(nrm))
                if m['profile']=='metal':emit('tutnt/'+stem+'-surface.png',png_bytes(metal_surface(rgb)))
                data_cache[fingerprint]=stem
            stem=data_cache[fingerprint]
            h=np.asarray(Image.open(io.BytesIO(outputs['tutnt/'+stem+'-height.png'])))
            limits=height_depth(h)
            bindings[v]=dict(stem=stem,depth=m['depth'],profile=m['profile'],family=n,logical=list(logical),size=[rgb.shape[1],rgb.shape[0]],data_size=[h.shape[1],h.shape[0]],neutral=127,base_height=PROFILE_BASE[m['profile']],min_depth=float(limits.min()),max_depth=float(limits.max()),trace_top=(-.5 if detail and detail.get('kind')=='traced-geometry' else PROFILE_BASE[m['profile']]-1),trace_bottom=(.5 if detail and detail.get('kind')=='traced-geometry' else PROFILE_BASE[m['profile']]),edge_mode=('band' if v==band else 'tile') if entry.get('edge_blend') and v!=n else None)
        records.append(dict(m,variants=variants))
    tables=[]
    env_bindings={}
    for p in sorted((mod/'environment').glob('*-surfaces.txt')):
        tables.append(p.relative_to(root).as_posix())
        for line in read(p).decode().splitlines():
            row=line.split('|')
            if len(row)>4 and row[3] in bindings:
                env_bindings[row[4]]=(bindings[row[3]],row[3])
    gldefs=['// Generated by tools/build_organic_materials.py. Include after environment materials.']
    def definition(name,m,env=False):
        shade={'rock':1.0,'gravel':.7,'soil':.5,'grass':.3,'snow':.55,'snowrock':.65,'ice':.4,'stonework':.55,'brick':.4,'metal':.28,'wood':.40,'technical':.38,'panel':.32,'mortar':.45,'authored':.35}[m['profile']]
        body=[f'Material "{name}" {{',f' Shader "shaders/organic/{"environment" if env else "material"}.fp"',
              f' Define ORGANIC_DEPTH = "{m["depth"]:.4f}"',
              # Profile-wide bounds keep compatible textures on a shared GPU program.
              f' Define ORGANIC_TRACE_TOP = "{m["trace_top"]:.9f}"',f' Define ORGANIC_TRACE_BOTTOM = "{m["trace_bottom"]:.9f}"',
              f' Define ORGANIC_BASE_HEIGHT = "{m["base_height"]:.4f}"',f' Define ORGANIC_SHADE = "{shade:.4f}"',
              f' Normal "{m["stem"]}-normal.png"', ' Specular "materials/organic/black.png"',
              f' Texture organicHeight "{m["stem"]}-height.png"']
        if m.get('edge_mode'):body += [' Define ORGANIC_'+m['edge_mode'].upper()+'_EDGE']
        if m['profile']=='ice':body += [' Define ORGANIC_ICE']
        if m['profile']=='metal':body += [' Define ORGANIC_METAL',f' Texture organicSurface "{m["stem"]}-surface.png"']
        if env:body += [f' Texture envMeta "materials/environment/{name}.png"',' Texture envState "UENVSTATE"']
        return '\n'.join(body+['}'])
    for n,m in sorted(bindings.items()):gldefs.append(definition(n,m))
    for n,(m,base) in sorted(env_bindings.items()):gldefs.append(definition(n,m,True))
    emit('tutnt/gldefs/GLDEFS.organic','\n\n'.join(gldefs)+'\n')
    manifest=dict(schema=2,height_encoding=dict(neutral=127,gain=HEIGHT_GAIN,profile_baselines=PROFILE_BASE),inputs=inputs,outputs={k:digest(v) for k,v in outputs.items()},
                  materials=records,variants=bindings,environment_tables=tables,bindings=len(bindings)+len(env_bindings),
                  environment_bindings={n:base for n,(m,base) in env_bindings.items()})
    # Write only changed bytes; the manifest is published after all owned outputs.
    for name,data in outputs.items():
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists() or p.read_bytes()!=data:p.write_bytes(data)
    # Remove only obsolete files previously recorded as this generator's output.
    if manifest_path.exists():
        for name in previous['outputs'].keys()-outputs.keys():
            p=(root/name).resolve()
            if not p.is_relative_to((mod/'materials/organic').resolve()):
                raise RuntimeError('Unexpected obsolete output: '+name)
            if p.is_file():p.unlink()
    manifest_path.write_text(json.dumps(manifest,indent=2)+'\n')
    return {'ok':True,'cached':False,'materials':len(records),'variants':len(bindings),'environment':len(env_bindings),'data_sets':len(data_cache),'bindings':manifest['bindings']}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--iwad',type=Path)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    print(json.dumps(generate(args.root,check=args.check,iwad=args.iwad),indent=2))
