"""Read-only UDMF wall-coverage inventory for choosing visual texture reviews.

Areas use authored reference heights, not a visibility/render simulation.
Slopes, 3D floors, ACS movement, occlusion and two-sided masked middles require
manual review. Connected groups share texture and geometric endpoint; they may
include branches or surfaces at different heights. No maps are changed.
"""
import argparse,collections,json,math,re,struct
from pathlib import Path
from build_utnt import read_wad

def parse(data):
    out=collections.defaultdict(list)
    for m in re.finditer(r'\b(vertex|linedef|sidedef|sector|thing)\s*(?://[^\n]*\n\s*)?\{([^}]*)\}',data.decode(errors='replace')):
        out[m[1]].append(dict(re.findall(r'(\w+)\s*=\s*([^;]+);',m[2])))
    return out

def dimensions(root):
    result={}
    for folder in ['textures','flats']:
        for p in sorted((root/folder).rglob('*')):
            if not p.is_file():continue
            data=p.read_bytes()[:32]; size=None
            if data.startswith(b'\x89PNG') and len(data)>=24:size=struct.unpack('>II',data[16:24])
            elif p.suffix.lower()=='.lmp' and len(data)>=8:
                w,h=struct.unpack_from('<HH',data)
                if 1<=w<=8192 and 1<=h<=8192:size=(w,h)
            if size:result[p.stem.upper()]=list(size)
    for p in sorted([*root.glob('TEXTURES*'), *(root/'textures/definitions').glob('TEXTURES*')], key=lambda p:p.name):
        if not p.is_file():continue
        text=p.read_text(errors='replace')
        for m in re.finditer(r'\b(?:Texture|WallTexture|Flat)\s+"?([^",\s]+)"?\s*,\s*(\d+)\s*,\s*(\d+)\s*\{',text,re.I):
            depth=1;pos=m.end()
            while pos<len(text) and depth:
                depth+=(text[pos]=='{')-(text[pos]=='}');pos+=1
            block=text[m.end():pos]
            scales=[]
            for axis in ['X','Y']:
                s=re.search(r'\b'+axis+r'Scale\s+([0-9.]+)',block,re.I)
                scales.append(float(s[1]) if s else 1)
            result[m[1].upper()]=[int(m[2])/scales[0],int(m[3])/scales[1]]
    return result

def audit(root):
    sizes=dimensions(root);summary={};maps=[]
    for path in sorted((root/'maps').glob('*.wad')):
        _,lumps=read_wad(path)
        text=next((d for n,d in lumps if n.rstrip(b'\0')==b'TEXTMAP'),None)
        if text is None:continue
        g=parse(text);bytexture=collections.defaultdict(list);maps.append(path.stem.upper())
        def height(s,k):return float(s.get('height'+k,0))
        for li,line in enumerate(g['linedef']):
            vs=[g['vertex'][int(line[k])] for k in ['v1','v2']]
            a,b=[(float(v['x']),float(v['y'])) for v in vs];length=math.dist(a,b)
            for face,other in [('sidefront','sideback'),('sideback','sidefront')]:
                if face not in line:continue
                s=g['sidedef'][int(line[face])];f=g['sector'][int(s['sector'])]
                bs=g['sidedef'][int(line[other])] if other in line else None
                back=g['sector'][int(bs['sector'])] if bs else None
                for slot,tier in [('texturemiddle','mid'),('texturetop','top'),('texturebottom','bottom')]:
                    name=s.get(slot,'"-"').strip('"').upper()
                    if name=='-' or not name:continue
                    if back is None:
                        if tier!='mid':continue
                        tall=height(f,'ceiling')-height(f,'floor')
                    elif tier=='mid':continue
                    elif tier=='top':
                        if f.get('textureceiling')=='"F_SKY1"' and back.get('textureceiling')=='"F_SKY1"':continue
                        tall=height(f,'ceiling')-height(back,'ceiling')
                    else:tall=height(back,'floor')-height(f,'floor')
                    if tall<=0 or length<=0:continue
                    dim=sizes.get(name);sx=abs(float(s.get('scalex_'+tier,1)));sy=abs(float(s.get('scaley_'+tier,1)))
                    rx=length*sx/dim[0] if dim else None;ry=tall*sy/dim[1] if dim else None
                    bytexture[name].append(dict(line=li,side=int(line[face]),tier=tier,a=a,b=b,area=length*tall,length=length,height=tall,repeats_x=rx,repeats_y=ry))
        for name,faces in bytexture.items():
            adj=collections.defaultdict(list)
            for i,e in enumerate(faces):
                adj[e['a']].append(i);adj[e['b']].append(i)
            todo=set(range(len(faces)));groups=[]
            while todo:
                seed=todo.pop();q=[seed];component=[seed]
                while q:
                    e=faces[q.pop()]
                    for v in [e['a'],e['b']]:
                        for i in adj[v]:
                            if i in todo:todo.remove(i);q.append(i);component.append(i)
                groups.append(component)
            biggest=max(groups,key=lambda comp:sum(faces[i]['area'] for i in comp))
            area=sum(e['area'] for e in faces)
            entry=summary.setdefault(name,dict(texture=name,estimated_wall_area=0,wall_tiers=0,dimensions=sizes.get(name),maps=[],largest_groups=[]))
            entry['estimated_wall_area']+=area;entry['wall_tiers']+=len(faces)
            entry['maps'].append(dict(map=path.stem.upper(),estimated_wall_area=round(area),wall_tiers=len(faces)))
            entry['largest_groups'].append(dict(map=path.stem.upper(),estimated_area=round(sum(faces[i]['area'] for i in biggest)),wall_tiers=len(biggest),example_lines=[faces[i]['line'] for i in sorted(biggest)[:8]],max_single_wall_repeats_x=round(max(faces[i]['repeats_x'] or 0 for i in biggest),2),max_single_wall_repeats_y=round(max(faces[i]['repeats_y'] or 0 for i in biggest),2)))
    ranked=sorted(summary.values(),key=lambda e:e['estimated_wall_area'],reverse=True)
    for e in ranked:
        e['estimated_wall_area']=round(e['estimated_wall_area'])
        e['maps'].sort(key=lambda x:x['estimated_wall_area'],reverse=True)
        e['largest_groups'].sort(key=lambda x:x['estimated_area'],reverse=True)
        e['rock_name_candidate']=bool(re.search(r'ROCK|CLIFF|ASHWALL|STONE',e['texture']))
    return dict(method=__doc__,maps_scanned=maps,textures=ranked)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent.parent/'tutnt')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();result=audit(a.root)
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2))
    rock=[x for x in result['textures'] if x['rock_name_candidate']]
    print(json.dumps(dict(maps=len(result['maps_scanned']),textures=len(result['textures']),rock_candidates=[{k:e[k] for k in ['texture','estimated_wall_area','wall_tiers','dimensions','maps']} for e in rock[:10]]),indent=2))
if __name__=='__main__':main()
