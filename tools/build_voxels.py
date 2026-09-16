"""Import selected Cheello voxels and build UTNT pickups from original lowres art.

Use --source <unpacked Voxel Doom folder> --iwad <DOOM2.WAD> for the initial
palette-aware import. Subsequent builds use committed imported KVX files.
--check compares deterministic custom output and validates every native KVX.
"""
from pathlib import Path
import argparse,hashlib,json,struct
from voxel_geometry import build as build_geometry
ROOT=Path(__file__).resolve().parent.parent
ART=Path('tools/artwork/voxels');DEST=Path('tutnt/voxels')
# actor, source sprite prefix, frames, degrees/sec, original source angle offset
IMPORTED=[
 ('Clip','CLIP','A',0,270),('Backpack','BPAK','A',0,0),('ClipBox','AMMO','A',0,270),
 ('RocketBox','BROK','A',0,270),('Cell','CELL','A',0,0),('CellPack','CELP','A',0,0),
 ('RocketAmmo','ROCK','A',0,0),('FloatingSkull','FSKU','ABC',0,0),
 ('BlueArmor','ARM2','AB',20,0),('GreenArmor','ARM1','AB',20,0),
 ('Medikit','MEDI','A',0,270),('Stimpack','STIM','A',0,270),
 ('Candelabra','CBRA','A',0,0),('Candlestick','CAND','A',0,0),
 ('Berserk','PSTR','A',0,0),('Infrared','PVIS','AB',0,0),('RadSuit','SUIT','A',0,0),
 ('Allmap','PMAP','ABCD',0,0),('Shell','SHEL','A',0,0),('ShellBox','SBOX','A',0,0),
 ('BlueCard','BKEY','AB',70,0),('YellowCard','YKEY','AB',70,0),('RedCard','RKEY','AB',70,0),
 ('BlueSkull','BSKU','AB',70,0),('YellowSkull','YSKU','AB',70,0),('RedSkull','RSKU','AB',70,0),
 ('ArmorBonus','BON2','ABCD',20,0),('HealthBonus','BON1','ABCD',20,0),
 ('UTNTBFG9000','BFUG','A',20,0),('UTNTChaingun','MGUN','A',20,0),
 ('UTNTChainsaw','CSAW','A',20,0),('UTNTPistol','PIST','A',20,0),
 ('UTNTPlasmaRifle','PLAS','A',20,0),('UTNTRocketLauncher','LAUN','A',20,0),
 ('UTNTShotgun','SHOT','A',20,0),('UTNTSuperShotgun','SGN2','A',20,0),
 ('ExplosiveBarrel','BAR1','AB',0,270),('ExplosiveBarrel','BEXP','ABCDE',0,270)]
CUSTOM=[
 ('Gas','AGAS','A','gas',0),('BigGas','AGAS','B','biggas',0),
 ('UTNTFlamer','WFLM','A','flamer',20),('UTNTPyroCannon','WPRY','A','pyro',20),
 ('UTNTMinigun','MNGN','A','minigun',0),('PortalCoreHeart','PHRT','ABCD','heart',0),
 ('UTNT_Barrel','FCAN','A','barrel',0),('CandelabraNew','T6CB','A','candelabra',0)]


def sha(b):return hashlib.sha256(b).hexdigest()
def wad_lump(path,wanted):
    data=Path(path).read_bytes();n,o=struct.unpack_from('<ii',data,4)
    for i in range(n):
        pos,size,name=struct.unpack_from('<ii8s',data,o+i*16)
        if name.rstrip(b'\0').decode()==wanted:return data[pos:pos+size]
    raise ValueError('Missing IWAD lump '+wanted)
def patch(data):
    w,h,left,top=struct.unpack_from('<hhhh',data);pixels={}
    if not (0<w<256 and 0<h<256):raise ValueError('Expected original lowres Doom patch')
    for x in range(w):
        pos=struct.unpack_from('<I',data,8+x*4)[0];last=-1
        while data[pos]!=255:
            z,n=data[pos:pos+2]
            if z<=last:z+=last
            last=z
            for i,c in enumerate(data[pos+3:pos+3+n]):pixels[x,z+i]=c
            pos+=n+4
    return w,h,left,top,pixels

