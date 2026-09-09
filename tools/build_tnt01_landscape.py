"""Remesh TNT01's continuous outdoor terrain and bevel its rock terraces.
Python 3.12, Shapely 2.1 / GEOS 3.10+, ZDBSP. Input is never overwritten.
All existing Things, ACS, materials on existing walls and action definitions
survive; original sector slots are reused for the first triangle of each region.
"""
import argparse,collections,hashlib,json,math,random,re,subprocess,sys
from pathlib import Path
from shapely import constrained_delaunay_triangles
from shapely.geometry import Point,LineString,Polygon
from shapely.ops import polygonize,unary_union
from shapely.strtree import STRtree
from build_utnt import read_wad,write_wad
from build_tnt01_organic import parse,block,sector_of,PAT
PARENTS=[884,1458,1478,2404,3676,3678]
def xy(g):return [(float(v['x']),float(v['y'])) for v in g['vertex']]
def smooth(x):x=max(0.,min(1.,x));return x*x*(3-2*x)
def polygons(g,selection):
 verts=xy(g);edges=collections.defaultdict(list)
 for l in g['linedef']:
  f,b=sector_of(g,l,'sidefront'),sector_of(g,l,'sideback')
  if f==b:continue
  a,c=verts[int(l['v1'])],verts[int(l['v2'])]
  if f in selection:edges[f].append((a,c))
  if b in selection:edges[b].append((c,a))
 result={}
 for si in sorted(selection):
  def inside(p):
   winding=0
   for (x,y),(xx,yy) in edges[si]:
    cross=(xx-x)*(p.y-y)-(p.x-x)*(yy-y)
    if y<=p.y<yy and cross>0:winding+=1
    elif yy<=p.y<y and cross<0:winding-=1
   return winding!=0
  result[si]=unary_union([p for p in polygonize([LineString(e) for e in edges[si]]) if inside(p.representative_point())])
  assert result[si].is_valid and result[si].area>0,si
 return result
