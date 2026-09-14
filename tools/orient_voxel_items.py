"""Audit each mapped voxel placement; orient stationary items into nearby open space.

Only UDMF or binary thing angles are edited. No geometry, nodes, scripts, flags or IDs change.
Default is read-only; --apply writes reviewed proposals and retains exact backups.
All evidence is under tutnt/.codex. Native rotating items retain their motion.
"""
from pathlib import Path
import argparse, collections, hashlib, json, math, re, struct
from build_utnt import read_wad, write_wad
from build_lava_lips import parse, point, height
from build_environment_fx import geometry, bounds, inside
from build_voxels import IMPORTED

ROOT = Path(__file__).resolve().parent.parent
# Native Doom editor numbers and UTNT DECORATE numbers, after replacements.
TYPES = {
    2007:'Clip', 8:'Backpack', 2048:'ClipBox', 2046:'RocketBox',
    2047:'Cell', 17:'CellPack', 2010:'RocketAmmo', 42:'FloatingSkull',
    2019:'BlueArmor', 2018:'GreenArmor', 2012:'Medikit', 2011:'Stimpack',
    35:'Candelabra', 34:'Candlestick', 2023:'Berserk', 2045:'Infrared',
    2025:'RadSuit', 2026:'Allmap', 2008:'Shell', 2049:'ShellBox',
    5:'BlueCard', 6:'YellowCard', 13:'RedCard', 40:'BlueSkull',
    39:'YellowSkull', 38:'RedSkull', 2015:'ArmorBonus', 2014:'HealthBonus',
    2006:'UTNTBFG9000', 2002:'UTNTChaingun', 2005:'UTNTChainsaw',
    2004:'UTNTPlasmaRifle', 2003:'UTNTRocketLauncher', 2001:'UTNTShotgun',
    82:'UTNTSuperShotgun', 2035:'ExplosiveBarrel', 20106:'Gas',
    20195:'BigGas', 20105:'UTNTFlamer', 20107:'UTNTPyroCannon',
    20039:'UTNTMinigun', 18999:'PortalCoreHeart', 70:'UTNT_Barrel',
    31991:'CandelabraNew',
}
# Cylindrical objects have no preferred horizontal presentation face.
# Native VOXELDEF import offsets rotate the visible front relative to Actor.Angle.
FRONT_OFFSET = {entry[0]:entry[4] for entry in IMPORTED}
SYMMETRIC = {'RocketAmmo', 'Candlestick', 'Gas', 'UTNT_Barrel', 'ExplosiveBarrel'}
BLOCK = re.compile(r'\bthing\s*(?://[^\n]*\n\s*)?\{([^}]*)\}')
FIELD = re.compile(r'(\w+)\s*=\s*([^;]+);')
ANGLE = re.compile(r'(\bangle\s*=\s*)([^;]+)(;)')


