"""Verify original TNTLE gameplay blocks and secret sky survived the sky change."""
from pathlib import Path
import argparse,re,json,hashlib,subprocess,tempfile
from build_utnt import read_wad
P=r'\b(thing|vertex|linedef|sidedef|sector)\s*(?://[^\n]*\n\s*)?\{([^}]*)\}'
def parse(data):
 d={}
 for m in re.finditer(P,data.decode()):d.setdefault(m[1],[]).append(m[2])
 return d
def lumps(path):return {n.rstrip(b'\0'):d for n,d in read_wad(path)[1]}
def fields(t):return dict(re.findall(r'(\w+)\s*=\s*([^;]+);',t))
def verify(before,after,acc=None):
 a,b=lumps(before),lumps(after);ga,gb=parse(a[b'TEXTMAP']),parse(b[b'TEXTMAP'])
 checks={}
 for k,extra in [('vertex',8),('linedef',8),('sidedef',8),('sector',2)]:
  assert len(gb[k])==len(ga[k])+extra,(k,len(gb[k]),len(ga[k]))
  assert ga[k]==gb[k][:len(ga[k])],k+' original blocks changed'
  checks[k+'_original_blocks']=len(ga[k])
 assert len(ga['thing'])==len(gb['thing']);changed=[]
 for i,(x,y) in enumerate(zip(ga['thing'],gb['thing'])):
  if x==y:continue
  fa,fb=fields(x),fields(y);assert fa.get('type')=='9080'
  tid=int(fa.get('id',0));assert tid in (0,13)
  assert {k:v for k,v in fa.items() if k not in ('x','y','height')}=={k:v for k,v in fb.items() if k not in ('x','y','height')}
  assert [float(fb[k]) for k in ('x','y','height')]==[-24576 if tid==0 else -20480,24576,512]
  changed.append(tid)
 assert sorted(changed)==[0,13];checks['only_two_cameras_moved']=True
 pat=rb'script\s+14\s+OPEN\s*(?://[^\r\n]*\s*)?\{[^}]*\}'
 assert re.sub(pat,b'RETIRED',a[b'SCRIPTS'])==re.sub(pat,b'RETIRED',b[b'SCRIPTS'])
 checks['only_script14_changed']=True
 for k in a.keys()&b.keys():
  if k not in (b'TEXTMAP',b'SCRIPTS',b'BEHAVIOR',b'ZNODES',b'BLOCKMAP',b'REJECT'):
   assert a[k]==b[k],k
 if acc:
  with tempfile.TemporaryDirectory() as t:
   t=Path(t);src=t/'map.acs';obj=t/'map.o';src.write_bytes(b[b'SCRIPTS'])
   p=subprocess.run([str(acc),'-i',str(acc.parent),str(src),str(obj)],capture_output=True);assert p.returncode==0
   assert obj.read_bytes()==b[b'BEHAVIOR'];checks['acs_recompiled_identically']=True
 checks['map_sha256']=hashlib.sha256(after.read_bytes()).hexdigest()
 print(json.dumps(checks,indent=2));return checks
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('--acc',type=Path);a=p.parse_args();verify(a.before,a.after,a.acc)
