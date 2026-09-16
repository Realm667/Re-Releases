"""Migrate a legacy cavern map to editable UDMF. Never run during packaging."""
from pathlib import Path
import re,struct
from build_lava_lips import parse,tex
from build_environment_fx import geometry,inside
from build_sky_edges import resolve_slopes,plane
from cavern_skyrooms import generate,apply
ROOT=Path(__file__).resolve().parents[1]
def lumps(data):
    magic,n,o=struct.unpack_from('<4sII',data)
    return magic,[(name,data[a:a+s]) for a,s,name in (struct.unpack_from('<II8s',data,o+i*16) for i in range(n))]
def wad(magic,entries):
    body=bytearray();directory=bytearray()
    for name,data in entries:
        directory+=struct.pack('<II8s',12+len(body),len(data),name);body+=data
    return struct.pack('<4sII',magic,len(entries),12+len(body))+body+directory
def edit_text(text,changes,append=''):
    for kind,edits in changes.items():
        index=-1
        def replace(m):
            nonlocal index
            index+=1;body=m[0]
            for key,value in edits.get(index,{}).items():
                pattern=r'\b'+key+r'\s*=\s*[^;]+;'
                if re.search(pattern,body):body=re.sub(pattern,lambda _:key+' = '+str(value)+';',body)
                else:body=body[:-1]+' '+key+' = '+str(value)+';\n}'
            return body
        text=re.sub(r'\b'+kind+r'\s*(?://[^\n]*\n\s*)?\{[^}]*\}',replace,text)
    return text+'\n'+append

def bake(source,root=ROOT):
    b=parse(source);resolve_slopes(b,source);geo=geometry(b)
    spec=generate(b,geo,lambda *a,**k:None,source.read_bytes())
    magic,entries=lumps(apply(source.read_bytes(),spec))
    changes={k:{} for k in ('sector','sidedef','linedef','thing')}
    chosen={int(r.split('|')[0]) for r in (root/'tutnt/cavern/sectors.txt').read_text().splitlines()}
    for i in chosen:
        s=b['sector'][i];edit={}
        for part in ('floor','ceiling'):
            if tex(s,'texture'+part) in ('IKWALL44','XA01TEX','XB01TEX'):edit['texture'+part]='"UCAVROCK"'
        if int(s.get('fadecolor','0'))==0x62411d:
            edit.update(fadecolor=0x363029,fogdensity=44)
            if int(s.get('lightlevel',160)) in (150,134):edit.update(lightlevel=int(s['lightlevel'])-6,lightfloor=32,lightceiling=-16,lightfloorabsolute='false',lightceilingabsolute='false')
        changes['sector'][i]=edit
    for i,s in enumerate(b['sidedef']):
        if int(s['sector']) in chosen:changes['sidedef'][i]={k:'"UCAVROCK"' for k in ('texturetop','texturemiddle','texturebottom') if tex(s,k) in ('IKWALL44','XA01TEX','XB01TEX')}
    for row in (root/'tutnt/cavern/platforms.txt').read_text().splitlines():
        changes['sector'].setdefault(int(row.split('|')[0]),{}).update(lightceiling=36,lightceilingabsolute='false')
    for w in spec['windows']:
        changes['sector'][w['pocket']]={'texturefloor':'"UCAVROCK"','textureceiling':'"UCAVROCK"'}
        changes['linedef'][w['line']]={'alpha':'.5','renderstyle':'"translucent"','wrapmidtex':'true'}
        sd=int(b['linedef'][w['line']]['sidefront'])
        changes['sidedef'][sd]={'texturetop':'"UCAVROCK"','texturebottom':'"UCAVROCK"','texturemiddle':'"UCAVFOG"','light_mid':255,'lightabsolute_mid':'true'}
    text=next(d for n,d in entries if n.rstrip(b'\0')==b'TEXTMAP').decode()
    things=re.findall(r'\bthing\s*(?://[^\n]*\n\s*)?\{([^}]*)\}',text)
    used=set()
    for i,body in enumerate(things):
        f=dict(re.findall(r'(\w+)\s*=\s*([^;]+);',body));used.add(int(f.get('type',0)))
        if f.get('type')=='9083' and 65200<=int(f.get('id',0))<=65202:changes['thing'][i]={'type':25110}
    assert not used.intersection(range(25000,25112)),'Editor number collision'
    definitions=[];placed=[]
    def thing(number,x,y,z,sector):
        floor=plane(b['sector'][sector],(x,y),'floor') if sector<len(b['sector']) else -650
        f={'type':number,'x':f'{x:.6f}','y':f'{y:.6f}','height':f'{z-floor:.6f}','angle':0}
        f.update({k:'true' for k in ('skill1','skill2','skill3','skill4','skill5','single','coop','dm')})
        placed.append('thing { '+' '.join(k+'='+str(v)+';' for k,v in f.items())+' }')
    for i,row in enumerate((root/'tutnt/cavern/scenery.txt').read_text().splitlines()):
        cls,x,y,z,sector,kind=row.split('|');definitions.append(f'    {25000+i} = {cls}')
        thing(25000+i,float(x),float(y),float(z),int(sector))
    for i in range(3):
        x,y,z=5375.,-4040.,-340.-i*470
        si=next(si for si,edges in geo.items() if inside((x,y),edges));thing(25111,x,y,z,si)
    text=edit_text(text,changes,'// Authored cavern Things; edit freely in UDB.\n'+'\n'.join(placed)+'\n')
    return wad(magic,[(n,text.encode() if n.rstrip(b'\0')==b'TEXTMAP' else d) for n,d in entries]),definitions

def validate(root=ROOT):
    """Read-only validation; manual model/map/material edits are authoritative."""
    for rel in ['maps/tnt03a2.wad','mapinfo/MAPINFO.cavern','modeldef/MODELDEF.cavern','zscript/cavern-actors.zc','cavern/haze.txt','cavern/fall-sources.txt','cavern/skyviews.txt']:
        if not (root/'tutnt'/rel).is_file():raise ValueError('Missing authored cavern asset: '+rel)
    for name in re.findall(r'Model\s+0\s+"([^"]+)"',(root/'tutnt/modeldef/MODELDEF.cavern').read_text()):
        if not (root/'tutnt/models/cavern'/name).is_file():raise ValueError('Missing authored model: '+name)
    assert any(n.rstrip(b'\0')==b'TEXTMAP' for n,d in lumps((root/'tutnt/maps/tnt03a2.wad').read_bytes())[1])
    print('Authored cavern assets validated; manual edits preserved.')
