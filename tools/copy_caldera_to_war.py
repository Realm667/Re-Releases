"""Copy the current TNT03B caldera verbatim into TNT04A, preserving gameplay.
Run once against a TNT04A without the caldera. Requires ZDBSP.
"""
import re,json,subprocess,argparse,hashlib
from pathlib import Path
from build_utnt import read_wad,write_wad
from test_caldera_structure import parse
BASE={'vertex':5286,'linedef':6373,'sidedef':11421,'sector':1426}
PAT=r'\b(vertex|linedef|sidedef|sector|thing)\s*(?://[^\n]*\n\s*)?\{([^}]*)\}'
def block(k,d):return k+'\n{\n'+''.join(f'{a} = {b};\n' for a,b in d.items())+'}\n'
def transfer(source,target,output,zdbsp):
 sl,sg=parse(source);tl,tg=parse(target);magic,lumps=read_wad(target)
 assert all(float(v['x'])<10000 for v in tg['vertex']),'Caldera already present or map expanded'
 counts={k:len(tg[k]) for k in BASE};delta={k:counts[k]-BASE[k] for k in BASE}
 copied={k:[dict(v) for v in sg[k][BASE[k]:]] for k in BASE}
 assert {k:len(v) for k,v in copied.items()}==dict(vertex=3456,linedef=9984,sidedef=19776,sector=6529)
 for l in copied['linedef']:
  for key,kind in [('v1','vertex'),('v2','vertex'),('sidefront','sidedef'),('sideback','sidedef')]:
   if key in l:
    assert int(l[key])>=BASE[kind];l[key]=str(int(l[key])+delta[kind])
 for s in copied['sidedef']:
  assert int(s['sector'])>=BASE['sector'];s['sector']=str(int(s['sector'])+delta['sector'])
 text=tl['TEXTMAP'].decode();seen=0
 def replace(m):
  nonlocal seen
  if m[1]!='thing':return m[0]
  idx=seen;seen+=1
  if idx!=5:return m[0]
  d=dict(tg['thing'][idx]);assert d['type']=='9080' and 'id' not in d
  d.update({k:sg['thing'][5][k] for k in ['x','y','height']});return block('thing',d)
 text=re.sub(PAT,replace,text)+'\n// Exact current TNT03B caldera; only local indices remapped.\n'
 text+=''.join(block(k,v) for k in BASE for v in copied[k])
 raw=output.with_suffix('.raw.wad');raw.write_bytes(write_wad(magic,[(n,text.encode() if n.rstrip(b'\0')==b'TEXTMAP' else d) for n,d in lumps if n.rstrip(b'\0') not in [b'ZNODES',b'BLOCKMAP',b'REJECT']]))
 r=subprocess.run([str(zdbsp),'-q','-X','-g','-r','-o',str(output),str(raw)],capture_output=True,timeout=120);assert r.returncode==0,r.stderr
 ol,og=parse(output)
 for k in BASE:assert og[k][:counts[k]]==tg[k]
 for k in BASE:assert og[k][counts[k]:]==copied[k]
 for i,t in enumerate(tg['thing']):
  assert (i==5 or t==og['thing'][i])
 assert len(tg['thing'])==len(og['thing'])
 for k,v in tl.items():
  if k not in ['TEXTMAP','ZNODES','BLOCKMAP','REJECT']:assert v==ol[k],k
 raw.unlink()
 return dict(ok=True,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),baseline_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),original_counts=counts,copied_counts={k:len(v) for k,v in copied.items()},checks=['all original gameplay geometry unchanged','all gameplay things unchanged','SCRIPTS and BEHAVIOR byte-identical','terrain identical to current TNT03B after index remapping','only default sky viewpoint moved'])
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for k in ['source','target','output','zdbsp']:p.add_argument('--'+k,type=Path,required=True)
 print(json.dumps(transfer(**vars(p.parse_args())),indent=2))