def inspect_kvx(data,remap=None):
    """Validate all MIPs, column boundaries, slabs and palette; optionally remap."""
    out=bytearray(data);pos=0;mips=[]
    while pos<len(data)-768:
        n,xs,ys,zs,px,py,pz=struct.unpack_from('<7i',data,pos)
        if not (0<xs<1024 and 0<ys<1024 and 0<zs<=256):raise ValueError('Invalid KVX bounds')
        start=pos+28;offsize=(xs+1)*4+xs*(ys+1)*2;end=pos+4+n
        if end>len(data)-768 or end<start+offsize:raise ValueError('Invalid KVX mip size')
        xo=struct.unpack_from('<'+'I'*(xs+1),data,start)
        if xo[0]!=offsize or start+xo[-1]!=end:raise ValueError('Invalid KVX x table')
        count=0
        for x in range(xs):
            yo=struct.unpack_from('<'+'H'*(ys+1),data,start+(xs+1)*4+x*(ys+1)*2)
            if yo[0]!=0 or yo[-1]!=xo[x+1]-xo[x]:raise ValueError('Invalid KVX y table')
            for y in range(ys):
                at=start+xo[x]+yo[y];stop=start+xo[x]+yo[y+1];prev=-1
                while at<stop:
                    top,length,mask=data[at:at+3]
                    if not length or top<=prev or top+length>zs or at+3+length>stop:raise ValueError('Invalid KVX slab')
                    if mask & ~63:raise ValueError('Invalid KVX face mask')
                    if remap is not None:out[at+3:at+3+length]=bytes(remap[c] for c in data[at+3:at+3+length])
                    count+=length;prev=top+length-1;at+=3+length
                if at!=stop:raise ValueError('KVX column overrun')
        mips.append({'size':[xs,ys,zs],'pivot':[px/256,py/256,pz/256],'surface_voxels':count});pos=end
    if pos!=len(data)-768 or not mips:raise ValueError('Invalid KVX palette boundary')
    return bytes(out),mips