def build(source,output,zdbsp,v1_manifest,report_path,routes):
 magic,lumps,text,g=parse(source);original={k:[dict(x) for x in a] for k,a in g.items()};base={k:len(v) for k,v in g.items()}
 assert base['sector']==4522 and base['linedef']==21320,'Requires reviewed first-pass TNT01 baseline'
 rng=random.Random(667020);grass=set(PARENTS);root_of={s:s for s in PARENTS}
 for m in json.loads(Path(v1_manifest).read_text())['meshes']:
  for si in range(m['first_sector'],m['first_sector']+m['sectors']):grass.add(si);root_of[si]=m['parent']
 neighbors=collections.defaultdict(set);incident=collections.defaultdict(list)
 for i,l in enumerate(g['linedef']):
  f,b=sector_of(g,l,'sidefront'),sector_of(g,l,'sideback')
  if min(f,b)>=0:neighbors[f].add(b);neighbors[b].add(f)
  for key in ('v1','v2'):incident[int(l[key])].append(i)
 def natural(si):
  s=g['sector'][si]
  adjacent_grass=[float(g['sector'][root_of[j]]['heightfloor']) for j in neighbors[si] if j in grass]
  if adjacent_grass and float(s['heightfloor'])<min(adjacent_grass)+32:return False
  return s.get('texturefloor') in ('"GRAVE02"','"QROCK3"','"QROCK1"') and s.get('textureceiling')=='"F_SKY1"' and not any(k in s for k in ('id','special','floorplane_a','ceilingplane_a')) and float(s['heightceiling'])-float(s['heightfloor'])>=80
 rocks=set();front=set(grass)
 for depth in range(3):
  new={j for si in front for j in neighbors[si] if j not in grass|rocks and natural(j)}
  rocks|=new;front=new
 selected=grass|rocks;vv=xy(g)
 line_geoms=[LineString([vv[int(l['v1'])],vv[int(l['v2'])]]) for l in g['linedef']];tree=STRtree(line_geoms)
 objects=[Point(float(t['x']),float(t['y'])) for t in g['thing']];object_tree=STRtree(objects)
 specials=[line_geoms[i] for i,l in enumerate(g['linedef']) if int(l.get('special',0)) or int(l.get('id',0))]
 special_union=unary_union(specials)
 moved=[]
 # Round plan-view corners of natural terrain; connected edges share the same
 # moved vertex. Architecturally shared vertices and action lines stay fixed.
 for vi,lines in sorted(incident.items()):
  connected={sector_of(g,g['linedef'][li],side) for li in lines for side in ('sidefront','sideback')}-{ -1 }
  if not connected<=selected or not (connected&rocks or any(sector_of(g,g['linedef'][li],'sideback')<0 for li in lines)):continue
  if 'zfloor' in g['vertex'][vi] or 'zceiling' in g['vertex'][vi]:continue
  if any(int(g['linedef'][li].get(k,0)) for li in lines for k in ('special','id')):continue
  p=Point(vv[vi])
  if p.distance(special_union)<112 or len(object_tree.query(p.buffer(80),predicate='intersects')):continue
  wall_neighbors=[]
  for li in lines:
   l=g['linedef'][li];f,b=sector_of(g,l,'sidefront'),sector_of(g,l,'sideback')
   if b>=0 and abs(float(g['sector'][f]['heightfloor'])-float(g['sector'][b]['heightfloor']))<24:continue
   wall_neighbors.append(vv[int(l['v2']) if int(l['v1'])==vi else int(l['v1'])])
  if len(wall_neighbors)<2:continue
  tx=sum(p[0] for p in wall_neighbors)/len(wall_neighbors);ty=sum(p[1] for p in wall_neighbors)/len(wall_neighbors)
  dx,dy=(tx-vv[vi][0])*.23,(ty-vv[vi][1])*.23;length=math.hypot(dx,dy)
  if length<2:continue
  if length>24:dx*=24/length;dy*=24/length
  proposed=(round(vv[vi][0]+dx,6),round(vv[vi][1]+dy,6));newlines={}
  for li in lines:
   l=g['linedef'][li];newlines[li]=LineString([proposed if int(l[k])==vi else vv[int(l[k])] for k in ('v1','v2')])
  if any(n.length<8 or any(int(j) not in lines and n.crosses(line_geoms[j]) for j in tree.query(n.buffer(32))) for n in newlines.values()):continue
  moved.append(dict(vertex=vi,before=vv[vi],after=proposed));vv[vi]=proposed;g['vertex'][vi].update(x=str(proposed[0]),y=str(proposed[1]))
  for li,n in newlines.items():line_geoms[li]=n
 # Split ALL long outdoor boundaries, including grass/rock joins and terrace
 # edges. Keep a common geometric edge on both sides and preserve wall UV phase.
 split=[];contoured=[]
 for li,l0 in enumerate(original['linedef']):
  l=dict(g['linedef'][li]);f,b=sector_of(g,l,'sidefront'),sector_of(g,l,'sideback')
  if not ({f,b}&selected) or int(l.get('special',0)) or int(l.get('id',0)):continue
  a,c=vv[int(l['v1'])],vv[int(l['v2'])];length=math.dist(a,c)
  if length<=56:continue
  n=math.ceil(length/48);points=[a]+[(round(a[0]+(c[0]-a[0])*j/n,8),round(a[1]+(c[1]-a[1])*j/n,8)) for j in range(1,n)]+[c]
  wall_material=any('QROCK' in g['sidedef'][int(l[side])].get(key,'') for side in ('sidefront','sideback') if side in l and int(l[side])>=0 for key in ('texturemiddle','texturebottom','texturetop'))
  rise=999 if b<0 else abs(float(g['sector'][f]['heightfloor'])-float(g['sector'][b]['heightfloor']))
  if wall_material and rise>=32 and (b<0 or not any(int(g['sector'][si].get('id',0)) for si in (f,b))):
   lower=f if b<0 or float(g['sector'][f]['heightfloor'])<float(g['sector'][b]['heightfloor']) else b
   nx,ny=(c[1]-a[1])/length,-(c[0]-a[0])/length
   if lower==b:nx,ny=-nx,-ny
   amp=min(30,length*.13);phase=li*.61803398875;curved=[a]
   for j,p0 in enumerate(points[1:-1],1):
    p=Point(p0);dist=p.distance(objects[int(object_tree.nearest(p))]);pin=smooth((dist-48)/64)*smooth((p.distance(special_union)-48)/80)
    shift=amp*math.sin(math.pi*j/n)*(.72+.28*math.sin(3*math.pi*j/n+phase))*pin
    curved.append((round(p0[0]+nx*shift,8),round(p0[1]+ny*shift,8)))
   curved.append(c);path=LineString(curved)
   if path.is_simple and not any(int(j)!=li and path.crosses(line_geoms[j]) for j in tree.query(path.buffer(48))):
    points=curved;line_geoms[li]=path
    if max(LineString([a,c]).distance(Point(point)) for point in curved)>.1:contoured.append(li)
  spans=[math.dist(p,q) for p,q in zip(points,points[1:])];total=sum(spans);travel=0.
  ids=[int(l['v1'])]
  for p in points[1:-1]:ids.append(len(g['vertex']));g['vertex'].append(dict(x=str(p[0]),y=str(p[1])))
  ids.append(int(l['v2']))
  for j,(va,vb) in enumerate(zip(ids,ids[1:])):
   nl=dict(l,v1=str(va),v2=str(vb))
   for side in ('sidefront','sideback'):
    if side not in l or int(l[side])<0:continue
    sd=dict(original['sidedef'][int(l[side])]);dist=travel if side=='sidefront' else total-travel-spans[j]
    # Slot offsets provide exact fractional UV shifts for both legacy and X8 walls.
    if dist:
     for slot,key in [('mid','texturemiddle'),('top','texturetop'),('bottom','texturebottom')]:
      if sd.get(key,'"-"')!='"-"':sd['offsetx_'+slot]=str(round(float(sd.get('offsetx_'+slot,0))+dist,8))
    if j==0:g['sidedef'][int(l[side])]=sd;nl[side]=l[side]
    else:nl[side]=str(len(g['sidedef']));g['sidedef'].append(sd)
   if j==0:g['linedef'][li]=nl
   else:g['linedef'].append(nl)
   travel+=spans[j]
  split.append(dict(line=li,length=length,segments=n))
 print('Selection',len(grass),'grass sectors +',len(rocks),'rock terraces;',len(moved),'rounded corners;',len(split),'split lines;',len(contoured),'curved wall runs',flush=True)
 vv=xy(g);regions=polygons(g,selected);grass_groups=collections.defaultdict(list)
 for si in grass:grass_groups[float(g['sector'][root_of[si]]['heightfloor'])].append(regions[si])
 grass_unions={h:unary_union(p) for h,p in grass_groups.items()}
 ber_edges=collections.defaultdict(list);hard_edges=collections.defaultdict(list);drop_edges=collections.defaultdict(list);rock_hard_edges=collections.defaultdict(list)
 for l in g['linedef']:
  f,b=sector_of(g,l,'sidefront'),sector_of(g,l,'sideback');geom=LineString([vv[int(l['v1'])],vv[int(l['v2'])]])
  for si,other,side in [(f,b,'sidefront'),(b,f,'sideback')]:
   if si<0:continue
   h=float(g['sector'][si]['heightfloor'])
   if si in grass and other not in grass:
    sd=g['sidedef'][int(l[side])];isrock='QROCK' in sd.get('texturemiddle' if other<0 else 'texturebottom','')
    rise=float(g['sector'][si]['heightceiling'])-h if other<0 else float(g['sector'][other]['heightfloor'])-h
    if isrock and rise>=40:ber_edges[h].append((geom,min(96,rise*.45)))
    else:hard_edges[h].append(geom)
   if si in rocks and (other<0 or float(g['sector'][other]['heightfloor'])<h-20):drop_edges[h].append(geom)
   if si in rocks and other>=0 and other not in rocks and abs(float(g['sector'][other]['heightfloor'])-h)<20:rock_hard_edges[h].append(geom)
 hard={h:unary_union(lines) for h,lines in hard_edges.items()};drops={h:unary_union(lines) for h,lines in drop_edges.items()};rock_hard={h:unary_union(lines) for h,lines in rock_hard_edges.items()}
 berm_trees={h:STRtree([line for line,rise in lines]) for h,lines in ber_edges.items()}
 route_data=json.loads(Path(routes).read_text())['routes'];route_groups=collections.defaultdict(list)
 for route in route_data:route_groups[route['floor']].append(LineString(route['points']))
 route_lines={h:unary_union(lines) for h,lines in route_groups.items()}
 height_cache={};berm_cache={}
 def height(si,x,y):
  isgrass=si in grass;baseh=float(g['sector'][root_of[si] if isgrass else si]['heightfloor']);key=(isgrass,baseh,x,y)
  if key in height_cache:return height_cache[key]
  p=Point(x,y);obj_distance=p.distance(objects[int(object_tree.nearest(p))]);pin=smooth((obj_distance-48)/64)*smooth((p.distance(special_union)-48)/80)
  if isgrass:
   if baseh in route_lines:pin*=smooth((route_lines[baseh].distance(p)-80)/64)
   edge=grass_unions[baseh].boundary.distance(p);safe=smooth(hard[baseh].distance(p)/88) if baseh in hard else 1.
   wave=(12*math.sin(x/170+y/235)+8*math.cos(x/97-y/180)+5*math.sin(y/78+x/119))*smooth(edge/96)
   berm=0.
   if baseh in berm_trees:
    for idx in berm_trees[baseh].query(p.buffer(176)):
     line,rise=ber_edges[baseh][idx];d=line.distance(p);berm=max(berm,rise*(1-smooth(d/152)))
   offset=(wave+berm)*pin*safe;berm_cache[key]=berm*pin*safe
  else:
   d=drops[baseh].distance(p) if baseh in drops else 1000
   # Bevel the actual terrace rim down, with a gently crowned interior.
   depth=min(38,max(18,abs(baseh)*.13));bevel=-depth*(1-smooth(d/52))
   crown=(10+7*math.sin(x/89+y/117))*smooth(d/44)
   join=smooth(rock_hard[baseh].distance(p)/64) if baseh in rock_hard else 1.
   offset=(bevel+crown)*pin*join
  value=round(baseh+offset,8);height_cache[key]=value;return value
 vertex_ids={tuple(round(p,8) for p in point):i for i,point in enumerate(vv)}
 def vertex(p):
  key=tuple(round(c,8) for c in p)
  if key not in vertex_ids:
   vertex_ids[key]=len(g['vertex']);g['vertex'].append(dict(x=str(key[0]),y=str(key[1])));vv.append(key)
  return vertex_ids[key]
 def cdt(poly):
  out=[]
  for p in constrained_delaunay_triangles(poly).geoms:
   ids=[vertex(point) for point in list(p.exterior.coords)[:-1]];assert len(ids)==3
   a,b,c=[vv[i] for i in ids]
   if (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])<0:ids.reverse()
   out.append(tuple(ids))
  return out
 line_lookup={tuple(sorted((int(l['v1']),int(l['v2'])))):i for i,l in enumerate(g['linedef'])}
 mesh=[];modified=[];boundary_count=len(g['linedef'])
 for si in sorted(selected):
  region=regions[si];tris=[]
  for poly in region.geoms if hasattr(region,'geoms') else [region]:tris+=cdt(poly)
  # Conforming edge refinement: neighboring triangles use the identical midpoint.
  for iteration in range(9):
   marks={}
   for tri in tris:
    for a,b in zip(tri,tri[1:]+tri[:1]):
     key=tuple(sorted((a,b)))
     if key not in line_lookup and math.dist(vv[a],vv[b])>128:marks[key]=vertex(((vv[a][0]+vv[b][0])/2,(vv[a][1]+vv[b][1])/2))
   if not marks:break
   refined=[]
   for tri in tris:
    ring=[]
    for a,b in zip(tri,tri[1:]+tri[:1]):
     ring.append(vv[a]);mid=marks.get(tuple(sorted((a,b))))
     if mid is not None:ring.append(vv[mid])
    refined+=cdt(Polygon(ring))
   tris=refined
  if si in rocks:
   detailed=[]
   for tri in tris:
    if Polygon([vv[i] for i in tri]).area>160:
     mid=vertex((sum(vv[i][0] for i in tri)/3,sum(vv[i][1] for i in tri)/3))
     detailed.extend((a,b,mid) for a,b in zip(tri,tri[1:]+tri[:1]))
    else:detailed.append(tri)
   tris=detailed
  fields_base=dict(original['sector'][root_of[si] if si in grass else si]);first=True
  for tri in tris:
   points=[(*vv[i],height(si,*vv[i])) for i in tri];a,b,c=points
   ux,uy,uz=[b[i]-a[i] for i in range(3)];vx,vy,vz=[c[i]-a[i] for i in range(3)]
   normal=(uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx);norm=math.sqrt(sum(n*n for n in normal));assert normal[2]>0
   normal=tuple(n/norm for n in normal);d=-sum(normal[i]*a[i] for i in range(3))
   fields=dict(fields_base);fields.update({f'floorplane_{k}':f'{v:.14f}' for k,v in zip('abcd',(*normal,d))})
   if si in grass:
    bh=float(fields_base['heightfloor']);berm=sum(berm_cache.get((True,bh,p[0],p[1]),0) for p in points)/3
    fields['texturefloor']='"QROCK3"' if berm>22 else '"QGRASS"'
   if first:sec=si;g['sector'][sec]=fields;first=False
   else:sec=len(g['sector']);g['sector'].append(fields)
   mesh.append(dict(sector=sec,parent=si,kind='grass' if si in grass else 'rock',points=points))
   # Front sides face clockwise; existing boundary materials/UVs stay attached.
   clockwise=tuple(reversed(tri))
   for va,vb in zip(clockwise,clockwise[1:]+clockwise[:1]):
    key=tuple(sorted((va,vb)))
    if key in line_lookup:
     line=g['linedef'][line_lookup[key]];side='sidefront' if (int(line['v1']),int(line['v2']))==(va,vb) else 'sideback'
     if side in line and int(line[side])>=0:g['sidedef'][int(line[side])]['sector']=str(sec)
     else:
      line[side]=str(len(g['sidedef']));g['sidedef'].append(dict(sector=str(sec),texturebottom='"QROCK3"'));line['twosided']='true'
    else:
     side=len(g['sidedef']);g['sidedef'].append(dict(sector=str(sec),texturebottom='"QROCK3"'))
     line_lookup[key]=len(g['linedef']);g['linedef'].append(dict(v1=str(va),v2=str(vb),sidefront=str(side)))
  modified.append(dict(sector=si,triangles=len(tris),area=region.area,kind='grass' if si in grass else 'rock'))
 for line in g['linedef'][boundary_count:]:assert 'sideback' in line,'Unsealed terrain edge'
 print('Meshed',len(mesh),'triangles;',len(g['sector'])-base['sector'],'added sectors',flush=True)
 cursor=collections.Counter()
 def edit(m):
  k=m[1];i=cursor[k];cursor[k]+=1;return block(k,g[k][i]) if g[k][i]!=original[k][i] else m[0]
 newtext=re.sub(PAT,edit,text)+'\n// TNT01_LANDSCAPE_V2\n'
 for k in g:newtext+=''.join(block(k,d) for d in g[k][base[k]:])
 raw=Path(output).with_suffix('.raw.wad');raw.write_bytes(write_wad(magic,[(n,newtext.encode() if n.rstrip(b'\0')==b'TEXTMAP' else d) for n,d in lumps if n.rstrip(b'\0') not in (b'ZNODES',b'BLOCKMAP',b'REJECT')]))
 result=subprocess.run([str(zdbsp),'-q','-X','-g','-r','-o',str(output),str(raw)],capture_output=True,timeout=120)
 assert result.returncode==0,(result.stdout+result.stderr).decode(errors='replace')
 report=dict(source_sha256=hashlib.sha256(Path(source).read_bytes()).hexdigest(),output_sha256=hashlib.sha256(Path(output).read_bytes()).hexdigest(),before=base,after={k:len(v) for k,v in g.items()},moved=moved,split=split,contoured=contoured,boundary_line_count=boundary_count,modified=modified,mesh=mesh,grass_roots=root_of,rock_sectors=sorted(rocks),routes=route_data)
 Path(report_path).write_text(json.dumps(report,indent=2));Path(report_path).with_suffix('.nodes.log').write_bytes(result.stdout+result.stderr)
 print(json.dumps({k:v for k,v in report.items() if k in ('before','after','source_sha256','output_sha256')}),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['source','output','zdbsp','v1_manifest','report_path','routes']:p.add_argument('--'+name.replace('_','-'),type=Path,required=True)
 build(**vars(p.parse_args()))
