from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from build_utnt import write_wad
addon=ROOT/'tools/weather-tests'; (addon/'maps').mkdir(exist_ok=True)
parts=['namespace="ZDoom";']
vertices={}; edges={}; side=0
def vertex(x,y):
    if (x,y) not in vertices:
        vertices[x,y]=len(vertices); parts.append(f'vertex {{ x={x}.0; y={y}.0; }}')
    return vertices[x,y]
def rectangle(index,x0,y0,x1,y1):
    global side
    vs=[vertex(x0,y0),vertex(x0,y1),vertex(x1,y1),vertex(x1,y0)]
    for a,b in zip(vs,vs[1:]+vs[:1]):
        parts.append(f'sidedef {{ sector={index}; texturemiddle="STARTAN3"; texturetop="STARTAN3"; texturebottom="STARTAN3"; }}')
        if (b,a) in edges: edges[b,a]['back']=side
        else: edges[a,b]={'front':side,'sector':index}
        side+=1
for y in range(3):
    for x in range(3):
        i=y*3+x
        extra=' id=55;' if i==5 else ' floorplane_a=-0.125; floorplane_b=0.0; floorplane_c=1.0; floorplane_d=0.0;' if i==7 else ''
        parts.append(f'sector {{ heightfloor=0; heightceiling={128 if i==4 else 384}; texturefloor="{"FWATER1" if i==1 else "FLAT5_4"}"; textureceiling="{"CEIL1_1" if i==4 else "F_SKY1"}"; lightlevel=192;{extra} }}')
        rectangle(i,-768+x*512,-768+y*512,-256+x*512,-256+y*512)
parts.append('sector { heightfloor=128; heightceiling=192; texturefloor="FLAT5_4"; textureceiling="CEIL1_1"; lightlevel=192; }')
rectangle(9,1024,0,1152,128)
special_added=False
for (a,b),e in edges.items():
    tail=f' sideback={e["back"]}; twosided=true;' if 'back' in e else ' blocking=true;'
    if e['sector']==9 and not special_added:
        tail+=' special=160; arg0=55; arg1=1; arg2=0; arg3=255;';special_added=True
    parts.append(f'linedef {{ v1={a}; v2={b}; sidefront={e["front"]};{tail} }}')
flags='skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; coop=true; dm=true;'
for i in range(2): parts.append(f'thing {{ x={i*64}.0; y=-512.0; type={i+1}; angle=90; {flags} }}')
for y in range(-704,769,128):
    for x in range(-704,769,128):
        if abs(x)<256 and abs(y)<256: continue
        parts.append(f'thing {{ x={x}.0; y={y}.0; type={19021 if x<0 else 19022}; {flags} }}')
(addon/'maps/utntwx.wad').write_bytes(write_wad(b'PWAD',[(b'UTNTWX',b''),(b'TEXTMAP', '\n'.join(parts).encode()),(b'ENDMAP',b'')]))
(addon/'TERRAIN').write_text('floor FWATER1 UTNT_Water\n')
print('Created isolated weather geometry fixture.')
