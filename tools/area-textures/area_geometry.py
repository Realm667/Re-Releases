"""Read native engine plane and finite-midtexture measurements (stdlib only)."""
from pathlib import Path
import re,collections
W=Path('.')
def records(path):
    text=Path(path).read_text(errors='replace')
    for m in re.finditer(r'(SURF(?:SEC|3D|MID)\|.*?)(?=\nSURF|\nUTNT_|\nAREAALIGN|\nSaved|\Z)',text,re.S):
        yield m[1].replace('\n','').replace('\r','').strip().split('|')
def z(p,x,y):return -(p[0]*x+p[1]*y+p[3])/p[2] if abs(p[2])>1e-9 else 0
def load_runtime(name):
    secs={};rovs=collections.defaultdict(list);mids={}
    for p in records(W/'logs'/f'geometry-{name}.log'):
        if p[0]=='SURFSEC':secs[int(p[1])]=dict(floor=p[2],ceiling=p[3],fp=list(map(float,p[4:8])),cp=list(map(float,p[8:12])),light=int(p[12]))
        elif p[0]=='SURF3D':rovs[int(p[1])].append(dict(index=int(p[2]),model=int(p[3]),flags=int(p[4]),alpha=int(p[5]),toptex=p[7],bottomtex=p[6],top=list(map(float,p[8:12])),bottom=list(map(float,p[12:16]))))
        elif p[0]=='SURFMID':mids[int(p[1]),int(p[2])]=(int(p[3]),float(p[4]),float(p[5]))
    return secs,rovs,mids
