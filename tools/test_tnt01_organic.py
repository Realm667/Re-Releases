"""Validate TNT01 topology, script preservation, mesh seams and walkable slopes."""
import argparse,collections,hashlib,json,math
from pathlib import Path
from build_tnt01_organic import parse,sector_polygon,sector_of,TARGETS,Point,LineString,Polygon,STRtree,unary_union
def verify(before,after,manifest):
 _,ol,_,a=parse(before);_,nl,_,b=parse(after);r=json.loads(Path(manifest).read_text());n=r['original_counts']
 assert hashlib.sha256(Path(before).read_bytes()).hexdigest()==r['source_sha256']
 assert hashlib.sha256(Path(after).read_bytes()).hexdigest()==r['output_sha256']
 old={k.rstrip(b'\0'):v for k,v in ol};new={k.rstrip(b'\0'):v for k,v in nl}
 for k in old:
  if k not in (b'TEXTMAP',b'ZNODES',b'BLOCKMAP',b'REJECT'):assert old[k]==new[k],k
 for k in ('thing','sector'):assert a[k]==b[k][:n[k]],k
 # ZDBSP reorders vertex storage when earlier walls gain new intermediate
 # vertices. Compare coordinates and resolved endpoints, not storage offsets.
 vertex_key=lambda v:tuple(sorted(v.items()))
 assert not (collections.Counter(map(vertex_key,a['vertex']))-collections.Counter(map(vertex_key,b['vertex'])))
 for x,y in zip(a['sidedef'],b['sidedef']):assert {k:v for k,v in x.items() if k!='offsetx'}=={k:v for k,v in y.items() if k!='offsetx'}
 assert len(b['thing'])==len(a['thing']);changed={c['line'] for c in r['contours']}
 for i,l in enumerate(a['linedef']):
  if i not in changed:
   assert {k:v for k,v in l.items() if k not in ('v1','v2')}=={k:v for k,v in b['linedef'][i].items() if k not in ('v1','v2')},i
   for key in ('v1','v2'):assert a['vertex'][int(l[key])]==b['vertex'][int(b['linedef'][i][key])],i
  else:
   assert int(l.get('special','0'))==int(l.get('id','0'))==0
   assert {k:v for k,v in l.items() if k not in ('v1','v2','sidefront','sideback')}=={k:v for k,v in b['linedef'][i].items() if k not in ('v1','v2','sidefront','sideback')}
   for side in ('sidefront','sideback'):assert sector_of(a,l,side)==sector_of(b,b['linedef'][i],side)
 for l in b['linedef'][n['linedef']:]:assert int(l.get('special','0'))==int(l.get('id','0'))==0
 vertices=[(float(v['x']),float(v['y'])) for v in b['vertex']]
 lines=[LineString([vertices[int(l['v1'])],vertices[int(l['v2'])]]) for l in b['linedef']]
 tree=STRtree(lines);checked=0
 for i in list(changed)+list(range(n['linedef'],len(lines))):
  assert lines[i].length>.001,i
  for j in tree.query(lines[i]):
   if i!=j:assert not lines[i].crosses(lines[j]),('crossing',i,int(j))
  checked+=1
 def z(si,vi):
  s=b['sector'][si];x,y=vertices[vi]
  if 'floorplane_a' not in s:return float(s['heightfloor'])
  return -(float(s['floorplane_a'])*x+float(s['floorplane_b'])*y+float(s['floorplane_d']))/float(s['floorplane_c'])
 maxgap=0;maxslope=0;seams=0
 for l in b['linedef']:
  f,back=sector_of(b,l,'sidefront'),sector_of(b,l,'sideback')
  if max(f,back)<n['sector']:continue
  assert f>=0 and back>=0 and l.get('twosided')=='true'
  for key in ('v1','v2'):
   vi=int(l[key]);gap=abs(z(f,vi)-z(back,vi));maxgap=max(maxgap,gap);assert gap<.00001,(f,back,gap)
  seams+=1
 for s in b['sector'][n['sector']:]:
  assert abs(math.sqrt(sum(float(s['floorplane_'+k])**2 for k in 'abc'))-1)<1e-10,'UDMF normals must already be normalized'
  slope=math.hypot(float(s['floorplane_a']),float(s['floorplane_b']))/float(s['floorplane_c']);maxslope=max(maxslope,slope);assert slope<=.650001
  assert not any(k in s for k in ('special','id','damageamount','friction','gravity'))
 oldpolys={si:sector_polygon(a,si) for si in TARGETS}
 objects=[Point(float(t['x']),float(t['y'])) for t in a['thing']];object_tree=STRtree(objects)
 footprints=[]
 for m in r['meshes']:
  p=Polygon(m['footprint']);assert oldpolys[m['parent']].contains(p)
  assert not len(object_tree.query(p.buffer(47.99),predicate='intersects'))
  for q in footprints:assert p.disjoint(q)
  footprints.append(p)
 # Compare connected components of the original grass route with radius 32.
 # Sloped inserts count as the parent region because all pass the slope test.
 contour_only={k:list(v) for k,v in b.items()}
 contour_only['linedef']=[l for l in b['linedef'] if max(sector_of(b,l,'sidefront'),sector_of(b,l,'sideback'))<n['sector']]
 connectivity=[]
 for si in TARGETS:
  bp=oldpolys[si].buffer(-32);ap=sector_polygon(contour_only,si).buffer(-32)
  oldparts=list(bp.geoms) if hasattr(bp,'geoms') else [bp];newparts=list(ap.geoms) if hasattr(ap,'geoms') else [ap]
  for piece in oldparts:
   if piece.area<4096:continue
   overlaps=[part for part in newparts if part.intersection(piece).area>512]
   assert len(overlaps)==1,('split walkable area',si,len(overlaps))
  loss=bp.difference(ap).area/max(bp.area,1);assert loss<.03,(si,loss)
  connectivity.append(dict(sector=si,walkable_area_loss_percent=round(loss*100,3)))
 return dict(ok=True,checks=['all 2648 original things unchanged','all original vertex coordinates and sector properties preserved; ZDBSP vertex order may change','original sidedef materials and sector links preserved; contour texture offsets adjusted','ACS and auxiliary lumps byte-identical','action and tagged linedef geometry unchanged','new edges do not cross existing or new edges','new floor seams continuous','all new slopes walkable <= 0.65','48-unit clearance around original actor origins','six grass regions retain radius-32 connectivity'],added=r['added_counts'],contours=len(r['contours']),formations=dict(collections.Counter(m['kind'] for m in r['meshes'])),checked_lines=checked,seams=seams,maximum_seam_error=maxgap,maximum_slope=maxslope,connectivity=connectivity)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for k in ('before','after','manifest','output'):p.add_argument('--'+k,type=Path,required=True)
 a=p.parse_args();r=verify(a.before,a.after,a.manifest);a.output.write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
