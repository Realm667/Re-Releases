"""Read-only UDMF and classic Doom/Hexen map decoding for surface measurement."""
from pathlib import Path
import collections,re,struct,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build_utnt import read_wad
def name(data):return data.split(b'\0')[0].decode('ascii',errors='replace').upper()
def read(path):
    _,lumps=read_wad(path);d={name(n):data for n,data in lumps}
    g=collections.defaultdict(list)
    if 'TEXTMAP' in d:
        for m in re.finditer(r'\b(vertex|linedef|sidedef|sector|thing)\s*(?://[^\n]*\n\s*)?\{([^}]*)\}',d['TEXTMAP'].decode()):
            obj={}
            for k,v in re.findall(r'(\w+)\s*=\s*([^;]+);',m[2]):
                v=v.strip()
                if v.startswith('"'):obj[k]=v.strip('"')
                elif v in ['true','false']:obj[k]=v=='true'
                else:
                    try:obj[k]=float(v)
                    except ValueError:obj[k]=v
            g[m[1]].append(obj)
    else:
        for x,y in struct.iter_unpack('<hh',d['VERTEXES']):g['vertex'].append(dict(x=x,y=y))
        for f,c,ft,ct,light,special,tag in struct.iter_unpack('<hh8s8shhh',d['SECTORS']):g['sector'].append(dict(heightfloor=f,heightceiling=c,texturefloor=name(ft),textureceiling=name(ct),lightlevel=light,special=special,id=tag))
        for x,y,top,bottom,mid,sec in struct.iter_unpack('<hh8s8s8sH',d['SIDEDEFS']):g['sidedef'].append(dict(offsetx=x,offsety=y,texturetop=name(top),texturebottom=name(bottom),texturemiddle=name(mid),sector=sec))
        fmt='<HHHB5BHH' if 'BEHAVIOR' in d else '<7H'
        for values in struct.iter_unpack(fmt,d['LINEDEFS']):
            a,b,flags,special=values[:4];sf,sb=values[-2:];l=dict(v1=a,v2=b,special=special,sidefront=sf if sf!=65535 else -1,sideback=sb if sb!=65535 else -1,dontpegtop=bool(flags&8),dontpegbottom=bool(flags&16))
            if 'BEHAVIOR' in d:l.update({f'arg{i}':values[4+i] for i in range(5)})
            else:l['id']=values[4]
            g['linedef'].append(l)
    return dict(g)
def allmaps(root):return {p.stem.upper():read(p) for p in sorted((Path(root)/'maps').glob('*.wad'))}
