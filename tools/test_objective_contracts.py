"""Verify objective integration preserves map geometry and exit destinations.
Pass the immutable pre-completion revision with --base.
"""
from pathlib import Path
import argparse,subprocess,struct,json
from build_utnt import read_wad
from audit_campaign import udmf
R=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',required=True);a=p.parse_args()
def lumps(data):
    _,count,offset=struct.unpack_from('<4sII',data)
    out={}
    for i in range(count):
        pos,size,name=struct.unpack_from('<II8s',data,offset+i*16)
        out[name.rstrip(b'\0').decode()]=data[pos:pos+size]
    return out
results=[]
allowed={'tnt03a1':{10819,16456,17843,17845},'tnt03b':{5170},'tnt04a':{2861}}
for f in sorted((R/'tutnt/maps').glob('*.wad')):
    n=f.relative_to(R).as_posix()
    old=lumps(subprocess.check_output(['git','-c',f'safe.directory={R.as_posix()}','-C',str(R),'show',f'{a.base}:{n}']))
    new=lumps(f.read_bytes());assert old.keys()==new.keys(),n
    changed=[k for k in old if old[k]!=new[k]]
    assert set(changed)<={'SCRIPTS','BEHAVIOR','TEXTMAP'},(n,changed)
    exits=[]
    if 'TEXTMAP' in changed:
        before,after=udmf(old['TEXTMAP'].decode()),udmf(new['TEXTMAP'].decode())
        assert before.keys()==after.keys()
        for kind in before:
            assert len(before[kind])==len(after[kind]),(n,kind)
            for i,(x,y) in enumerate(zip(before[kind],after[kind])):
                if x==y:continue
                assert kind=='linedef' and i in allowed.get(f.stem,set()),(n,kind,i)
                expected=dict(x)
                for arg in range(5):expected.pop(f'arg{arg}',None)
                expected.update(special=80,arg0=250,arg1=0,arg2=x.get('arg0',0),arg3=x.get('arg1',0),arg4=x.get('arg2',0))
                assert y==expected and x['special']==74,(n,i)
                exits.append(i)
        assert set(exits)==allowed[f.stem]
    results.append({'map':f.stem,'changed_lumps':changed,'wrapped_exits':exits,'geometry_preserved':True})
out={'base':a.base,'maps':results,'ok':True}
(R/'logs/objectives-completion-contracts.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print('All map geometry, node lumps and authored exit arguments preserved; only six explicit exit adapters added.')
