"""Plan/apply scoped expanded-rock wall mappings; no geometry or global replacement.

Outputs separate WADs and a reproducible per-field manifest. Source maps are
never written. Only static, unscaled opaque wall sections are selected.
"""
import argparse,collections,hashlib,json,math,re
from pathlib import Path
from build_utnt import read_wad,write_wad

BLOCK=re.compile(r'\b(vertex|linedef|sidedef|sector|thing)\s*(?://[^\n]*\n\s*)?\{([^}]*)\}')
SLOTS={'mid':'texturemiddle','top':'texturetop','bottom':'texturebottom'}
MOTION=re.compile(r'^(?:Door_|Floor_|Ceiling_|Elevator_|Pillar_|Plat_|Stairs_|Generic_|Sector_Set3dFloor|Plane_)',re.I)
PERIOD=1024.;MATERIALS={f'QROCK{n}':f'QROCK{n}X8' for n in [1,3,4,5]}

def parse(raw):
    groups=collections.defaultdict(list);blocks=collections.defaultdict(list)
    for m in BLOCK.finditer(raw):
        groups[m[1]].append(dict(re.findall(r'(\w+)\s*=\s*([^;]+);',m[2])))
        blocks[m[1]].append(m)
    return groups,blocks

def number(obj,key,default=0):return float(obj.get(key,default))
def tag(sec):return int(sec.get('id',0))
def height(sec,plane):return number(sec,'height'+plane)

def context(g,e):
    l=g['linedef'][e['line']];s=g['sidedef'][e['side']]
    sides=[int(l.get(k,-1)) for k in ['sidefront','sideback']]
    assert e['side'] in sides
    points=[tuple(number(g['vertex'][int(l[k])],c) for c in ['x','y']) for k in ['v1','v2']]
    if sides[1]==e['side']:points.reverse()
    sectors=[]
    for si in sides:
        if si<0:sectors.append(None);continue
        sec=g['sector'][int(g['sidedef'][si]['sector'])]
        sectors.append({k:v for k,v in sec.items() if k.startswith(('height','floorplane_','ceilingplane_')) or k in ['textureceiling','id','moreids']})
    return {'sides':sides,'points':points,'sectors':sectors,'flags':{k:l.get(k) for k in ['dontpegtop','dontpegbottom','special','id','moreids']},'mapping':{k:v for k,v in s.items() if k in ['offsetx','offsety','sector'] or k.startswith(('scalex_','scaley_','skew_'))}}

def excluded_sectors(g,scripts,actions):
    """Conservative static motion analysis; runtime checks complement this filter."""
    tags=set();local=set();unknown=False
    for line in g['linedef']:
        name=actions.get(str(int(line.get('special',0))), '')
        if MOTION.match(name):
            value=int(line.get('arg0',0))
            if value:tags.add(value)
            else:
                for face in ['sidefront','sideback']:
                    si=int(line.get(face,-1))
                    if si>=0:local.add(int(g['sidedef'][si]['sector']))
    scripts=re.sub(r'/\*.*?\*/|//[^\n]*','',scripts,flags=re.S)
    for name,argument in re.findall(r'\b([a-zA-Z_]\w*)\s*\(\s*([^,\)]+)',scripts):
        if MOTION.match(name):
            try:tags.add(int(argument.strip(),0))
            except ValueError:unknown=True
    for i,s in enumerate(g['sector']):
        if tag(s) in tags or (unknown and tag(s)) or s.get('moreids'):
            local.add(i)
        if any(k.startswith(('ceilingplane_','floorplane_')) for k in s):local.add(i)
    return local,{'motion_tags':sorted(tags),'unknown_motion_argument':unknown,'excluded_sectors':len(local)}