def nearest(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    length2 = dx*dx+dy*dy
    if length2 < 1e-9:
        return a
    t = max(0, min(1, ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/length2))
    return (a[0]+t*dx, a[1]+t*dy)



def inward_angle(p, walls, old):
    """Nearest wall normal; combine corner normals without attracting distant walls."""
    candidates = []
    for index, a, b in walls:
        q = nearest(p, a, b)
        d = math.dist(p, q)
        if 0.01 < d <= 128:
            candidates.append((d, index, a, b, q))
    if not candidates:
        return old, [], 'open placement: retain authored angle'
    nearest_distance = min(c[0] for c in candidates)
    selected = [c for c in candidates if c[0] <= nearest_distance+16]
    vx = vy = 0.0
    for d, index, a, b, q in selected:
        # Length weighting prevents tessellated trim from dominating a corner.
        weight = min(math.dist(a,b), 64) / max(d, 8)**2
        vx += (p[0]-q[0])/d*weight
        vy += (p[1]-q[1])/d*weight
    if math.hypot(vx,vy) < 1e-7:
        return old, [c[1] for c in selected], 'balanced corridor: retain authored angle'
    angle = round(math.degrees(math.atan2(vy,vx))) % 360
    return angle, [c[1] for c in selected], 'face away from nearby wall'


class MapGeometry:
    def __init__(self, path, binary=None):
        self.b = b = binary if binary is not None else parse(path)
        self.geo = geometry(b)
        self.boxes = {i:bounds(e) for i,e in self.geo.items()}
        self.lines = []
        self.grid = collections.defaultdict(list)
        for i,l in enumerate(b['linedef']):
            a,c = (point(b['vertex'][int(l[v])]) for v in ('v1','v2'))
            sectors = [int(b['sidedef'][int(l[k])]['sector']) if int(l.get(k,-1))>=0 else -1 for k in ('sidefront','sideback')]
            self.lines.append((i,a,c,sectors,l))
            for x in range(math.floor(min(a[0],c[0])/256), math.floor(max(a[0],c[0])/256)+1):
                for y in range(math.floor(min(a[1],c[1])/256), math.floor(max(a[1],c[1])/256)+1):
                    self.grid[x,y].append(i)

    def sector(self, p):
        for i,(x0,y0,x1,y1) in self.boxes.items():
            if x0<=p[0]<=x1 and y0<=p[1]<=y1 and inside(p,self.geo[i]):
                return i
        # Self-referencing sectors do not always form parity-test polygons.
        # Match the nearest genuine boundary's sidedef, as the map BSP does.
        for _,a,b,sectors,l in sorted(self.lines, key=lambda line: math.dist(p,nearest(p,line[1],line[2]))):
            if sectors[0]==sectors[1]: continue
            cross=(b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
            sid=sectors[0 if cross<=0 else 1]
            return sid if sid>=0 else None
        return None

    def walls(self, p, z):
        indices = set()
        for x in range(math.floor((p[0]-128)/256), math.floor((p[0]+128)/256)+1):
            for y in range(math.floor((p[1]-128)/256), math.floor((p[1]+128)/256)+1):
                indices.update(self.grid[x,y])
        result = []
        for i in sorted(indices):
            _,a,b,sectors,l = self.lines[i]
            q = nearest(p,a,b)
            if math.dist(p,q)>128: continue
            # Only consider faces bordering this item's elevation. Upper-storey
            # partitions and control sectors must not turn a lower-storey item.
            open_sides = []
            for sid in sectors:
                if sid<0: open_sides.append(False); continue
                s=self.b['sector'][sid]
                floor=height(s,q)
                if 'ceilingplane_c' in s:
                    aa,bb,c,d=(float(s.get('ceilingplane_'+k,0)) for k in 'abcd')
                    ceiling=-(aa*q[0]+bb*q[1]+d)/c
                else: ceiling=float(s.get('heightceiling',0))
                open_sides.append(floor<=z+24 and ceiling>=z+48)
            if not any(open_sides): continue
            if all(open_sides) and l.get('blocking','false')!='true': continue
            result.append((i,a,b))
        return result


def strip_angle_changes(text):
    return BLOCK.sub(lambda m: 'thing{'+ANGLE.sub('', m[1]).strip()+'}', text)


def process(path, actors):
    magic,lumps=read_wad(path)
    text_entry=next(((i,d) for i,(n,d) in enumerate(lumps) if n.rstrip(b'\0')==b'TEXTMAP'),None)
    binary = text_entry is None
    if binary:
        payload={n.rstrip(b'\0'):d for n,d in lumps}
        hexen=b'BEHAVIOR' in payload
        entry=next(i for i,(n,d) in enumerate(lumps) if n.rstrip(b'\0')==b'THINGS')
        original=payload[b'THINGS'];stride=20 if hexen else 10
        text=''
        for offset in range(0,len(original),stride):
            if hexen:
                tid,x,y,z,angle,num,flags=struct.unpack_from('<HhhhHHH',original,offset)
            else:
                x,y,angle,num,flags=struct.unpack_from('<hhHHH',original,offset);z=tid=0
            text+=f'thing {{ x={x}; y={y}; height={z}; angle={angle}; type={num}; id={tid}; }}\n'
        vertices=[dict(x=str(x),y=str(y)) for x,y in struct.iter_unpack('<hh',payload[b'VERTEXES'])]
        sectors=[dict(heightfloor=str(f),heightceiling=str(c),lightlevel=str(light)) for f,c,ft,ct,light,sp,tag in struct.iter_unpack('<hh8s8shhh',payload[b'SECTORS'])]
        sides=[dict(sector=str(v[-1])) for v in struct.iter_unpack('<hh8s8s8sH',payload[b'SIDEDEFS'])]
        lines=[];linebytes=payload[b'LINEDEFS'];linelen=16 if hexen else 14
        for offset in range(0,len(linebytes),linelen):
            v1,v2,flags=struct.unpack_from('<HHH',linebytes,offset)
            front,back=struct.unpack_from('<HH',linebytes,offset+linelen-4)
            lines.append(dict(v1=str(v1),v2=str(v2),sidefront=str(front if front!=65535 else -1),sideback=str(back if back!=65535 else -1),blocking='true' if flags&1 else 'false'))
        geo=MapGeometry(path,dict(vertex=vertices,sector=sectors,sidedef=sides,linedef=lines))
    else:
        entry,raw=text_entry; text=raw.decode('utf-8'); geo=MapGeometry(path)
    records=[];edits=[]
    for index,m in enumerate(BLOCK.finditer(text)):
        t=dict(FIELD.findall(m[1])); num=int(t.get('type',0))
        if num not in TYPES: continue
        actor=TYPES[num]; config=actors[actor]
        p=(float(t['x']),float(t['y'])); old=int(float(t.get('angle',0)))%360
        record=dict(thing=index,type=num,actor=actor,x=p[0],y=p[1],before=old,after=old)
        if config['spin']:
            record['reason']='native rotation retained'
        elif actor in SYMMETRIC:
            record['reason']='rotationally symmetric'
        else:
            sid=geo.sector(p)
            if sid is None:
                record['reason']='sector boundary: manual review required'
            else:
                z=height(geo.b['sector'][sid],p)+float(t.get('height',0))
                front_offset=FRONT_OFFSET.get(actor,0)
                facing,lines,reason=inward_angle(p,geo.walls(p,z),(old+front_offset)%360)
                new=(facing-front_offset)%360
                record.update(front_offset=front_offset,facing=facing,after=new,reason=reason,sector=sid,walls=lines)
                if old!=new:
                    if ANGLE.search(m[1]):
                        body=ANGLE.sub(lambda a:a[1]+str(new)+a[3],m[1],count=1)
                    else:
                        body=m[1]+f'angle = {new};\n'
                    edits.append((m.start(1),m.end(1),body))
        records.append(record)
    updated=text
    for start,end,body in reversed(edits): updated=updated[:start]+body+updated[end:]
    assert strip_angle_changes(text)==strip_angle_changes(updated), 'Non-angle edit'
    if binary:
        output=bytearray(original)
        for r in records:
            if r['before']!=r['after']:
                struct.pack_into('<H',output,r['thing']*stride+(8 if hexen else 4),r['after'])
        lumps[entry]=(lumps[entry][0],bytes(output))
    else:
        lumps[entry]=(lumps[entry][0],updated.encode('utf-8'))
    return write_wad(magic,lumps) if edits else None,records,'binary' if binary else 'UDMF'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--report',default='audit.json')
    args=parser.parse_args();root=args.root.resolve()
    actors={a['actor']:a for a in json.loads((root/'tools/artwork/voxels/manifest.json').read_text())['actors']}
    assert set(TYPES.values())<=set(actors), 'Unmapped voxel actor'
    report=[];changes=[]
    for path in sorted((root/'tutnt/maps').glob('*.wad')):
        before=path.read_bytes();data,records,kind=process(path,actors)
        changed=sum(r['before']!=r['after'] for r in records)
        report.append(dict(map=path.stem,format=kind,placements=len(records),changed=changed,items=records))
        print(f'{path.stem}: {len(records)} voxel placements, {changed} angle changes',flush=True)
        if data:changes.append((path,before,data))
    work=root/'tutnt/.codex/work/voxel-facing';work.mkdir(parents=True,exist_ok=True)
    if Path(args.report).name!=args.report: parser.error('--report must be a filename')
    (work/args.report).write_text(json.dumps(report,indent=2))
    if args.apply:
        backup=root/'tutnt/.codex/backups/voxel-facing';backup.mkdir(parents=True,exist_ok=True)
        for path,before,data in changes:
            if path.read_bytes()!=before:raise RuntimeError('Map changed concurrently: '+str(path))
            digest=hashlib.sha256(before).hexdigest()[:12]
            (backup/(path.stem+'-'+digest+'.wad')).write_bytes(before)
            path.write_bytes(data)
    print(json.dumps(dict(maps=len(report),placements=sum(r['placements'] for r in report),changes=sum(r['changed'] for r in report),applied=args.apply)))

if __name__=='__main__':main()
