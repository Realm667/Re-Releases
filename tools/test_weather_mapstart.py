"""Check the normal and alternate cooperative starts in TNT03A1."""
import argparse,json,re,struct,zipfile
from pathlib import Path
R=Path(__file__).resolve().parent.parent
def check(data):
    _,count,offset=struct.unpack_from('<4sII',data)
    lumps=[struct.unpack_from('<II8s',data,offset+i*16) for i in range(count)]
    text=next(data[p:p+n].decode('utf-8') for p,n,name in lumps if name.rstrip(b'\0')==b'TEXTMAP')
    starts=[]
    for m in re.finditer(r'\bthing\s*(?://[^\n]*\n\s*)?\{[^}]*\}',text):
        f=dict(re.findall(r'(\w+)\s*=\s*([^;]+);',m[0]))
        if f.get('type') in ['1','2','3','4']:starts.append(f)
    normal=[s for s in starts if s['type']=='1' and s.get('arg0','0')=='0']
    alternate=[s for s in starts if s['type']=='1' and s.get('arg0','0')=='1']
    assert len(normal)==1 and (normal[0]['x'],normal[0]['y'])==('-1440.0','2112.0'),normal
    assert len(alternate)==1 and (alternate[0]['x'],alternate[0]['y'])==('3360.0','-4992.0'),alternate
    assert all(len([s for s in starts if s['type']==str(t)])==2 for t in [2,3,4]),starts
    return {'ok':True,'normal_player1':normal[0],'alternate_player1':alternate[0],'starts_total':len(starts)}
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--mod',type=Path);a=parser.parse_args()
    if a.mod:
        with zipfile.ZipFile(a.mod) as z:data=z.read('maps/tnt03a1.wad')
    else:data=(R/'tutnt/maps/tnt03a1.wad').read_bytes()
    print(json.dumps(check(data)))
