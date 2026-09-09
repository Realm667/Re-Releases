"""Build guarded runtime alignment tables without rewriting any map WAD."""
from pathlib import Path
import collections, hashlib, json, math, sys, re
W=Path(__file__).resolve().parent
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import area_geometry as analyze
from expand_rock_walls import trails
from rover_plan import plan_rovers
from build_utnt import read_wad
analyze.W=W
SLOTS={'top':'texturetop','mid':'texturemiddle','bottom':'texturebottom'}
PART={'top':0,'mid':1,'bottom':2}

def build():
    materials=json.loads((W/'materials.json').read_text())
    lookup={m['name']:m for m in materials}
    lookup.update({m['alias']:m for m in materials})
    maps=json.loads((W/'map-data.json').read_text())
    out=W/'addon/areaalign';out.mkdir(parents=True,exist_ok=True)
    report={}
    for name,g in maps.items():
        runtime,rovs,mids=analyze.load_runtime(name)
        rows=[];groups=collections.defaultdict(list);counts=collections.Counter();seams=[]
        vertices=[(v['x'],v['y']) for v in g['vertex']]
        # Plane coordinates already use world-space mapping. Removing complete
        # original repeats preserves the old phase while sharing the new period.
        for i,s in enumerate(g['sector']):
            for part,plane in enumerate(['floor','ceiling']):
                old=s.get('texture'+plane,'').upper()
                if old not in lookup:continue
                m=lookup[old];ow,oh=m['original_size']
                x=float(s.get('xpanning'+plane,0));y=float(s.get('ypanning'+plane,0))
                rows.append(['F',i,part,old,m['alias'],x%ow,y%oh,x,y])
                counts[m['name']+'.'+plane]+=1
        for li,l in enumerate(g['linedef']):
            for face,key in enumerate(['sidefront','sideback']):
                si=int(l.get(key,-1));bi=int(l.get(['sideback','sidefront'][face],-1))
                if si<0:continue
                s=g['sidedef'][si];fs=int(s['sector']);bs=int(g['sidedef'][bi]['sector']) if bi>=0 else None
                a,b=vertices[int(l['v1'])],vertices[int(l['v2'])]
                if face:a,b=b,a
                length=math.dist(a,b);x,y=(a[0]+b[0])/2,(a[1]+b[1])/2
                f=runtime[fs];back=runtime[bs] if bs is not None else None
                fh=analyze.z(f['fp'],x,y);ch=analyze.z(f['cp'],x,y)
                bf=analyze.z(back['fp'],x,y) if back else fh
                bc=analyze.z(back['cp'],x,y) if back else ch
                per=collections.defaultdict(list)
                for tier,slot in SLOTS.items():
                    old=s.get(slot,'').upper()
                    if old not in lookup:continue
                    m=lookup[old];sx=float(s.get('scalex_'+tier,1));sy=float(s.get('scaley_'+tier,1))
                    finite=tier=='mid' and back is not None and l.get('special')!=160 and not (l.get('wrapmidtex') or s.get('wrapmidtex'))
                    alias=('XB'+m['alias'][2:]) if finite and not m['reuse'] else (m['name']+'B' if finite else m['alias'])
                    if tier=='mid':lo,hi=(max(fh,bf),min(ch,bc)) if back else (fh,ch)
                    elif tier=='top':lo,hi=max(fh,bc),ch
                    else:lo,hi=fh,min(bf,ch)
                    # Inactive tiers may become visible through a door or lift.
                    # Include their source assignment, with conservative bounds.
                    if hi<=lo:lo,hi=fh,ch
                    ox=float(s.get('offsetx',0))+float(s.get('offsetx_'+tier,0))
                    oy=float(s.get('offsety',0))+float(s.get('offsety_'+tier,0))
                    per[(m['name'],sx,sy)].append(dict(tier=tier,lo=lo,hi=hi,old=old,alias=alias,finite=finite,ox=ox,oy=oy))
                    counts[m['name']+'.wall']+=1
                for key,tiers in per.items():
                    groups[key].append(dict(line=li,side=si,face=face,sector=fs,backsector=bs,start=a,end=b,length=length,tiers=tiers))
        chains=[]
        for (material,sx,sy),edges in sorted(groups.items()):
            # Degenerate lines are still assigned, but are never graph links.
            positive=[e for e in edges if e['length']>1e-8]
            paths=trails(positive)+[([e],None) for e in edges if e['length']<=1e-8]
            for chain,seam in paths:
                length=sum(e['length'] for e in chain);new_sx=sx
                # Native WorldPanning offsets are world distances, including
                # per-side scaling; the renderer rounds its physical period.
                period=abs(math.ceil(lookup[material]['logical_size'][0]/sx)) if sx else lookup[material]['logical_size'][0]
                if seam and abs(length-round(length/period)*period)<.001:seam=None
                if seam:seams.append(dict(material=material,lines=[e['line'] for e in chain],**seam))
                anchor=math.ceil(max(t['hi'] for e in chain for t in e['tiers'])/128)*128
                u=chain[0]['tiers'][0]['ox']%lookup[material]['original_size'][0]
                chainrows=[]
                for e in chain:
                    for t in e['tiers']:
                        rows.append(['W',e['line'],e['face'],PART[t['tier']],t['old'],t['alias'],u%period,anchor,int(t['finite']),new_sx,sy,t['ox'],t['oy'],*e['start'],*e['end'],e['sector'],e['backsector'] if e['backsector'] is not None else -1,sx])
                        chainrows.append(len(rows)-1)
                    u+=e['length']
                chains.append(dict(material=material,length=length,rows=chainrows,closed_cut=seam is not None))
        roverrows,roverinfo=plan_rovers(g,runtime,rovs,mids,lookup)
        rows+=roverrows
        watchers=[]
        mapfile=W/'baseline/tutnt/maps'/(name.lower()+'.wad')
        script='\n'.join(d.decode(errors='replace') for n,d in read_wad(mapfile)[1] if n.rstrip(b'\0')==b'SCRIPTS')
        for plane,tag,texture in re.findall(r'\bChange(Floor|Ceiling)\s*\(\s*(\d+)\s*,\s*"([^"]+)"',script,re.I):
            texture=texture.upper()
            if texture not in lookup:continue
            m=lookup[texture]
            for si,sec in enumerate(g['sector']):
                tags={int(sec.get('id',0))}|{int(n) for n in re.findall(r'\d+',str(sec.get('moreids','')))}
                if int(tag) not in tags:continue
                row=['D',si,0 if plane.lower()=='floor' else 1,texture,m['alias'],*m['original_size']]
                if row not in watchers:watchers.append(row)
        rows+=watchers
        legacy=json.loads((W/'legacy.json').read_text()).get(name,[]) if (W/'legacy.json').exists() else []
        # Older committed TNT03B still has three middle textures removed by the
        # concurrent sky update. Accept them only when the old assignment exists.
        for row in legacy:
            line=g['linedef'][int(row[1])];si=int(line[['sidefront','sideback'][int(row[2])]])
            if g['sidedef'][si].get('texturemiddle','-')=='-':rows.append(row)
        header=['H',len(g['vertex']),len(g['linedef']),len(g['sidedef']),len(g['sector']),len(rows)]
        text='\n'.join('|'.join(format(v,'.9f').rstrip('0').rstrip('.') if isinstance(v,float) else str(v) for v in row) for row in [header]+rows)+'\n'
        (out/(name+'.txt')).write_text(text)
        report[name]=dict(counts=dict(counts),bindings=len(rows),dynamic_watchers=watchers,legacy_checks=sum(r[0]=='L' for r in rows),chains=chains,rover_chains=roverinfo,rover_bindings=len(roverrows),corner_cuts=seams,map_sha256=hashlib.sha256(mapfile.read_bytes()).hexdigest())
    (W/'plan.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:{'bindings':v['bindings'],'corner_cuts':len(v['corner_cuts'])} for k,v in report.items()},indent=2))

if __name__=='__main__':build()
