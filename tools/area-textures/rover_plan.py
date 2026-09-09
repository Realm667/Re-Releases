"""Additional shared-offset constraints for native 3D-floor side rendering."""
import collections,math
from expand_rock_walls import trails

def plan_rovers(g,runtime,rovs,mids,lookup):
    vertices=[(v['x'],v['y']) for v in g['vertex']];masters={};groups=collections.defaultdict(list)
    for li,l in enumerate(g['linedef']):
        si=int(l.get('sidefront',-1))
        if l.get('special')==160 and si>=0:masters[int(g['sidedef'][si]['sector'])]=(li,g['sidedef'][si])
    def z(p,xy):return -(p[0]*xy[0]+p[1]*xy[1]+p[3])/p[2]
    seen=set()
    for li,l in enumerate(g['linedef']):
        for face,key in enumerate(['sidefront','sideback']):
            si=int(l.get(key,-1));bi=int(l.get(['sideback','sidefront'][face],-1))
            if min(si,bi)<0:continue
            s=g['sidedef'][si];sec=int(s['sector']);bs=int(g['sidedef'][bi]['sector'])
            a,b=vertices[int(l['v1'])],vertices[int(l['v2'])]
            if face:a,b=b,a
            length=math.dist(a,b)
            if length<1e-8:continue
            xy=((a[0]+b[0])/2,(a[1]+b[1])/2);own={d['model'] for d in rovs.get(sec,[]) if d['flags']&1}
            for d in rovs.get(bs,[]):
                if not(d['flags']&1 and d['flags']&4) or d['alpha']==0 or d['flags']&(0x1000000|0x40000000) or d['model'] in own:continue
                ml,master=masters.get(d['model'],(-1,{}))
                slot='texturetop' if d['flags']&0x20000 else 'texturebottom' if d['flags']&0x40000 else 'texturemiddle'
                source=s if slot!='texturemiddle' else master;tex=source.get(slot,'-')
                if tex not in lookup or ml<0:continue
                lo=max(z(runtime[sec]['fp'],xy),z(d['bottom'],xy));hi=min(z(runtime[sec]['cp'],xy),z(d['top'],xy))
                if hi<=lo:continue
                key=li,face,tex,ml
                if key in seen:continue
                seen.add(key);m=lookup[tex]
                # A visible ordinary midtexture shares these offsets. Its
                # original phase and its clipping bounds take precedence.
                lock=bool(mids.get((li,face),(0,))[0])
                ox=float(s.get('offsetx',0))+float(s.get('offsetx_mid',0));oy=float(s.get('offsety',0))+float(s.get('offsety_mid',0))
                groups[m['name']].append(dict(line=li,face=face,side=si,start=a,end=b,length=length,tiers=[dict(lo=lo,hi=hi)],master=ml,part={'texturetop':0,'texturemiddle':1,'texturebottom':2}[slot],alias=m['alias'],lock=lock,ox=ox,oy=oy,model=d['model']))
    rows=[];info=[]
    for material,edges in groups.items():
        period=lookup[material]['logical_size'][0]
        for chain,seam in trails(edges):
            d=0;anchor=None;anchor_distance=0
            for e in chain:
                if e['lock'] and anchor is None:anchor=e;anchor_distance=d
                d+=e['length']
            d=0
            for e in chain:
                rows.append(['R',e['line'],e['face'],e['master'],e['part'],e['alias'],d,period,int(e['lock']),e['ox'],e['oy'],e['model'],anchor['master'] if anchor else -1,anchor['model'] if anchor else -1,anchor['ox'] if anchor else 0,anchor['oy'] if anchor else 0,anchor_distance,*e['start'],*e['end']])
                d+=e['length']
            info.append(dict(material=material,lines=[e['line'] for e in chain],locked=any(e['lock'] for e in chain),corner_cut=seam))
    return rows,info