def encode(vox,dims,pivot,palette):
    xs,ys,zs=dims;xo=[];yo=[];slabs=bytearray();offsetsize=(xs+1)*4+xs*(ys+1)*2
    for x in range(xs):
        xo.append(offsetsize+len(slabs));start=len(slabs)
        for y in range(ys):
            yo.append(len(slabs)-start)
            for z in range(zs):
                if (x,y,z) not in vox:continue
                mask=0
                for bit,(dx,dy,dz) in enumerate(((-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1))):
                    if (x+dx,y+dy,z+dz) not in vox:mask|=1<<bit
                if mask:slabs.extend((z,1,mask,vox[x,y,z]))
        yo.append(len(slabs)-start)
    xo.append(offsetsize+len(slabs))
    body=struct.pack('<6i',xs,ys,zs,*(round(p*256) for p in pivot))+struct.pack('<'+'I'*len(xo),*xo)+struct.pack('<'+'H'*len(yo),*yo)+slabs
    return struct.pack('<I',len(body))+body+bytes(c//4 for c in palette)

def build(root=ROOT,source=None,iwad=None,check=False):
    root=Path(root);dest=root/DEST;art=root/ART;palette=(root/'tutnt/PLAYPAL.pal').read_bytes()[:768]
    records=[];actors=[];defs=['// Generated by tools/build_voxels.py. Selected Cheello models and original-lowres UTNT models.',
      '// OverridePalette uses the active UTNT PLAYPAL. Import indices are converted to Doom order.',
      '// Spin: stationary 0; slow 20 degrees/sec; keys 70 degrees/sec.']
    old=json.loads((art/'manifest.json').read_text()) if (art/'manifest.json').exists() else {'models':[]}
    oldmodels={m['sprite']:m for m in old['models']};changed=[]
    def output(path,data):
        previous=path.read_bytes() if path.exists() else None
        if previous is not None and path.suffix.lower() in ('.txt','.json'):
            previous=previous.replace(b'\r\n',b'\n')
        if previous!=data:
            changed.append(path.relative_to(root).as_posix())
            if not check:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    for actor,prefix,frames,spin,angle in IMPORTED:
        entry=next((a for a in actors if a['actor']==actor),None)
        if entry is None:
            actors.append({'actor':actor,'sprite':prefix,'frames':frames,'spin':spin,'origin':'Cheello'})
        else:
            entry.setdefault('extra_states',[]).append({'sprite':prefix,'frames':frames,'spin':spin})
        for frame in frames:
            sprite=prefix+frame;name='CV'+sprite;target=dest/(name+'.kvx')
            if source:
                candidates=list(Path(source).rglob(sprite+'.kvx'))
                if len(candidates)!=1:raise ValueError(f'Expected one source {sprite}: {candidates}')
                f=candidates[0];raw=f.read_bytes();doom=wad_lump(iwad,'PLAYPAL')[:768]
                # Source palettes are re-ordered. Find exact 6-bit Doom colors first;
                # nearest-color fallback accommodates other compatible source versions.
                colors=[tuple(c//4 for c in doom[i:i+3]) for i in range(0,768,3)]
                mapping=[min(range(256),key=lambda j:sum((colors[j][k]-raw[-768+i*3+k])**2 for k in range(3))) for i in range(256)]
                data,_=inspect_kvx(raw,mapping);data=data[:-768]+bytes(c//4 for c in palette)
                output(target,data)
                record={'sprite':sprite,'source':f.relative_to(source).as_posix(),'source_sha256':sha(raw)}
            else:
                data=target.read_bytes();record={k:v for k,v in oldmodels[sprite].items() if k in ('sprite','source','source_sha256')}
            _,mips=inspect_kvx(data);record.update(file=target.relative_to(root).as_posix(),sha256=sha(data),mips=mips);records.append(record)
            defs.append(f'{sprite} = "{name}" {{ OverridePalette Spin = {spin}'+(f' AngleOffset = {angle}' if angle else '')+' }')
    for actor,prefix,frames,kind,spin in CUSTOM:
        actors.append({'actor':actor,'sprite':prefix,'frames':frames,'spin':spin,'origin':'UTNT lowres','geometry':kind})
        for frame in frames:
            sprite=prefix+frame
            f=art/'sources/MNGNA0.lmp' if prefix=='MNGN' else next((root/'tutnt/sprites').rglob(sprite+'0.lmp'))
            raw=f.read_bytes();w,h,left,top,p=patch(raw)
            v,dims,pivot=build_geometry(kind,p,w,h,palette);data=encode(v,dims,pivot,palette)
            name='UV'+sprite;target=dest/(name+'.kvx');output(target,data);_,mips=inspect_kvx(data)
            records.append({'sprite':sprite,'source':f.relative_to(root).as_posix(),'source_sha256':sha(raw),'file':target.relative_to(root).as_posix(),'sha256':sha(data),'geometry':kind,'source_size':[w,h],'solid_voxels':len(v),'mips':mips})
            defs.append(f'{sprite} = "{name}" {{ OverridePalette Spin = {spin} }}')
    from grenade_voxel import geometry, fallback
    v,dims,pivot,palette,source=geometry(root)
    data=encode(v,dims,pivot,palette);target=dest/'UVUGRNA.kvx'
    output(target,data);output(root/'tutnt/sprites/UGRNA0.lmp',fallback(v,dims))
    _,mips=inspect_kvx(data)
    records.append({'sprite':'UGRNA','source':source.relative_to(root).as_posix(),'source_sha256':sha(source.read_bytes().replace(b'\r\n',b'\n')),'file':target.relative_to(root).as_posix(),'sha256':sha(data),'geometry':'grenade','solid_voxels':len(v),'mips':mips})
    actors.append({'actor':'UTNTGrenade','sprite':'UGRN','frames':'A','spin':0,'origin':'UTNT authored','geometry':'grenade'})
    defs.append('UGRNA = "UVUGRNA" { OverridePalette Spin = 0 UseActorPitch UseActorRoll }')
    output(root/'tutnt/VOXELDEF.txt',('\n'.join(defs)+'\n').encode())
    manifest={'palette':'tutnt/PLAYPAL.pal','palette_mode':'native OverridePalette; imported source indices normalized to Doom order','slow_spin':20,'key_spin':70,'minigun_source':'75f81f1fc^:tutnt/sprites/MNGNA0.lmp','actors':actors,'models':records}
    output(art/'manifest.json',(json.dumps(manifest,indent=2)+'\n').encode())
    if check and changed:raise ValueError('Stale voxel outputs: '+', '.join(changed))
    return {'actors':len(actors),'models':len(records),'changed':changed,'ok':True}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--source',type=Path);p.add_argument('--iwad',type=Path);p.add_argument('--check',action='store_true');a=p.parse_args()
    if a.source and not a.iwad:p.error('--source requires --iwad')
    print(json.dumps(build(**vars(a)),indent=2))
