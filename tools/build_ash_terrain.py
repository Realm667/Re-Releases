"""Append isolated basalt fins to original TNT04B and move only its default sky.
Preserve gameplay geometry, ACS, and secondary views. Requires NumPy/ZDBSP.
Input must be a TNT04B without this new scenery. Never overwrites input.
"""
from pathlib import Path
import argparse,re,math,json,subprocess
import numpy as np
from build_utnt import read_wad,write_wad
from test_caldera_structure import parse
PAT=r'\b(vertex|linedef|sidedef|sector|thing)\s*(?://[^\n]*\n\s*)?\{([^}]*)\}'
def block(kind,fields):return kind+'\n{\n'+''.join(f'{k} = {v};\n' for k,v in fields.items())+'}\n'

def build(source,output,zdbsp):
 magic,lumps=read_wad(source);l,g=parse(source);base={k:len(v) for k,v in g.items()}
 assert base==dict(vertex=15662,linedef=18555,sidedef=33338,sector=3455,thing=1293)
 assert g['thing'][34]['type']=='9080' and 'id' not in g['thing'][34]
 assert g['sector'][0]['id']=='3' and g['sector'][0]['lightlevel']=='128'
 text=l['TEXTMAP'].decode();count=0;disabled=[]
 def edit(m):
  nonlocal count
  if m[1]!='thing':return m[0]
  i=count;count+=1;d=dict(g['thing'][i])
  if i==34:
   d.update(x='18000.0',y='18000.0',height='640.0');return block('thing',d)
  if d.get('type')=='19020':
   assert d.get('id')=='40' and -4400<float(d['x'])<-3400 and 1300<float(d['y'])<2200
   # Preserve index, TID and placement as inert MapSpots in the retired sky room.
   d['type']='9001';disabled.append(i);return block('thing',d)
  return m[0]
 text=re.sub(PAT,edit,text)
 vertices=[];sectors=[];sides=[];lines=[];edges={};xyz=[];N=256
 rings=[(850,0,-640),(1200,1,0),(1550,1,.18),(1790,1,.65),(1920,1,1),
        (2100,1,.50),(2400,1,.08),(2850,0,-480),(3400,2,0),
        (3860,2,.5),(4100,2,1),(4380,2,.50),(4820,2,.08),(5400,0,-560),(6500,0,-700)]
 for j,(radius,ridge,weight) in enumerate(rings):
  for i in range(N):
   a=2*math.pi*i/N
   rad=radius*(1+.026*math.sin(7*a+j*.11)+.014*math.sin(19*a+j*.18))
   phase=ridge*.69
   # Narrow, unequal peaks with sharply fractured shoulders instead of smooth hills.
   peak=.08+.72*max(0,math.sin(17*a+phase))**6+.55*max(0,math.sin(29*a-phase))**10
   peak+=.12*max(0,math.sin(43*a+phase*2))**4
   peak*=.85+.20*math.sin(5*a-phase)
   height=weight if ridge==0 else -380+(380+(380 if ridge==1 else 550)*peak)*weight
   if ridge and 0<weight<1:height+=30*math.sin(31*a+j*.8)*math.sin(weight*math.pi)
   p=(round(18000+rad*math.cos(a),4),round(18000+rad*math.sin(a),4),round(height,4))
   xyz.append(p);vertices.append(block('vertex',dict(x=p[0],y=p[1])))
 def poly(indices,fields):
  si=base['sector']+len(sectors);sectors.append(block('sector',fields));indices=list(reversed(indices))
  for a,b in zip(indices,indices[1:]+indices[:1]):
   side=base['sidedef']+len(sides);sides.append(block('sidedef',dict(sector=si,texturebottom='"UCBASALT"',texturemiddle='"-"',texturetop='"-"')))
   if (b,a) in edges:
    line=lines[edges[(b,a)]];line['sideback']=side;line['twosided']='true';line.pop('blocking',None)
   else:edges[(a,b)]=len(lines);lines.append(dict(v1=base['vertex']+a,v2=base['vertex']+b,sidefront=side,blocking='true'))
 def common():return dict(heightfloor=-640,heightceiling=9000,texturefloor='"UCBASALT"',textureceiling='"F_SKY1"',lightlevel=112,lightcolor=0xb0aaa4,fadecolor=0x181512,fogdensity=9,xscalefloor=1.0,yscalefloor=1.0)
 center=common();center['texturefloor']='"F_SKY1"';poly(list(range(N)),center)
 max_gap=0
 for j in range(len(rings)-1):
  for i in range(N):
   a=j*N+i;b=j*N+(i+1)%N;c=(j+1)*N+i;d=(j+1)*N+(i+1)%N
   tris=((a,c,d),(a,d,b)) if (i+j)%2==0 else ((a,c,b),(b,c,d))
   for tri in tris:
    p,q,r=[np.array(xyz[k]) for k in tri];normal=np.cross(q-p,r-p);normal/=np.linalg.norm(normal)
    if normal[2]<0:normal=-normal
    f=common();f.update(floorplane_a=round(float(normal[0]),13),floorplane_b=round(float(normal[1]),13),floorplane_c=round(float(normal[2]),13),floorplane_d=round(float(-np.dot(normal,p)),10))
    f['lightlevel']=round(136+26*max(0,float(np.dot(normal,[.3,-.6,.74]))));poly(tri,f)
 text+='\n// Isolated TNT04B ash landscape: 256 angular samples, 15 radial bands.\n'+''.join(vertices)+''.join(sectors)+''.join(sides)+''.join(block('linedef',d) for d in lines)
 output=Path(output);output.parent.mkdir(parents=True,exist_ok=True);raw=output.with_suffix('.raw.wad')
 raw.write_bytes(write_wad(magic,[(n,text.encode() if n.rstrip(b'\0')==b'TEXTMAP' else d) for n,d in lumps if n.rstrip(b'\0') not in [b'ZNODES',b'BLOCKMAP',b'REJECT']]))
 r=subprocess.run([str(zdbsp),'-q','-X','-g','-r','-o',str(output),str(raw)],capture_output=True,timeout=120)
 assert r.returncode==0,(r.stdout+r.stderr).decode(errors='replace');raw.unlink()
 ol,og=parse(output)
 for k in ['vertex','linedef','sidedef','sector']:assert og[k][:base[k]]==g[k]
 for i,t in enumerate(g['thing']):
  if i==34:assert {k:v for k,v in t.items() if k not in ['x','y','height']}=={k:v for k,v in og['thing'][i].items() if k not in ['x','y','height']}
  elif i in disabled:assert {k:v for k,v in t.items() if k!='type'}=={k:v for k,v in og['thing'][i].items() if k!='type'}
  else:assert t==og['thing'][i]
 for name,data in l.items():
  if name not in ['TEXTMAP','ZNODES','BLOCKMAP','REJECT']:assert ol[name]==data,name
 return dict(original_counts=base,added_counts=dict(vertex=len(vertices),linedef=len(lines),sidedef=len(sides),sector=len(sectors)),disabled_spawner_indices=disabled,default_viewpoint=34,checks=['gameplay geometry unchanged','ACS and other lumps unchanged','secondary cameras unchanged','old sky spawners replaced only by inert MapSpots'])

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['source','output','zdbsp']:p.add_argument('--'+k,type=Path,required=True)
 print(json.dumps(build(**vars(p.parse_args())),indent=2))
