"""Verify TNT01's sky edit against a baseline WAD or Git revision.
All geometry, nodes, ACS and gameplay actors must remain byte-for-byte intact.
"""
import argparse,hashlib,json,re,subprocess,tempfile
from pathlib import Path
from build_utnt import read_wad

ROOT=Path(__file__).resolve().parent.parent

def verify(current,baseline):
 before=read_wad(baseline);after=read_wad(current)
 assert before[0]==after[0]
 assert [n for n,d in before[1]]==[n for n,d in after[1]]
 changed=[]
 for (name,old),(_,new) in zip(before[1],after[1]):
  if old==new:continue
  assert name.rstrip(b'\0')==b'TEXTMAP','Non-map lump changed: '+str(name)
  oldtext=old.decode();newtext=new.decode()
  pattern=r'\bthing\s*(?://[^\n]*\n\s*)?\{[^}]*\}'
  oldthings=list(re.finditer(pattern,oldtext));newthings=list(re.finditer(pattern,newtext))
  assert len(oldthings)==len(newthings)==2648
  for index,(a,b) in enumerate(zip(oldthings,newthings)):
   if a[0]==b[0]:continue
   assert index==606
   assert re.search(r'type\s*=\s*9080;',a[0])
   assert re.sub(r'(type\s*=\s*)9001;',r'\g<1>9080;',b[0])==a[0]
   restored=newtext[:b.start()]+a[0]+newtext[b.end():]
   assert restored==oldtext,'Changes beyond the sky actor'
   changed.append(index)
 assert changed==[606]
 return {'ok':True,'changed_actor':606,'change':'SkyViewpoint 9080 to inert MapSpot 9001',
         'geometry_nodes_acs_and_gameplay_preserved':True,
         'sha256':hashlib.sha256(current.read_bytes()).hexdigest()}

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--root',type=Path,default=ROOT)
 g=p.add_mutually_exclusive_group(required=True);g.add_argument('--baseline',type=Path);g.add_argument('--baseline-ref')
 a=p.parse_args()
 with tempfile.TemporaryDirectory(prefix='storm-check-') as tmp:
  baseline=a.baseline
  if a.baseline_ref:
   baseline=Path(tmp)/'before.wad'
   baseline.write_bytes(subprocess.check_output(['git','-c','safe.directory='+str(a.root),'-C',str(a.root),'show',a.baseline_ref+':tutnt/maps/tnt01.wad']))
  print(json.dumps(verify(a.root/'tutnt/maps/tnt01.wad',baseline),indent=2))
