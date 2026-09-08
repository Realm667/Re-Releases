"""Add deterministic, collision-checked rock contours and sloped terrain to TNT01.
Requires Shapely 2.x and ZDBSP. The input is never overwritten. Preserve original
line/sector indices, actors, sector fields, action lines and ACS. ZDBSP can reorder
vertex storage. Re-running on output is refused.
"""
import argparse,collections,hashlib,json,math,random,re,subprocess,sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent/'deps'))
from shapely.geometry import Point,LineString,Polygon,MultiPoint
from shapely.ops import polygonize,unary_union
from shapely.strtree import STRtree
from build_utnt import read_wad,write_wad
PAT=r'\b(vertex|linedef|sidedef|sector|thing)\s*(?://[^\n]*\n\s*)?\{([^}]*)\}'
TARGETS=[884,1458,1478,2404,3676,3678]
def parse(path):
 magic,lumps=read_wad(path);text=dict((n.rstrip(b'\0').decode(),d) for n,d in lumps)['TEXTMAP'].decode()
 g={k:[] for k in ('vertex','linedef','sidedef','sector','thing')}
 for m in re.finditer(PAT,text):g[m[1]].append(dict(re.findall(r'(\w+)\s*=\s*([^;]+);',m[2])))
 return magic,lumps,text,g
def block(k,d):return k+'\n{\n'+''.join(f'{a} = {b};\n' for a,b in d.items())+'}\n'
def sector_of(g,l,side):return int(g['sidedef'][int(l[side])]['sector']) if side in l and int(l[side])>=0 else -1
def sector_polygon(g,si):
 vertices=[(float(v['x']),float(v['y'])) for v in g['vertex']];edges=[]
 for l in g['linedef']:
  f,b=sector_of(g,l,'sidefront'),sector_of(g,l,'sideback')
  if f==b or si not in (f,b):continue
  a,c=vertices[int(l['v1'])],vertices[int(l['v2'])]
  edges.append((a,c) if f==si else (c,a))
 def inside(p):
  # Oriented ray crossing excludes islands and holes belonging to other sectors.
  winding=0
  for (x,y),(xx,yy) in edges:
   cross=(xx-x)*(p.y-y)-(p.x-x)*(yy-y)
   if y<=p.y<yy and cross>0:winding+=1
   elif yy<=p.y<y and cross<0:winding-=1
  return winding!=0
 return unary_union([p for p in polygonize([LineString(e) for e in edges]) if inside(p.representative_point())])