def collect(g,blocked):
    out=collections.defaultdict(list);skips=collections.Counter()
    for li,line in enumerate(g['linedef']):
        for face,other in [('sidefront','sideback'),('sideback','sidefront')]:
            si=int(line.get(face,-1));bi=int(line.get(other,-1))
            if si<0:continue
            s=g['sidedef'][si];fs=int(s['sector']);bs=int(g['sidedef'][bi]['sector']) if bi>=0 else None
            f=g['sector'][fs];b=g['sector'][bs] if bs is not None else None
            a,z=[tuple(number(g['vertex'][int(line[k])],c) for c in ['x','y']) for k in ['v1','v2']]
            if face=='sideback':a,z=z,a
            length=math.dist(a,z)
            per=collections.defaultdict(list)
            for tier,slot in SLOTS.items():
                material=s.get(slot,'').strip('"').upper()
                if material not in MATERIALS:continue
                if fs in blocked or bs in blocked:skips['moving_tagged_or_sloped']+=1;continue
                if int(line.get('special',0)) or int(line.get('id',0)) or line.get('moreids'):
                    skips['special_or_addressable_line']+=1;continue
                if any(number(s,'scale'+axis+'_'+tier,1)!=1 for axis in ['x','y']) or any(k in s for k in ['skew_'+tier,'lightabsolute_'+tier]):
                    skips['custom_mapping']+=1;continue
                if length<=0:continue
                if tier=='mid':
                    if b is not None:skips['masked_middle']+=1;continue
                    lo,hi=height(f,'floor'),height(f,'ceiling')
                    ref=lo+PERIOD if line.get('dontpegbottom')=='true' else hi
                elif b is None:continue
                elif tier=='top':
                    if f.get('textureceiling')=='"F_SKY1"' and b.get('textureceiling')=='"F_SKY1"':continue
                    lo=max(height(b,'ceiling'),height(f,'floor'));hi=height(f,'ceiling')
                    ref=hi if line.get('dontpegtop')=='true' else height(b,'ceiling')+PERIOD
                else:
                    lo=height(f,'floor');hi=min(height(b,'floor'),height(f,'ceiling'))
                    ref=height(b,'floor')
                    if line.get('dontpegbottom')=='true':
                        sky=f.get('textureceiling')=='"F_SKY1"' and b.get('textureceiling')=='"F_SKY1"'
                        ref=height(b if sky else f,'ceiling')+PERIOD
                if hi<=lo:continue
                per[material].append(dict(tier=tier,lo=lo,hi=hi,reference_z=ref))
            for material,tiers in per.items():
                out[material].append(dict(line=li,side=si,sector=fs,backsector=bs,start=a,end=z,length=length,tiers=tiers))
    return out,dict(skips)

def turn(a,b):
    u=[a['end'][i]-a['start'][i] for i in [0,1]];v=[b['end'][i]-b['start'][i] for i in [0,1]]
    dot=sum(x*y for x,y in zip(u,v))/a['length']/b['length']
    return math.degrees(math.acos(max(-1,min(1,dot))))

def overlaps(a,b):
    return any(min(x['hi'],y['hi'])-max(x['lo'],y['lo'])>0 for x in a['tiers'] for y in b['tiers'])

def trails(edges):
    """Only unambiguous directed continuations; branch arms get separate groups."""
    starts=collections.defaultdict(list);ends=collections.defaultdict(list)
    for i,e in enumerate(edges):starts[e['start']].append(i);ends[e['end']].append(i)
    nxt={};prev={}
    for i,e in enumerate(edges):
        candidates=[j for j in starts[e['end']] if j!=i and edges[j]['line']!=e['line'] and overlaps(e,edges[j]) and turn(e,edges[j])<150]
        if len(candidates)!=1:continue
        j=candidates[0]
        predecessors=[k for k in ends[edges[j]['start']] if k!=j and edges[k]['line']!=edges[j]['line'] and overlaps(edges[k],edges[j]) and turn(edges[k],edges[j])<150]
        if predecessors==[i]:nxt[i]=j;prev[j]=i
    unseen=set(range(len(edges)));result=[]
    for seed in [i for i in range(len(edges)) if i not in prev]+list(range(len(edges))):
        if seed not in unseen:continue
        chain=[];i=seed
        while i in unseen:
            unseen.remove(i);chain.append(i)
            if i not in nxt:break
            i=nxt[i]
        closed=nxt.get(chain[-1])==chain[0]
        seam=None
        if closed:
            corners=[(turn(edges[chain[k-1]],edges[chain[k]]),k) for k in range(len(chain))]
            angle,k=max(corners)
            seam=dict(reason='closed loop cut at sharpest corner',angle=angle,point=edges[chain[k]]['start'])
            chain=chain[k:]+chain[:k]
        result.append(([edges[i] for i in chain],seam))
    return result

def patch(raw,changes):
    _,blocks=parse(raw)
    for si,fields in sorted(changes.items(),key=lambda item:blocks['sidedef'][int(item[0])].start(),reverse=True):
        m=blocks['sidedef'][int(si)];block=m[0]
        for key,value in fields.items():
            rule=rf'\b{re.escape(key)}\s*=\s*[^;]+;'
            if re.search(rule,block):block=re.sub(rule,f'{key} = {value};',block)
            else:block=block[:-1]+f'\n{key} = {value};\n}}'
        raw=raw[:m.start()]+block+raw[m.end():]
    return raw

