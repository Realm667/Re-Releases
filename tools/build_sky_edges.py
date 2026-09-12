"""Build material-matched, noncolliding cornices at actual outdoor sky boundaries.

One-sided sky walls, exposed upper walls and closed sky sectors qualify. Ordinary outdoor steps,
architecture, liquids and horizon/portal lines do not. Geometry and UVs are
baked from current maps and area bindings; source WADs are never rewritten.
"""
from pathlib import Path
import argparse, collections, hashlib, json, math, re
from build_lava_lips import parse, tex, point, plus, sub, dot, norm

ROOT = Path(__file__).resolve().parents[1]
SNOW = {'ICEY', 'SNOW3', 'OSNOW', 'OSNOW3'}
ROCK = {'QROCK1', 'QROCK3', 'QROCK4', 'QROCK5', 'IKWALL44', 'ASHWALL2', 'ROCKF5'}

def plane(s, p, part='ceiling'):
    if part+'plane_c' in s:
        a,b,c,d = (float(s.get(part+'plane_'+k,0)) for k in 'abcd')
        if abs(c)<1e-9: raise ValueError('Vertical sector plane')
        return -(a*p[0]+b*p[1]+d)/c
    return float(s.get('height'+part,0))

def mapping(root, mapname):
    path=root/'tutnt/areaalign'/f'{mapname.lower()}.txt'
    rows={}
    if path.exists():
        for line in path.read_text().splitlines():
            r=line.split('|')
            if r[0] in ('W','P'):
                rows[tuple(map(int,r[1:4]))]=r
    return rows