def build(source,output,zdbsp,report_path):
 magic,lumps,text,g=parse(source)
 assert 'TNT01_ORGANIC_V1' not in text,'Already refined'
 counts={k:len(a) for k,a in g.items()};orig={k:[dict(d) for d in a] for k,a in g.items()}
 assert counts['sector']==3742 and counts['linedef']==19971,'Review changed baseline before applying'
 rng=random.Random(66701)
 verts=lambda:[(float(v['x']),float(v['y'])) for v in g['vertex']]
 vv=verts();polys={si:sector_polygon(g,si) for si in TARGETS}
 all_lines=[LineString([vv[int(l['v1'])],vv[int(l['v2'])]]) for l in g['linedef']]
 special=unary_union([all_lines[i].buffer(96) for i,l in enumerate(g['linedef']) if int(l.get('special','0')) or int(l.get('id','0'))])
 thing_tree=STRtree([Point(float(t['x']),float(t['y'])) for t in g['thing']])
 line_tree=STRtree(all_lines)
 contours=[];rock_edges=[]
 for li,l in enumerate(orig['linedef']):
  f,b=sector_of(g,l,'sidefront'),sector_of(g,l,'sideback')
  candidates=[s for s in (f,b) if s in TARGETS]
  if len(candidates)!=1:continue
  si=candidates[0];other=b if si==f else f;s=g['sector'][si]
  if any(k.startswith('floorplane') for k in s) or int(s.get('id','0')):continue
  side=g['sidedef'][int(l['sidefront'] if si==f else l['sideback'])]
  texture=side.get('texturemiddle' if other<0 else 'texturebottom','')
  if 'QROCK' not in texture:continue
  height=float(s.get('heightceiling','640'))-float(s['heightfloor']) if other<0 else float(g['sector'][other]['heightfloor'])-float(s['heightfloor'])
  if height<48 or (other>=0 and any(k.startswith('floorplane') for k in g['sector'][other])):continue
  a,c=vv[int(l['v1'])],vv[int(l['v2'])];length=all_lines[li].length
  if length<76:continue
  dx,dy=(c[0]-a[0])/length,(c[1]-a[1])/length
  nx,ny=(dy,-dx) if si==f else (-dy,dx)
  rock_edges.append(dict(line=li,sector=si,a=a,b=c,normal=(nx,ny),height=height,length=length))
  if length<100 or int(l.get('special','0')) or int(l.get('id','0')):continue
  mid=Point((a[0]+c[0])/2+nx*100,(a[1]+c[1])/2+ny*100)
  if not polys[si].contains(mid.buffer(58)):continue
  if not all_lines[li].buffer(8).disjoint(special) or len(thing_tree.query(all_lines[li].buffer(56),predicate='intersects')):continue
  n=max(3,min(7,round(length/72)));amp=min(32,length*.12)
  points=[a]+[(round(a[0]+dx*length*j/n+nx*amp*math.sin(math.pi*j/n)*rng.uniform(.35,1),4),round(a[1]+dy*length*j/n+ny*amp*math.sin(math.pi*j/n)*rng.uniform(.35,1),4)) for j in range(1,n)]+[c]
  path=LineString(points)
  if len(thing_tree.query(path.buffer(48),predicate='intersects')):continue
  if not path.is_simple or not polys[si].buffer(.001).covers(path):continue
  if any(j!=li and path.crosses(all_lines[j]) for j in line_tree.query(path)):continue
  ids=[int(l['v1'])]
  for p in points[1:-1]:ids.append(len(g['vertex']));g['vertex'].append(dict(x=p[0],y=p[1]))
  ids.append(int(l['v2']));distance=0
  for j,(va,vb) in enumerate(zip(ids,ids[1:])):
   nl=dict(l,v1=str(va),v2=str(vb))
   for key in ('sidefront','sideback'):
    if key not in l or int(l[key])<0:continue
    ns=dict(orig['sidedef'][int(l[key])]);ns['offsetx']=str(round(float(ns.get('offsetx',0))+(distance if key=='sidefront' else length-distance-LineString(points[j:j+2]).length)))
    if j==0:
     nl[key]=l[key];g['sidedef'][int(l[key])]=ns
    else:
     nl[key]=str(len(g['sidedef']));g['sidedef'].append(ns)
   if j==0:g['linedef'][li]=nl
   else:g['linedef'].append(nl)
   distance+=LineString(points[j:j+2]).length
  contours.append(dict(line=li,sector=si,added_segments=n-1,maximum_inset=amp))
 vv=verts();polys={si:sector_polygon(g,si) for si in TARGETS}
 # Every mesh is wholly inside one original static grass region, clear of all
 # original lines and actor origins. Boundary height is exactly the old floor.
 updated_lines=[LineString([vv[int(l['v1'])],vv[int(l['v2'])]]) for l in g['linedef']]
 updated_tree=STRtree(updated_lines);meshes=[];occupied=[];rejections=collections.Counter()
 def mesh(si,cx,cy,rx,ry,angle,height,kind):
  s=g['sector'][si];floor=float(s['heightfloor']);N=9 if kind=='rock' else 10
  phase=rng.random()*6.28;outer=[]
  for j in range(N):
   a=2*math.pi*j/N;scale=1+.11*math.sin(3*a+phase)+.05*math.sin(5*a-phase)
   x,y=rx*math.cos(a)*scale,ry*math.sin(a)*scale
   outer.append((round(cx+x*math.cos(angle)-y*math.sin(angle),4),round(cy+x*math.sin(angle)+y*math.cos(angle),4),floor))
  p=Polygon([(x,y) for x,y,z in outer])
  if not p.is_valid or not polys[si].contains(p.buffer(2)):rejections[kind+'-outside']+=1;return False
  if any(p.buffer(2).intersects(updated_lines[j]) for j in updated_tree.query(p.buffer(2))):rejections[kind+'-line']+=1;return False
  if not p.disjoint(special) or len(thing_tree.query(p.buffer(48),predicate='intersects')):rejections[kind+'-protected']+=1;return False
  if any(p.distance(o)<24 for o in occupied):rejections[kind+'-occupied']+=1;return False
  # Keep ground relief low; slopes remain walkable (verified separately).
  inner=[]
  for j,(x,y,z) in enumerate(outer):
   scale=.48 if kind=='rock' else .46
   inner.append((round(cx+(x-cx)*scale+rx*.04,4),round(cy+(y-cy)*scale-ry*.06,4),round(floor+height*(.76+.17*math.sin(j*2.17+phase)),4)))
  points=outer+inner+[(round(cx-rx*.10,4),round(cy+ry*.04,4),floor+height)]
  tris=[]
  for j in range(N):
   k=(j+1)%N;tris.extend([(j,k,N+k),(j,N+k,N+j),(N+j,N+k,2*N)])
  # Check the actual piecewise-planar slopes before committing any geometry.
  planes=[]
  for tri in tris:
   a,b,c=[points[i] for i in tri];ux,uy,uz=[b[i]-a[i] for i in range(3)];vx,vy,vz=[c[i]-a[i] for i in range(3)]
   nx,ny,nz=uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx
   if nz<=0:return False
   nx,ny=nx/nz,ny/nz;nz=1
   if math.hypot(nx,ny)>.65:rejections[kind+'-slope']+=1;return False
   norm=math.sqrt(nx*nx+ny*ny+1)
   # UZDoom normalizes a/b/c on load but leaves d untouched.
   planes.append(tuple(value/norm for value in (nx,ny,1,-nx*a[0]-ny*a[1]-a[2])))
  vb=len(g['vertex']);sb=len(g['sector']);lb=len(g['linedef']);edges={}
  g['vertex'].extend(dict(x=x,y=y) for x,y,z in points)
  for ti,tri in enumerate(tris):
   fields=dict(s);fields['texturefloor']='"QROCK3"' if kind=='rock' and ti%3==2 else s['texturefloor']
   fields.update({f'floorplane_{k}':f'{value:.12f}' for k,value in zip('abcd',planes[ti])})
   g['sector'].append(fields);sec=sb+ti
   # Doom front sides face clockwise interiors.
   indices=list(reversed(tri))
   for a,b in zip(indices,indices[1:]+indices[:1]):
    sd=len(g['sidedef']);g['sidedef'].append(dict(sector=str(sec),texturebottom='"QROCK3"'))
    if (b,a) in edges:g['linedef'][edges[(b,a)]]['sideback']=str(sd)
    else:
     edges[(a,b)]=len(g['linedef']);g['linedef'].append(dict(v1=str(vb+a),v2=str(vb+b),sidefront=str(sd),twosided='true'))
  for li in range(lb,len(g['linedef'])):
   line=g['linedef'][li]
   if 'sideback' not in line:
    line['sideback']=str(len(g['sidedef']));g['sidedef'].append(dict(sector=str(si),texturebottom='"QROCK3"'))
  occupied.append(p);meshes.append(dict(kind=kind,parent=si,center=[cx,cy],radii=[rx,ry],height=height,first_sector=sb,sectors=len(tris),first_line=lb,vertices=points,footprint=list(p.exterior.coords)))
  return True
 for e in sorted(rock_edges,key=lambda e:-e['length']):
  si=e['sector'];a,b=e['a'],e['b'];nx,ny=e['normal'];angle=math.atan2(b[1]-a[1],b[0]-a[0]);length=e['length']
  for t in ([.25,.7] if length>400 else [.5]):
   ry=rng.uniform(58,84);rx=min(length*.40,rng.uniform(85,135));distance=ry*1.2+24
   cx=a[0]+(b[0]-a[0])*t+nx*distance;cy=a[1]+(b[1]-a[1])*t+ny*distance
   if not mesh(si,cx,cy,rx,ry,angle,rng.uniform(14,23),'rock'):
    # Smaller fractured outcrops fit between existing terrace corners.
    ry=32;rx=min(length*.30,74);distance=ry*1.2+24
    cx=a[0]+(b[0]-a[0])*t+nx*distance;cy=a[1]+(b[1]-a[1])*t+ny*distance
    mesh(si,cx,cy,rx,ry,angle,rng.uniform(7,11),'rock')
 # Sparse grass rises follow the open space; deterministic placement rejects
 # narrow strips, actors, triggers, sector islands and all existing geometry.
 for si in TARGETS:
  p=polys[si];xmin,ymin,xmax,ymax=p.bounds;limit=max(2,min(9,int(p.area/110000)));done=0
  for attempt in range(220):
   if done>=limit:break
   cx=rng.uniform(xmin,xmax);cy=rng.uniform(ymin,ymax)
   if mesh(si,cx,cy,rng.uniform(68,145),rng.uniform(48,92),rng.random()*math.pi,rng.uniform(7,14),'grass'):done+=1
 changes={k:{i:block(k,d) for i,d in enumerate(g[k][:counts[k]]) if d!=orig[k][i]} for k in g};cursor=collections.Counter()
 def replace(m):
  k=m[1];i=cursor[k];cursor[k]+=1;return changes[k].get(i,m[0])
 newtext=re.sub(PAT,replace,text)+'\n// TNT01_ORGANIC_V1: rock contours and sealed walkable terrain.\n'
 for k in g:newtext+=''.join(block(k,d) for d in g[k][counts[k]:])
 raw=Path(output).with_suffix('.raw.wad');raw.write_bytes(write_wad(magic,[(n,newtext.encode() if n.rstrip(b'\0')==b'TEXTMAP' else d) for n,d in lumps if n.rstrip(b'\0') not in (b'ZNODES',b'BLOCKMAP',b'REJECT')]))
 r=subprocess.run([str(zdbsp),'-q','-X','-g','-r','-o',str(output),str(raw)],capture_output=True,timeout=120)
 assert r.returncode==0,(r.stdout+r.stderr).decode(errors='replace')
 report=dict(source_sha256=hashlib.sha256(Path(source).read_bytes()).hexdigest(),output_sha256=hashlib.sha256(Path(output).read_bytes()).hexdigest(),original_counts=counts,added_counts={k:len(g[k])-counts[k] for k in g},contours=contours,meshes=meshes,nodebuilder=(r.stdout+r.stderr).decode(errors='replace'))
 Path(report_path).write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ('meshes','contours','nodebuilder')}));print('Contours',len(contours),'Meshes',collections.Counter(m['kind'] for m in meshes),'Rejections',rejections)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['source','output','zdbsp','report_path']:p.add_argument('--'+name.replace('_','-'),type=Path,required=True)
 build(**vars(p.parse_args()))
