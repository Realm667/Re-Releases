"""Replace the first caldera's isolated coarse terrain with detailed sloped ridges.

Input must contain the 769-sector caldera from the 2026-09-08 baseline.
All gameplay blocks and all things are preserved exactly. Requires NumPy and
ZDBSP; output uses the same sky viewpoint and coordinates. Never edits input.
"""
import argparse,re,math,json,subprocess
from pathlib import Path
import numpy as np
from build_utnt import read_wad,write_wad

BASE={'vertex':5286,'linedef':6373,'sidedef':11421,'sector':1426}
OLD={'vertex':448,'linedef':1216,'sidedef':2368,'sector':769}
PATTERN=r'\b(vertex|linedef|sidedef|sector|thing)\s*(?://[^\n]*\n\s*)?\{([^}]*)\}'

def block(kind,fields):return kind+'\n{\n'+''.join(f'{k} = {v};\n' for k,v in fields.items())+'}\n'

def refine(source,output,zdbsp):
 magic,lumps=read_wad(source)
 text=next(d for n,d in lumps if n.rstrip(b'\0')==b'TEXTMAP').decode()
 groups={k:[] for k in [*BASE,'thing']}
 for m in re.finditer(PATTERN,text):groups[m[1]].append(m)
 for k in BASE:assert len(groups[k])==BASE[k]+OLD[k],f'Unexpected {k} count; require original caldera baseline'
 fields=lambda m:dict(re.findall(r'(\w+)\s*=\s*([^;]+);',m[2]))
 # Verify scenery is isolated and that retaining old index prefixes is safe.
 for m in groups['vertex'][BASE['vertex']:]:
  v=fields(m);assert 9500<float(v['x'])<26500 and 9500<float(v['y'])<26500
 for i,m in enumerate(groups['linedef']):
  v=fields(m);ours=i>=BASE['linedef']
  for key in ['v1','v2']:assert (int(v[key])>=BASE['vertex'])==ours
  for key in ['sidefront','sideback']:
   if key in v:assert (int(v[key])>=BASE['sidedef'])==ours
 for i,m in enumerate(groups['sidedef']):assert (int(fields(m)['sector'])>=BASE['sector'])==(i>=BASE['sidedef'])
 spans=sorted([(m.start(),m.end()) for k in BASE for m in groups[k][BASE[k]:]],reverse=True)
 for start,end in spans:text=text[:start]+text[end:]
 vertices=[];sectors=[];lines=[];sides=[];edges={};xyz=[];N=192
 # Radius, ridge number, relative height along the cross-section.
 rings=[(850,0,-640),(1150,1,0),(1450,1,.5),(1800,1,1),
  (2100,1,.55),(2400,0,-380),(2700,2,0),(3100,2,.45),
  (3500,2,1),(3900,2,.55),(4350,0,-360),(4750,3,0),
  (5150,3,.4),(5650,3,1),(6050,3,.68),(6500,3,.30),
  (6900,3,.05),(7300,0,-450)]
 for j,(radius,ridge,weight) in enumerate(rings):
  for i in range(N):
   a=2*math.pi*i/N
   # Shared angular samples keep every radial strip watertight.
   jitter=.036*math.sin(5*a+j*.21)+.022*math.sin(13*a+j*.37)+.008*math.sin(37*a+j*.13)
   rad=radius*(1+jitter)
   phase=ridge*.87
   relief=.71+.16*math.sin(5*a+phase)+.13*math.sin(11*a-phase)+.085*math.sin(23*a+phase*1.4)+.05*math.sin(47*a-phase)+.025*math.sin(79*a+phase)
   # Narrow gullies and a broad southern opening frame the fortress.
   delta=math.atan2(math.sin(a-math.radians(270)),math.cos(a-math.radians(270)))
   valley=1-.65*math.exp(-(delta/.30)**2)
   height=weight if ridge==0 else -320+(320+[0,420,610,800][ridge]*relief*valley)*weight
   if ridge and 0<weight<1:height+=24*math.sin(19*a+j*.8)*math.sin(weight*math.pi)
   p=(round(18000+rad*math.cos(a),4),round(18000+rad*math.sin(a),4),round(height,4))
   xyz.append(p);vertices.append(block('vertex',dict(x=p[0],y=p[1])))
 def poly(indices,f):
  si=BASE['sector']+len(sectors);sectors.append(block('sector',f));indices=list(reversed(indices))
  for a,b in zip(indices,indices[1:]+indices[:1]):
   side=BASE['sidedef']+len(sides)
   sides.append(block('sidedef',dict(sector=si,texturebottom='"UCBASALT"',texturemiddle='"-"',texturetop='"-"')))
   if (b,a) in edges:
    line=lines[edges[(b,a)]];line['sideback']=side;line['twosided']='true';line.pop('blocking',None)
   else:
    edges[(a,b)]=len(lines);lines.append(dict(v1=BASE['vertex']+a,v2=BASE['vertex']+b,sidefront=side,blocking='true'))
 def common():return dict(heightfloor=-640,heightceiling=9000,texturefloor='"UCBASALT"',textureceiling='"F_SKY1"',lightlevel=144,fadecolor=0x28100b,fogdensity=10,xscalefloor=1.0,yscalefloor=1.0,lightcolor=0xead6cd)
 center=common();center['texturefloor']='"F_SKY1"';poly(list(range(N)),center)
 for j in range(len(rings)-1):
  for i in range(N):
   a=j*N+i;b=j*N+(i+1)%N;c=(j+1)*N+i;d=(j+1)*N+(i+1)%N
   tris=((a,c,d),(a,d,b)) if (i+j)%2==0 else ((a,c,b),(b,c,d))
   for tri in tris:
    p,q,r=[np.array(xyz[k]) for k in tri];normal=np.cross(q-p,r-p);normal/=np.linalg.norm(normal)
    if normal[2]<0:normal=-normal
    f=common();f.update(floorplane_a=round(float(normal[0]),13),floorplane_b=round(float(normal[1]),13),floorplane_c=round(float(normal[2]),13),floorplane_d=round(float(-np.dot(normal,p)),10))
    f['lightlevel']=round(116+34*max(0,float(np.dot(normal,[.3,-.6,.74]))))
    poly(list(tri),f)
 added='\n// Detailed caldera terrain: 192 angular samples, 18 radial bands.\n'+''.join(vertices)+''.join(sectors)+''.join(sides)+''.join(block('linedef',l) for l in lines)
 output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
 raw=output.with_suffix('.raw.wad')
 raw.write_bytes(write_wad(magic,[(n,(text+added).encode() if n.rstrip(b'\0')==b'TEXTMAP' else d) for n,d in lumps if n.rstrip(b'\0') not in [b'ZNODES',b'BLOCKMAP',b'REJECT']]))
 r=subprocess.run([str(zdbsp),'-q','-X','-g','-r','-o',str(output),str(raw)],capture_output=True,timeout=120)
 if r.returncode:raise RuntimeError((r.stdout+r.stderr).decode(errors='replace'))
 raw.unlink()
 return {'terrain_sectors_before':769,'terrain_sectors_after':len(sectors),'terrain_vertices':len(vertices),'terrain_lines':len(lines),'terrain_sides':len(sides),'base_counts':BASE,'angular_samples':N,'radial_bands':len(rings)}

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--zdbsp',type=Path,required=True)
 a=p.parse_args();print(json.dumps(refine(a.input,a.output,a.zdbsp),indent=2))
