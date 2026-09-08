from pathlib import Path
import struct,re,json,sys,math,collections
import argparse
p=argparse.ArgumentParser(description='Inventory UTNT portal surfaces, including UDMF and Hexen maps.')
p.add_argument('--root',type=Path,default=Path(__file__).resolve().parent.parent)
p.add_argument('--out',type=Path,required=True)
args=p.parse_args();R=args.root;W=args.out.parent;W.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'tools'))
from build_utnt import read_wad
out=[]
for path in sorted((R/'tutnt/maps').glob('*.wad')):
    lumps={n.rstrip(b'\0').decode():d for n,d in read_wad(path)[1]}
    if 'TEXTMAP' not in lumps:
        # Binary Hexen-format maps (all three non-UDMF maps contain BEHAVIOR).
        name=lambda x:x.rstrip(b'\0').decode()
        groups=dict(vertex=[dict(x=x,y=y) for x,y in struct.iter_unpack('<hh',lumps['VERTEXES'])],
            sector=[dict(heightfloor=f,heightceiling=c,texturefloor=name(ft),textureceiling=name(ct),id=tag) for f,c,ft,ct,light,sp,tag in struct.iter_unpack('<hh8s8shhh',lumps['SECTORS'])],
            sidedef=[dict(texturetop=name(t),texturebottom=name(b),texturemiddle=name(m),sector=s) for x,y,t,b,m,s in struct.iter_unpack('<hh8s8s8sH',lumps['SIDEDEFS'])],
            linedef=[dict(v1=x[0],v2=x[1],sidefront=x[-2],sideback=x[-1] if x[-1]!=65535 else -1,special=x[3]) for x in struct.iter_unpack('<HHHB5BHH',lumps['LINEDEFS'])],
            thing=[dict(id=x[0],x=x[1],y=x[2],angle=x[4],type=x[5]) for x in struct.iter_unpack('<HhhhHHHB5B',lumps['THINGS'])])
        text=''
    else:
        text=lumps['TEXTMAP'].decode()
        # Keep strings while removing UDB's `thing // 123` and block comments.
        text=re.sub(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*[\s\S]*?\*/',lambda m:m[0] if m[0].startswith('"') else '',text)
        groups={}
    for kind,body in re.findall(r'(\w+)\s*\{([^}]+)\}',text):
        row={}
        for key,value in re.findall(r'(\w+)\s*=\s*([^;]+);',body):
            value=value.strip()
            row[key]=value[1:-1] if value.startswith('"') else float(value) if re.fullmatch(r'-?\d+(\.\d+)?',value) else value
        groups.setdefault(kind,[]).append(row)
    sides=groups.get('sidedef',[]);sectors=groups.get('sector',[]);verts=groups.get('vertex',[])
    found=[]
    for si,side in enumerate(sides):
        for part in ['texturetop','texturemiddle','texturebottom']:
            tex=side.get(part,'-')
            if 'TELEP' not in tex.upper():continue
            line=next((l for l in groups['linedef'] if si in (l.get('sidefront'),l.get('sideback'))),None)
            if not line:continue
            a,b=[verts[int(line[k])] for k in ['v1','v2']]
            width=math.hypot(a.get('x',0)-b.get('x',0),a.get('y',0)-b.get('y',0))
            sec=sectors[int(side['sector'])];height=sec.get('heightceiling',0)-sec.get('heightfloor',0)
            otherindex=line.get('sideback',-1) if line.get('sidefront')==si else line.get('sidefront',-1)
            if otherindex>=0:
                other=sectors[int(sides[int(otherindex)]['sector'])]
                height=min(sec.get('heightceiling',0),other.get('heightceiling',0))-max(sec.get('heightfloor',0),other.get('heightfloor',0))
            found.append(dict(side=si,part=part,texture=tex,width=round(width,2),opening=height,sector=int(side['sector']),heights=[sec.get('heightfloor',0),sec.get('heightceiling',0)],otherheights=[other.get('heightfloor',0),other.get('heightceiling',0)] if otherindex>=0 else None,ends=[a,b],center=[(a.get('x',0)+b.get('x',0))/2,(a.get('y',0)+b.get('y',0))/2],line={k:v for k,v in line.items() if k in ['special','arg0','arg1','id','dontpegbottom']},eligible=part=='texturemiddle' and tex in ['QTELEPT','QTELEPOR'] and width>=48 and height>=48))
    actors=[dict(index=i,**t) for i,t in enumerate(groups.get('thing',[])) if t.get('type') in [31000,31001]]
    flats=[dict(index=i,**{k:v for k,v in s.items() if k in ['texturefloor','textureceiling','heightfloor','heightceiling','id']}) for i,s in enumerate(sectors) if any('TELEP' in str(s.get(k,'')) for k in ['texturefloor','textureceiling'])]
    script=lumps.get('SCRIPTS',b'').decode(errors='replace')
    scriptrefs=[s for s in script.splitlines() if re.search(r'portal|qtelep|3100[01]',s,re.I)]
    if found or actors or flats or scriptrefs:
        out.append(dict(map=path.stem.upper(),walls=found,actors=actors,flats=flats,scripts=scriptrefs))
        print(path.stem, 'walls',len(found),'eligible',sum(s['eligible'] for s in found),'actors',len(actors),'flats',len(flats), 'otherwalls',[(x['texture'],x['part'],x['width'],x['opening']) for x in found if not x['eligible']])
args.out.write_text(json.dumps(out,indent=2))
