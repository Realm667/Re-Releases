"""Build organic relief data and bindings without changing diffuse textures or maps.

Requires NumPy and Pillow. --check verifies all recorded inputs and outputs.
The regular UTNT build regenerates only this tool's outputs when inputs change.
"""
from pathlib import Path
import argparse, hashlib, io, json, math, os, re, struct
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent

def digest(data):
    return hashlib.sha256(data).hexdigest()

def texture_defs(mod):
    result = {}
    for p in sorted(mod.glob('TEXTURES*')):
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

def relief(rgb, profile, depth, logical):
    lum = np.asarray(rgb,np.float32)/255 @ np.array([.2126,.7152,.0722],np.float32)
    soft = wrap_blur(lum,.9)
    lo,hi = np.quantile(soft,[.16,.91])
    face = np.clip((soft-lo)/max(hi-lo,.001),0,1)
    if profile in ('rock','gravel'):
        dist = np.where(face<.14,0,32).astype(np.float32)
        for _ in range(14):
            values = [dist]
            for y,x in ((0,1),(0,-1),(1,0),(-1,0),(1,1),(-1,1),(1,-1),(-1,-1)):
                values.append(np.roll(np.roll(dist,y,0),x,1)+math.hypot(x,y))
            dist = np.minimum.reduce(values)
        crown = np.sqrt(np.clip(dist/7.5,0,1))
        h = wrap_blur(.72*crown+.28*face,.8)*.92+.04
    else:
        # Fine ground: continuous shallow relief instead of separated rock crowns.
        broad = wrap_blur(face,2.5)
        h = wrap_blur(.55*face+.45*broad,1.0)*.72+.14
    dx = (np.roll(h,-1,1)-np.roll(h,1,1))*.5*depth*h.shape[1]/logical[0]
    dy = (np.roll(h,-1,0)-np.roll(h,1,0))*.5*depth*h.shape[0]/logical[1]
    normal = np.stack((-dx,dy,np.ones_like(h)),axis=2)
    normal /= np.linalg.norm(normal,axis=2,keepdims=True)
    return np.uint8(np.clip(h,0,1)*255), np.uint8(np.clip(normal*.5+.5,0,1)*255)

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
    config=json.loads(read(config_path))
    library={m['name']:m for m in json.loads(read(root/'tools/artwork/area-textures/materials.json'))}
    for p in sorted(mod.glob('TEXTURES*')):
        if p.is_file() and not p.name.startswith('TEXTURES.environment'):read(p)
    definitions=texture_defs(mod)
    palette=np.frombuffer(read(mod/'PLAYPAL.pal')[:768],np.uint8).reshape(256,3)
    lumps=None
    def iw_flat(name):
        nonlocal lumps
        if lumps is None:
            b=read(iwad);_,n,o=struct.unpack_from('<4sII',b)
            lumps={key.rstrip(b'\0').decode():b[a:a+size] for a,size,key in (struct.unpack_from('<II8s',b,o+i*16) for i in range(n))}
        return patch_rgb(lumps[name],palette,True)
    files={}; file_rank={}
    for folder in ('flats','textures','patches'):
        for p in sorted((mod/folder).rglob('*')):
            if p.is_file() and p.suffix.lower() in ('.lmp','.png'):
                key=p.stem.upper()
                rank=({'textures':0,'flats':1,'patches':2}[folder],0 if p.suffix.lower()=='.png' else 1)
                if key not in file_rank or rank<file_rank[key]:
                    files[key]=p;file_rank[key]=rank
    def resolve(name, fallback):
        if name in definitions:
            w,h,scales,patches=definitions[name]
            if len(patches)!=1 or patches[0][1:]!=('0','0'):
                raise ValueError('Review composite material '+name)
            path=mod/patches[0][0]
            if not path.exists():
                path=files.get(Path(patches[0][0]).stem.upper())
            if path is None:raise FileNotFoundError(name)
            rgb=patch_rgb(read(path),palette,'flats' in path.relative_to(mod).parts)
            # TEXTURES can expose a cropped band or repeat a smaller legacy patch.
            rgb=rgb[np.arange(h)%rgb.shape[0]][:,np.arange(w)%rgb.shape[1]]
            return rgb,(w/scales[0],h/scales[1])
        if fallback[0].startswith('DOOM2.WAD:') and (name not in file_rank or file_rank[name][0]==2):
            rgb=iw_flat(fallback[0].split(':')[1])
        elif name in files:
            path=files[name];rgb=patch_rgb(read(path),palette,'flats' in path.relative_to(mod).parts)
        elif fallback[0].startswith('DOOM2.WAD:'):rgb=iw_flat(fallback[0].split(':')[1])
        else:
            path=root/fallback[0].replace('\\','/');rgb=patch_rgb(read(path),palette,'flats' in path.relative_to(mod).parts)
        return rgb,(rgb.shape[1],rgb.shape[0])
    core=read(mod/'shaders/organic/relief.glsl').decode()
    environment=read(mod/'shaders/environment/surface.glsl').decode()
    assert environment.count('ENV_ORIGINAL_BODY')==1
    emit('tutnt/shaders/organic/material.fp','#include "shaders/organic/relief.glsl"\nvoid SetupMaterial(inout Material mat){SetupOrganicMaterial(mat);}\n')
    emit('tutnt/shaders/organic/environment.fp', '#include "shaders/organic/relief.glsl"\n'
         '#define ENV_ORIGINAL_BODY SetupOrganicMaterial(mat);\n'
         '#define SetupMaterial OrganicEnvironment\n'
         '#include "shaders/environment/surface.glsl"\n'
         '#undef SetupMaterial\n#undef ENV_ORIGINAL_BODY\n'
         'void SetupMaterial(inout Material mat){OrganicEnvironment(mat);}\n')
    emit('tutnt/materials/organic/black.png',png_bytes(np.zeros((2,2,3),np.uint8)))
    bindings={};records=[];data_cache={}
    for m in config['materials']:
        n=m['name'];entry=library[n];alias=entry['alias']
        band=alias.replace('X8','B') if alias.endswith('X8') else 'XB'+alias[2:]
        variants=[n]+[v for v in (alias,band) if v in definitions]
        for v in variants:
            rgb,logical=resolve(v,entry['sources'])
            fingerprint=digest(rgb.tobytes()+json.dumps([logical,m['profile'],m['depth']]).encode())[:14]
            if fingerprint not in data_cache:
                h,nrm=relief(rgb,m['profile'],m['depth'],logical)
                stem=f"materials/organic/{n.lower()}-{fingerprint}"
                emit('tutnt/'+stem+'-height.png',png_bytes(h));emit('tutnt/'+stem+'-normal.png',png_bytes(nrm))
                data_cache[fingerprint]=stem
            stem=data_cache[fingerprint]
            bindings[v]=dict(stem=stem,depth=m['depth'],profile=m['profile'],family=n,logical=list(logical),size=[rgb.shape[1],rgb.shape[0]])
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
        shade={'rock':1.0,'gravel':.7,'soil':.5,'grass':.3}[m['profile']]
        body=[f'Material "{name}" {{',f' Shader "shaders/organic/{"environment" if env else "material"}.fp"',
              f' Define ORGANIC_DEPTH = "{m["depth"]:.4f}"',f' Define ORGANIC_SHADE = "{shade:.4f}"',
              f' Normal "{m["stem"]}-normal.png"', ' Specular "materials/organic/black.png"',
              f' Texture organicHeight "{m["stem"]}-height.png"']
        if env:body += [f' Texture envMeta "materials/environment/{name}.png"',' Texture envState "UENVSTATE"']
        return '\n'.join(body+['}'])
    for n,m in sorted(bindings.items()):gldefs.append(definition(n,m))
    for n,(m,base) in sorted(env_bindings.items()):gldefs.append(definition(n,m,True))
    emit('tutnt/GLDEFS.organic','\n\n'.join(gldefs)+'\n')
    manifest=dict(schema=1,inputs=inputs,outputs={k:digest(v) for k,v in outputs.items()},
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