def plan(path,actions,shared_scripts):
    magic,lumps=read_wad(path)
    raw=next((d.decode() for n,d in lumps if n.rstrip(b'\0')==b'TEXTMAP'),None)
    if raw is None:return None
    scripts=shared_scripts+'\n'+next((d.decode(errors='replace') for n,d in lumps if n.rstrip(b'\0')==b'SCRIPTS'),'')
    g,_=parse(raw);blocked,motion=excluded_sectors(g,scripts,actions);materials,skips=collect(g,blocked)
    changes={};before={};groups=[];rejected=collections.Counter()
    for material,edges in sorted(materials.items()):
        for chain,seam in trails(edges):
            length=sum(e['length'] for e in chain)
            area=sum(e['length']*sum(t['hi']-t['lo'] for t in e['tiers']) for e in chain)
            tall=max(t['hi']-t['lo'] for e in chain for t in e['tiers'])
            if area<262144 or (length<1024 and tall<512):rejected['small_surface']+=1;continue
            if seam and seam['angle']<45:rejected['smooth_closed_loop']+=1;continue
            anchor=math.ceil(max(t['hi'] for e in chain for t in e['tiers'])/128)*128
            distance=0
            for e in chain:
                s=g['sidedef'][e['side']];fields={};e['u']=distance%PERIOD
                e['context']=context(g,e)
                for t in e['tiers']:
                    tier=t['tier'];fields[SLOTS[tier]]='"'+MATERIALS[material]+'"'
                    fields['offsetx_'+tier]=f'{e["u"]-number(s,"offsetx"):.9f}'
                    fields['offsety_'+tier]=f'{anchor-t["reference_z"]-number(s,"offsety"):.9f}'
                changes.setdefault(e['side'],{}).update(fields)
                before.setdefault(e['side'],{}).update({k:s.get(k) for k in fields})
                distance+=e['length']
            groups.append(dict(material=material,expanded=MATERIALS[material],length=length,area=area,anchor_z=anchor,seam=seam,edges=chain))
    edited=patch(raw,changes)
    # Independent scope proof: only explicitly recorded sidedef fields may differ.
    after,_=parse(edited)
    for kind in ['vertex','linedef','sector','thing']:assert g[kind]==after[kind],kind
    assert len(g['sidedef'])==len(after['sidedef'])
    for si,(old,new) in enumerate(zip(g['sidedef'],after['sidedef'])):
        for k in old.keys()|new.keys():
            if old.get(k)!=new.get(k):assert changes.get(si,{}).get(k)==new.get(k),(si,k)
    output=write_wad(magic,[(n,edited.encode() if n.rstrip(b'\0')==b'TEXTMAP' else d) for n,d in lumps])
    report=dict(map=path.stem.upper(),source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(output).hexdigest(),motion=motion,skipped_tiers=skips,rejected_groups=dict(rejected),changes=changes,before=before,groups=groups)
    return output,report

def replay(path,record):
    """Apply the recorded delta to a newer map only if mapping context still matches."""
    magic,lumps=read_wad(path);raw=next(d.decode() for n,d in lumps if n.rstrip(b'\0')==b'TEXTMAP')
    g,_=parse(raw)
    for c in record['groups']:
        for e in c['edges']:
            assert json.dumps(context(g,e),sort_keys=True)==json.dumps(e['context'],sort_keys=True),(record['map'],e['side'],'mapping context changed')
    for side,fields in record['changes'].items():
        for k,v in fields.items():
            actual=g['sidedef'][int(side)].get(k)
            assert actual in [record['before'][str(side)][k],v],(record['map'],side,k,'concurrent field change')
    edited=patch(raw,record['changes'])
    return write_wad(magic,[(n,edited.encode() if n.rstrip(b'\0')==b'TEXTMAP' else d) for n,d in lumps])

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--actions',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True);(a.output/'maps').mkdir(exist_ok=True)
    actions=json.loads(a.actions.read_text());shared='\n'.join(p.read_text(errors='replace') for p in (a.root/'source').rglob('*.acs'))
    reports=[]
    for path in sorted((a.root/'maps').glob('*.wad')):
        result=plan(path,actions,shared)
        if result is None:continue
        data,r=result;reports.append(r)
        if r['changes']:(a.output/'maps'/path.name).write_bytes(data)
        print(r['map'],len(r['groups']),'groups',sum(len(e['tiers']) for c in r['groups'] for e in c['edges']),'tiers',r['motion'],flush=True)
    (a.output/'manifest.json').write_text(json.dumps(reports,indent=2))

if __name__=='__main__':main()
