"""Inventory of original map progression contracts and UDMF boundary integrity.
Reports static script/lock references; does not claim reachability from the player start.
"""
import collections,json,pathlib,re,struct
from build_utnt import ROOT,read_wad

def udmf(text):
    out=collections.defaultdict(list)
    # Comments can occur around strings. Preserve quoted tokens during stripping.
    text=re.sub(r'("(?:[^"\\]|\\.)*")|/\*.*?\*/|//[^\n]*',lambda m:m[1] or '',text,flags=re.S)
    for m in re.finditer(r'(\w+)\s*\{([^{}]*)\}',text):
        props={}
        for key,value in re.findall(r'(\w+)\s*=\s*("(?:[^"\\]|\\.)*"|[^;]+);',m[2]):
            value=value.strip()
            if value.startswith('"'):value=value[1:-1]
            elif value in ('true','false'):value=value=='true'
            else:
                try:value=float(value) if '.' in value else int(value)
                except ValueError:pass
            props[key]=value
        out[m[1].lower()].append(props)
    return out

def scripts(source):
    matches=list(re.finditer(r'(?im)^\s*script\s+("[^"]+"|\d+)[^\n]*',source))
    result=[]
    for i,m in enumerate(matches):
        body=source[m.start():matches[i+1].start() if i+1<len(matches) else len(source)]
        calls=re.findall(r'(?i)\b((?:door_\w+|floor_\w+|ceiling_\w+|teleport_newmap|exit_normal|exit_secret|autosave|setlineblocking|setplayerproperty|ACS_NamedExecuteAlways|ACS_Execute)\s*\([^;]*?\))\s*;',body)
        if calls:result.append(dict(script=m[1],line=source.count('\n',0,m.start())+1,actions=[' '.join(c.split()) for c in calls]))
    return result

def audit():
    report=[]
    common=(ROOT/'tutnt/source/tutnt.acs').read_text()
    known_common=set(map(int,re.findall(r'(?im)^script\s+(\d+)',common)))
    for path in sorted((ROOT/'tutnt/maps').glob('*.wad')):
        lumps={n.rstrip(b'\0').decode():d for n,d in read_wad(path)[1]}
        source=lumps['SCRIPTS'].decode(errors='replace')
        item=dict(map=path.stem.upper(),critical_scripts=scripts(source))
        if 'TEXTMAP' in lumps:
            b=udmf(lumps['TEXTMAP'].decode())
            item['counts']={key:len(values) for key,values in b.items()}
            item['player_starts']=[dict(index=i,**t) for i,t in enumerate(b['thing']) if t.get('type') in (1,2,3,4,4001,4002,4003,4004)]
            item['checkpoint_destinations']=[dict(index=i,**t) for i,t in enumerate(b['thing']) if 1100<=t.get('id',0)<=1307]
            item['keys']=[dict(index=i,**t) for i,t in enumerate(b['thing']) if t.get('type') in (5,6,13,38,39,40)]
            item['locks']=[dict(index=i,**l) for i,l in enumerate(b['linedef']) if l.get('special') in (13,83,85)]
            definitions=known_common|set(map(int,re.findall(r'(?im)^\s*script\s+(\d+)',source)))
            missing=[]
            for kind in ('thing','linedef'):
                for i,obj in enumerate(b[kind]):
                    if obj.get('special') in (80,83,84,85,226) and obj.get('arg1',0)==0 and obj.get('arg0',0) not in definitions:
                        missing.append(dict(kind=kind,index=i,script=obj.get('arg0',0),tid=obj.get('id',0)))
            item['unresolved_local_numeric_ACS']=missing
            edges=collections.defaultdict(collections.Counter)
            for l in b['linedef']:
                for side,reverse in (('sidefront',False),('sideback',True)):
                    if side not in l or l[side]<0:continue
                    sector=b['sidedef'][l[side]]['sector'];a,c=l['v1'],l['v2']
                    if reverse:a,c=c,a
                    edges[sector][a]+=1;edges[sector][c]-=1
            item['unbalanced_sector_vertices']=[dict(sector=sec,vertices={v:n for v,n in vs.items() if n}) for sec,vs in edges.items() if any(vs.values())]
        else:item['format']='Hexen'
        report.append(item)
    (ROOT/'logs').mkdir(exist_ok=True)
    out=ROOT/'logs/campaign-contracts.json';out.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps([dict(map=i['map'],scripts=len(i['critical_scripts']),unresolved=i.get('unresolved_local_numeric_ACS',[]),open_boundaries=len(i.get('unbalanced_sector_vertices',[]))) for i in report],indent=2))
    return report
if __name__=='__main__':audit()