def resolve_slopes(b, map_path=None):
    """Resolve authored slope setup before detecting the visual skyline.

    Mirrors the geometric contracts of UZDoom maploader/slopes.cpp: alignment
    to adjacent texture Z, triangle vertex heights, then explicit slope copies.
    This changes only the in-memory inspection, never the map file.
    """
    lines=collections.defaultdict(list)
    for l in b['linedef']:
        for key in ('sidefront','sideback'):
            si=int(l.get(key,-1))
            if si>=0:
                sec=int(b['sidedef'][si]['sector'])
                if l not in lines[sec]:lines[sec].append(l)
    def set_plane(sec,part,pts):
        p,a,c=pts;u=[a[i]-p[i] for i in range(3)];v=[c[i]-p[i] for i in range(3)]
        n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        if abs(n[2])<1e-8:return
        d=-sum(n[i]*p[i] for i in range(3))
        for k,value in zip('abcd',n+[d]):sec[part+'plane_'+k]=str(value)
    def side_ids(l):return [int(b['sidedef'][int(l[k])]['sector']) if int(l.get(k,-1))>=0 else -1 for k in ('sidefront','sideback')]
    for l in b['linedef']:
        if int(l.get('special',0))!=181:continue
        ids=side_ids(l)
        if min(ids)<0:continue
        a,c=[point(b['vertex'][int(l[k])]) for k in ('v1','v2')];dx,dy=sub(c,a)
        for part,arg in (('floor',0),('ceiling',1)):
            bits=int(l.get('arg'+str(arg),0))&3
            if arg==1 and bits==0:bits=(int(l.get('arg0',0))>>2)&3
            if bits not in (1,2):continue
            target=ids[bits-1];sec=b['sector'][target];ref=b['sector'][ids[2-bits]]
            vertices=[point(b['vertex'][int(line[k])]) for line in lines[target] for k in ('v1','v2')]
            far=max(vertices,key=lambda p:abs((p[0]-a[0])*dy-(p[1]-a[1])*dx))
            zh=float(ref.get('height'+part,0));zf=float(sec.get('height'+part,0))
            set_plane(sec,part,[(*a,zh),(*c,zh),(*far,zf)])
    for i,sec in enumerate(b['sector']):
        if len(lines[i])!=3:continue
        ids=list(dict.fromkeys(int(l[k]) for l in lines[i] for k in ('v1','v2')))
        if len(ids)!=3:continue
        for part in ('floor','ceiling'):
            if any('z'+part in b['vertex'][j] for j in ids):
                set_plane(sec,part,[(*point(b['vertex'][j]),float(b['vertex'][j].get('z'+part,sec.get('height'+part,0)))) for j in ids])
    def copy(source,target,part):
        src=b['sector'][source];dst=b['sector'][target]
        for k in 'abcd':dst[part+'plane_'+k]=src.get(part+'plane_'+k,str(-float(src.get('height'+part,0))) if k=='d' else '1' if k=='c' else '0')
    tags={}
    for i,sec in enumerate(b['sector']):
        for tag in [sec.get('id','0'),*sec.get('moreids','').strip('"').split()]:
            if int(tag):tags.setdefault(int(tag),i)
    if map_path is not None and b['sector']:
        from build_environment_fx import things, geometry, inside
        geo=geometry(b)
        for t in things(map_path):
            if int(t.get('type',0)) not in (9510,9511):continue
            source=tags.get(int(t.get('arg0',0)))
            if source is None:continue
            p=(float(t.get('x',0)),float(t.get('y',0)))
            target=next((i for i,edges in geo.items() if inside(p,edges)),None)
            if target is not None:copy(source,target,'floor' if int(t['type'])==9510 else 'ceiling')
    for l in b['linedef']:
        if int(l.get('special',0))!=118:continue
        ids=side_ids(l)
        for j in range(4 if ids[1]>=0 else 2):
            source=tags.get(int(l.get('arg'+str(j),0)))
            if source is not None:copy(source,ids[j//2],'ceiling' if j%2 else 'floor')
        if ids[1]<0:continue
        flag=int(l.get('arg4',0))
        for part,bits in (('floor',flag&3),('ceiling',(flag>>2)&3)):
            if bits in (1,2):copy(ids[bits-1],ids[2-bits],part)

def wall_uv(e, variants, bindings):
    s,l,front,back=e['side'],e['linedef'],e['front'],e['back']
    part=e['part'];suffix=('top','mid','bottom')[part]
    skin=e['texture'];sx=float(s.get('scalex_'+suffix,1));sy=float(s.get('scaley_'+suffix,1))
    ox=float(s.get('offsetx',0))+float(s.get('offsetx_'+suffix,0))
    oy=float(s.get('offsety',0))+float(s.get('offsety_'+suffix,0))
    oldsy=sy;oldox=ox;oldoy=oy;oldsx=sx
    w,h=variants[skin]['logical']
    fc=float(front.get('heightceiling',0));ff=float(front.get('heightfloor',0))
    bc=float(back.get('heightceiling',0)) if back else fc
    bf=float(back.get('heightfloor',0)) if back else ff
    peg=l.get('dontpegtop' if part==0 else 'dontpegbottom','false')=='true'
    def reference(height):
        if part==0:return fc if peg else bc+math.ceil(height/sy)
        if part==1:return ff+math.ceil(height/sy) if peg else fc
        return bc+math.ceil(height/sy) if peg else bf
    row=bindings.get((e['line'],e['face'],part))
    if row:
        if row[4]!=skin: raise ValueError('Stale area binding')
        skin=row[5];w,h=variants[skin]['logical']
        if row[0]=='W':
            sx=float(row[9]);ox=float(row[6]);oy=float(row[7])-reference(h)
        elif (not peg if part==0 else peg):
            oy-=(math.ceil(h/sy)-math.ceil(variants[e['texture']]['logical'][1]/sy))*sy
    return dict(skin=skin,width=w,height=h,sx=sx,sy=sy,ox=ox,oy=oy,ref=reference(h),
                oldsx=oldsx,oldsy=oldsy,oldox=oldox,oldoy=oldoy)

def detect(b, variants, bindings=None):
    edges=[];bindings=bindings or {}
    for index,l in enumerate(b['linedef']):
        # Horizon lines and portal boundaries need their own rendering treatment.
        if int(l.get('special',0)) in (9,156):continue
        for face,key in enumerate(('sidefront','sideback')):
            si=int(l.get(key,-1));oi=int(l.get(('sideback','sidefront')[face],-1))
            if si<0:continue
            side=b['sidedef'][si];front=b['sector'][int(side['sector'])]
            if tex(front,'textureceiling')!='F_SKY1':continue
            back=b['sector'][int(b['sidedef'][oi]['sector'])] if oi>=0 else None
            part=1 if back is None else 2 if tex(back,'textureceiling')=='F_SKY1' else 0
            texture=tex(side,('texturetop','texturemiddle','texturebottom')[part])
            material=variants.get(texture,{});family=material.get('family',texture)
            if family not in SNOW|ROCK:continue
            a,z=(point(b['vertex'][int(l[k])]) for k in ('v1','v2'))
            if face:a,z=z,a
            length=math.dist(a,z)
            if length<2:continue
            if any(abs(float(side.get('scale'+axis+('_top','_mid','_bottom')[part],1)))<1e-6 for axis in ('x','y')):continue
            if part==2:
                if tex(back,'textureceiling')!='F_SKY1':continue
                # A sky-backed terrace is NOT the end of the landscape.
                if any(plane(back,p,'floor')<plane(back,p,'ceiling')-.01 for p in (a,z)):continue
                top=back;top_part='floor';sec=int(b['sidedef'][oi]['sector'])
            else:top=front;top_part='ceiling';sec=int(side['sector'])
            heights=[plane(top,p,top_part) for p in (a,z)]
            clearance=min(heights[j]-max(plane(front,p,'floor'),plane(back,p,'ceiling') if part==0 else -math.inf) for j,p in enumerate((a,z)))
            if clearance<(8 if part==0 else 48):continue
            snow=family in SNOW
            radius=min(24 if snow else 22,clearance*.36 if part==0 else max(7,clearance*.075))
            t=norm(sub(z,a));n=(t[1],-t[0])
            e=dict(line=index,face=face,part=part,front_id=int(side['sector']),top_id=sec,
                   a=a,b=z,length=length,normal=n,texture=texture,family=family,
                   kind='snow' if snow else 'rock',radius=radius,h0=heights[0],h1=heights[1],
                   top=top,top_part=top_part,side=side,linedef=l,front=front,back=back)
            e['uv']=wall_uv(e,variants,bindings);edges.append(e)
    connect(edges)
    return edges

def connect(edges):
    joins=collections.defaultdict(list)
    for e in edges:
        for end,h in (('a','h0'),('b','h1')):
            key=(*e[end],round(e[h],3),e['kind'])
            joins[key].append((e,end))
    for peers in joins.values():
        for e,end in peers:
            e['m'+end]=e['normal'];e['r'+end]=0.0
            if len(peers)!=2:continue
            other=next(p for p,x in peers if p is not e)
            den=1+dot(e['normal'],other['normal'])
            if den<.4:continue
            e['m'+end]=tuple(v/den for v in plus(e['normal'],other['normal']))
            e['r'+end]=min(e['radius'],other['radius'])

def ridge(phase):
    # Piecewise-linear ridges keep rock outlines angular and deterministic.
    return 1.0-abs(phase%2.0-1.0)

def wave(p, snow):
    x,y=p
    broad=.76+.23*math.sin(x*.017+y*.013)+.16*math.sin(x*.039-y*.023)
    return broad if snow else .52+.54*ridge(x*.017+y*.013)+.22*ridge(x*.067-y*.043)

def profile(r,snow):
    # Starts hidden inside the solid wall, rounds over its top, projects out,
    # curls underneath, then meets the original vertical face with its normal.
    controls=[(-.28,-.35),(-.18,.20),(.04,.48),(.48,.36),(.94,.05),
              (1.0,-.32),(.77,-.70),(.33,-1.05),(.09,-1.50),(0,-2.10)]
    if not snow:
        # Broken shoulders and a narrow raised ridge, rather than a round roll.
        controls=[(-.28,-.35),(-.24,.40),(-.06,1.18),(.28,1.05),(.90,.30),
                  (1.02,-.22),(.65,-.76),(.28,-1.10),(.07,-1.52),(0,-2.10)]
        return [(d*r,z*r) for d,z in controls]
    # Catmull-Rom interpolation makes snow soft without changing end locations.
    result=[]
    for i in range(len(controls)-1):
        p0=controls[max(0,i-1)];p1=controls[i];p2=controls[i+1];p3=controls[min(len(controls)-1,i+2)]
        for j in range(3):
            t=j/3
            result.append(tuple(.5*((2*p1[k])+(-p0[k]+p2[k])*t+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*t*t+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*t*t*t)*r for k in (0,1)))
    result.append((0,-2.10*r));return result

def mesh(e):
    mid=plus(e['a'],sub(e['b'],e['a']),.5)
    # Put the actor's sector/light origin just inside the playable sector.
    center=plus(mid,e['normal'],.5);h=plane(e['top'],mid,e['top_part'])
    snow=e['kind']=='snow';steps=max(2,math.ceil(e['length']/(14 if snow else 18)))
    verts=[];uv=[];normals=[];faces=[];radii=[]
    for j in range(steps+1):
        u=j/steps;p=plus(e['a'],sub(e['b'],e['a']),u)
        m=plus(e['ma'],sub(e['mb'],e['ma']),u)
        # Limit each end locally; do not shrink an entire chain for a short line.
        ramp=min(1,j/2,(steps-j)/2)
        base=e['ra']*(1-u)+e['rb']*u
        r=(base*(1-ramp)+e['radius']*ramp)*wave(p,snow)
        r=max(.04,r);radii.append(r)
        rows=profile(r,snow)
        # Crest height varies independently of nose depth. Keep the hidden
        # rear and the wall seam fixed; raise only the upper curved shoulder.
        crest=r*(.12+.90*(.5+.5*math.sin(p[0]*.025+p[1]*.019))+.45*(.5+.5*math.sin(p[0]*.051-p[1]*.033)))
        if not snow:
            crest=r*(.18+1.05*ridge(p[0]*.026+p[1]*.019)+.62*ridge(p[0]*.081-p[1]*.057))
        rows=[(d,z+crest*math.sin(math.pi*min(1,k/(len(rows)-1)/.72))**2) for k,(d,z) in enumerate(rows)]
        arc=[0.0]*len(rows)
        for k in range(len(rows)-2,-1,-1):arc[k]=arc[k+1]+math.dist(rows[k],rows[k+1])
        for k,(d,z) in enumerate(rows):
            w=plus(p,m,d+.025);worldz=plane(e['top'],p,e['top_part'])+z
            verts.append((w[0]-center[0],worldz-h,-(w[1]-center[1])))
            c=e['uv']
            # Match the wall exactly at the lower seam; bend the texture over
            # the top rather than stretch a single row across the upper cap.
            wrappedz=plane(e['top'],p,e['top_part'])+rows[-1][1]+arc[k]
            uu=(u*e['length']*c['sx']+c['ox'])/c['width']
            vv=((c['ref']-wrappedz)*c['sy']+c['oy'])/c['height']
            uv.append((uu,1-vv))
            before=rows[max(0,k-1)];after=rows[min(len(rows)-1,k+1)]
            dd,dz=after[0]-before[0],after[1]-before[1];n=norm(m)
            nx,ny,nz=-dz*n[0],-dz*n[1],dd
            if k==len(rows)-1:nx,ny,nz=n[0],n[1],0
            size=math.sqrt(nx*nx+ny*ny+nz*nz) or 1
            normals.append((nx/size,nz/size,-ny/size))
    count=len(rows)
    for j in range(steps):
        for k in range(count-1):
            a=j*count+k+1;b=a+count
            faces.extend(((a,b,b+1),(a,b+1,a+1)))
    face_normals=[]
    for i,f in enumerate(faces):
        band=(i//2)%(count-1)
        if snow or band>=6:
            face_normals.append(f);continue
        # Both triangles share a rock facet; lower bands keep smooth wall normals.
        if i%2==0:
            a,b,c=f;v=verts[a-1];across=[verts[b-1][k]-v[k] for k in range(3)]
            down=[verts[a][k]-v[k] for k in range(3)]
            n=[down[1]*across[2]-down[2]*across[1],down[2]*across[0]-down[0]*across[2],down[0]*across[1]-down[1]*across[0]]
            size=math.sqrt(sum(x*x for x in n)) or 1
            normals.append(tuple(x/size for x in n));ni=len(normals)
        face_normals.append((ni,ni,ni))
    out=['# Generated sky cornice; visual geometry only.','s 1']
    out+=['v %.6f %.6f %.6f'%v for v in verts]
    out+=['vt %.8f %.8f'%v for v in uv]
    out+=['vn %.6f %.6f %.6f'%v for v in normals]
    out+=['f '+' '.join(f'{v}/{v}/{n}' for v,n in zip(f,ns)) for f,ns in zip(faces,face_normals)]
    return '\n'.join(out)+'\n',center,h,len(faces),verts

def generate(root=ROOT,check=False):
    root=Path(root);variants=json.loads((root/'tools/organic-materials/generated.json').read_text())['variants']
    outputs={};models=[];actors=[];records=[];skins=set();glow_sectors={};skin_bindings={}
    def glow_skin(skin,slot):
        key=(skin,slot)
        if key not in skin_bindings:skin_bindings[key]=f"SG{len(skin_bindings):06d}"
        return skin_bindings[key]
    for path in sorted((root/'tutnt/maps').glob('*.wad')):
        b=parse(path);resolve_slopes(b,path);edges=detect(b,variants,mapping(root,path.stem));rows=[]
        envpath=root/'tutnt/environment'/f'{path.stem}-surfaces.txt'
        environment={}
        if envpath.exists():
            for line in envpath.read_text().splitlines():
                r=line.split('|')
                if r[0]=='1':environment[(int(r[1]),int(r[2]),r[3])]=r[4]
        for e in edges:
            obj,center,h,triangles,verts=mesh(e)
            stem=f'{path.stem}-{e["line"]}-{e["face"]}'
            cls='UTNTSkyEdge_'+stem.replace('-','_');c=e['uv']
            sector_key=(path.stem,e['front_id'])
            if sector_key not in glow_sectors:glow_sectors[sector_key]=len(glow_sectors)
            slot=glow_sectors[sector_key];primary=glow_skin(c['skin'],slot)
            outputs[f'tutnt/models/sky-edges/{stem}.obj']=obj
            extent=math.ceil(max(math.sqrt(v[0]**2+v[2]**2) for v in verts)+8)
            actors.append(f'class {cls} : UTNTSkyEdge {{ Default {{ RenderRadius {extent}; }} }}')
            # UZDoom's model scale has an implicit 1/1.2 vertical correction.
            models.append(f'Model {cls}\n{{\n Path "models/sky-edges/"\n Model 0 "{stem}.obj"\n Skin 0 "{primary}"\n Scale 1 1 1.2\n DontCullBackfaces\n FrameIndex SKED A 0 0\n}}')
            row=[cls,e['line'],e['face'],e['part'],e['front_id'],e['top_id'],*e['a'],*e['b'],*center,h,e['h0'],e['h1'],e['texture'],c['skin'],c['sx'],c['sy'],c['ox'],c['oy'],e['radius'],e['kind'],environment.get((int(e['linedef']['sidefront' if e['face']==0 else 'sideback']),e['part'],c['skin']),'-')]
            alternate=glow_skin(row[-1],slot) if row[-1]!='-' else '-'
            row.extend([primary,alternate,slot])
            skins.add(c['skin'])
            if row[23]!='-':skins.add(row[23])
            rows.append('|'.join(str(x) for x in row))
            records.append({k:e[k] for k in ('line','face','part','front_id','top_id','a','b','kind','family','texture','radius','h0','h1')}|dict(map=path.stem.upper(),skin=c['skin'],center=[*center,h],triangles=triangles))
        if rows:outputs[f'tutnt/skyedges/{path.stem}.txt']='\n'.join(rows)+'\n'
    # Clone the existing texture/material definitions so terrain relief and
    # weather remain authoritative. Only macro underside shading is added.
    from build_environment_fx import blocks
    textures={};materials={}
    files=[root/'tutnt/TEXTURES.txt',*sorted((root/'tutnt/textures/definitions').glob('*'))]
    for path in files:
        if path.name=='TEXTURES.sky-edges':continue
        for m,body in blocks(path.read_text(),r'\b(?:texture|flat|graphic)\s+"?([\w.-]+)"?\s*,\s*(\d+)\s*,\s*(\d+)'):
            textures[m[1].upper()]=(int(m[2]),int(m[3]),body)
    for m,body in blocks((root/'tutnt/gldefs/GLDEFS.organic').read_text(),r'\bmaterial\s+(?:(?:flat|texture)\s+)?"?([\w.-]+)"?'):
        materials[m[1].upper()]=body
    texturedefs=[];materialdefs=[]
    import struct,zlib
    def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    for slot in glow_sectors.values():
        pixel=bytes((slot>>16,(slot>>8)&255,slot&255))
        outputs[f'tutnt/materials/sky-edges/glow-{slot}.png']=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b'\0'+pixel))+chunk(b'IEND',b'')
    for (skin,slot),alias in skin_bindings.items():
        if skin in textures:w,h,body=textures[skin]
        else:
            v=variants[skin];w,h=v['size'];lw,lh=v['logical']
            body=f' XScale {w/lw}\n YScale {h/lh}\n Patch "{skin}", 0, 0\n'
        texturedefs.append(f'Texture "{alias}", {w}, {h}\n{{\n{body}\n}}')
        body=materials[skin]
        match=re.search(r'Shader\s+"([^"]+)"',body)
        original=match[1];target='shaders/sky-edges/'+Path(original).name
        if 'tutnt/'+target not in outputs:
            source=(root/'tutnt'/original).read_text()
            entry='void SetupMaterial(inout Material mat)'
            if source.count(entry)!=1:raise ValueError('Sky-edge shader wrapper needs updating: '+original)
            source=source.replace(entry,'void SkyEdgeOriginal(inout Material mat)')
            source+='#include "shaders/skyedges/ceiling_glow.glsl"\n'
            source+='\nvoid SetupMaterial(inout Material mat)\n{\n SkyEdgeOriginal(mat);\n float up=normalize(vWorldNormal.xyz).y;\n mat.Base.rgb*=1.0+0.12*max(up,0.0)-0.48*max(-up,0.0);\n SkyEdgeCeilingGlow(mat);\n}\n'
            outputs['tutnt/'+target]=source
        body=body.replace(original,target)
        body+=f'\n Texture skyGlowMeta "materials/sky-edges/glow-{slot}.png"\n Texture skyGlowState "USKYGLOW"\n'
        materialdefs.append(f'Material "{alias}" {{\n{body}\n}}')
    outputs['tutnt/textures/definitions/TEXTURES.sky-edges']='\n'.join(texturedefs)+'\n'
    outputs['tutnt/gldefs/GLDEFS.sky-edges']='\n'.join(materialdefs)+'\n'
    outputs['tutnt/zscript/sky-edges-generated.zc']='// Generated by tools/build_sky_edges.py.\n'+'\n'.join(actors)+'\n'
    outputs['tutnt/modeldef/MODELDEF.sky-edges']='\n'.join(models)+'\n'
    import base64
    outputs['tutnt/sprites/SKEDA0.png']=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR4nGNgAAIAAAUAAarVyFEAAAAASUVORK5CYII=')
    manifest=dict(schema=2,glow_sectors=len(glow_sectors),glow_materials=len(skin_bindings),rule='one-sided/upper sky walls or closed sky sectors; material allowlist',snow=sorted(SNOW),rock=sorted(ROCK),edges=records)
    outputs['tools/sky-edges-manifest.json']=json.dumps(manifest,indent=2)+'\n'
    inventory=root/'tools/sky-edges-outputs.json'
    previous=json.loads(inventory.read_text()) if inventory.exists() else []
    stale=[]
    for rel in previous:
        if rel not in outputs and re.fullmatch(r'tutnt/(?:models/sky-edges/[\w-]+\.obj|skyedges/[\w-]+\.txt|materials/sky-edges/glow-\d+\.png)',rel):
            p=(root/rel).resolve();p.relative_to(root.resolve())
            if p.exists():stale.append(p)
    outputs['tools/sky-edges-outputs.json']=json.dumps(sorted(outputs),indent=2)+'\n'
    changed=[]
    for rel,data in outputs.items():
        path=root/rel;data=data.encode() if isinstance(data,str) else data
        if path.exists() and path.read_bytes()==data:continue
        changed.append(rel)
        if not check:
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    if check and (changed or stale):raise RuntimeError('Stale sky-edge assets: '+', '.join(changed[:8]))
    if not check:
        for path in stale:path.unlink()
    return dict(edges=len(records),maps=dict(collections.Counter(r['map'] for r in records)),kinds=dict(collections.Counter(r['kind'] for r in records)),triangles=sum(r['triangles'] for r in records),updated=len(changed))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,default=ROOT);ap.add_argument('--check',action='store_true');args=ap.parse_args()
    print(json.dumps(generate(args.root,args.check),indent=2))
