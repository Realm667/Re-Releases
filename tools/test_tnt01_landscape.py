"""Validate landscape topology, preserved contracts and actual plane geometry."""
import argparse,collections,hashlib,json,math
from pathlib import Path
from shapely.geometry import LineString,Point,Polygon
from shapely.ops import unary_union
from shapely.strtree import STRtree
from build_tnt01_organic import parse,sector_of
from build_tnt01_landscape import polygons
def verify(before,after,manifest):
 a=parse(before);b=parse(after);g=a[3];h=b[3];r=json.loads(Path(manifest).read_text());selected={m['sector'] for m in r['modified']};parent={m['sector']:m['parent'] for m in r['mesh']}
 assert g['thing']==h['thing']
 for n,d in a[1]:
  if n.rstrip(b'\0') not in (b'TEXTMAP',b'ZNODES',b'BLOCKMAP',b'REJECT'):assert dict(b[1])[n]==d,n
 for i,s in enumerate(g['sector']):
  if i not in selected:assert s==h['sector'][i],i
  else:
   allowed={'texturefloor','floorplane_a','floorplane_b','floorplane_c','floorplane_d'}
   assert {k:v for k,v in s.items() if k not in allowed}=={k:v for k,v in h['sector'][i].items() if k not in allowed},i
   assert not any(k in s for k in ('id','special','ceilingplane_a')),i
 for x,y in zip(g['sidedef'],h['sidedef']):
  assert {k:v for k,v in x.items() if k!='sector' and not k.startswith('offsetx_')}=={k:v for k,v in y.items() if k!='sector' and not k.startswith('offsetx_')}
 for i,l in enumerate(g['linedef']):
  assert {k:v for k,v in l.items() if k not in ('v1','v2')}=={k:v for k,v in h['linedef'][i].items() if k not in ('v1','v2')},i
  if int(l.get('special',0)) or int(l.get('id',0)):
   for key in ('v1','v2'):assert g['vertex'][int(l[key])]==h['vertex'][int(h['linedef'][i][key])]
 vertices=[(float(v['x']),float(v['y'])) for v in h['vertex']]
 lines=[LineString([vertices[int(l[k])] for k in ('v1','v2')]) for l in h['linedef']];tree=STRtree(lines)
 oldlines=[LineString([(float(g['vertex'][int(l[k])]['x']),float(g['vertex'][int(l[k])]['y'])) for k in ('v1','v2')]) for l in g['linedef']]
 changed=[i for i in range(len(lines)) if i>=len(oldlines) or lines[i]!=oldlines[i]];crossings=[]
 for i in changed:
  assert lines[i].length>1e-6,i
  for j in tree.query(lines[i]):
   if j!=i and lines[i].crosses(lines[j]):crossings.append((i,int(j)))
 assert not crossings,crossings[:12]
 def z(si,p):
  s=h['sector'][si]
  if 'floorplane_a' not in s:return float(s['heightfloor'])
  return -(float(s['floorplane_a'])*p[0]+float(s['floorplane_b'])*p[1]+float(s['floorplane_d']))/float(s['floorplane_c'])
 maxgap=0;seams=0;boundary_steps=[]
 for i,l in enumerate(h['linedef']):
  f,back=sector_of(h,l,'sidefront'),sector_of(h,l,'sideback')
  if i>=r['boundary_line_count']:
   assert f>=0 and back>=0 and l.get('twosided')=='true'
   assert parent[f]==parent[back]
   for key in ('v1','v2'):maxgap=max(maxgap,abs(z(f,vertices[int(l[key])])-z(back,vertices[int(l[key])])))
   seams+=1
  elif f>=0 and back>=0 and (f in parent or back in parent):
   pf,pb=parent.get(f,f),parent.get(back,back)
   if float(g['sector'][pf]['heightfloor'])==float(g['sector'][pb]['heightfloor']):
    gap=max(abs(z(f,vertices[int(l[key])])-z(back,vertices[int(l[key])])) for key in ('v1','v2'))
    if gap>.001:boundary_steps.append((i,pf,pb,gap))
 assert maxgap<1e-5,maxgap
 assert not boundary_steps,boundary_steps[:15]
 errors=[];slopes=[];walkpolys=collections.defaultdict(list);floor_changes=[]
 for m in r['mesh']:
  s=h['sector'][m['sector']];normal=[float(s['floorplane_'+k]) for k in 'abc'];assert abs(sum(v*v for v in normal)-1)<1e-10
  for x,y,height in m['points']:
   error=abs(z(m['sector'],(x,y))-height)
   if error>1e-5:errors.append((m['sector'],error))
  slope=math.hypot(*normal[:2])/normal[2];slopes.append(slope)
  if m['kind']=='grass':
   bh=float(g['sector'][m['parent']]['heightfloor'])
   if slope<=.7:walkpolys[bh].append(Polygon([(x,y) for x,y,height in m['points']]))
   floor_changes.extend(height-bh for x,y,height in m['points'])
 assert not errors,errors[:10]
 roots={int(k):int(v) for k,v in r['grass_roots'].items()};old_regions=polygons(g,set(roots));groups=collections.defaultdict(list)
 for si,p in old_regions.items():groups[float(g['sector'][si]['heightfloor'])].append(p)
 nav=[]
 for bh,parts in groups.items():
  old=unary_union(parts).buffer(-16);new=unary_union(walkpolys[bh]).buffer(-16)
  oldparts=[p for p in (old.geoms if hasattr(old,'geoms') else [old]) if p.area>4096]
  newparts=[p for p in (new.geoms if hasattr(new,'geoms') else [new]) if p.area>4096]
  nav.append(dict(floor=bh,old_area=old.area,new_walkable_area=new.area,area_loss_percent=100*(1-new.intersection(old).area/max(old.area,1)),original_components=len(oldparts),new_components=len(newparts)))
  assert len(newparts)==len(oldparts),('outdoor route network split',nav[-1])
  matching=[max(range(len(newparts)),key=lambda j:p.intersection(newparts[j]).area) for p in oldparts]
  assert len(set(matching))==len(oldparts),('distinct outdoor areas no longer correspond',nav[-1])
  assert all(p.intersection(newparts[j]).area>4096 for p,j in zip(oldparts,matching))
 result=dict(ok=True,before=r['before'],after=r['after'],split_lines=len(r['split']),rounded_corners=len(r['moved']),curved_runs=len(r['contoured']),rock_terraces=len(r['rock_sectors']),meshed_triangles=len(r['mesh']),modified_regions=len(selected),new_internal_seams=seams,maximum_seam_error=maxgap,changed_lines_checked=len(changed),maximum_slope=max(slopes),grass_height_change_range=[min(floor_changes),max(floor_changes)],navigation=nav,checks=['all Things and ACS unchanged','all non-target sectors unchanged','ceilings, lighting and original wall materials preserved','action lines retain geometry and definitions','no new crossing lines','normalized terrain planes match intended heights','no cracks or new steps across originally level joins'])
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for key in ['before','after','manifest','output']:p.add_argument('--'+key,type=Path,required=True)
 a=p.parse_args();result=verify(a.before,a.after,a.manifest);a.output.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
