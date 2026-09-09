"""Verify unchanged Source combat contracts against a supplied pre-change commit."""
from pathlib import Path
import argparse,subprocess,json,tempfile
from build_utnt import read_wad
ROOT=Path(__file__).resolve().parent.parent
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--baseline-ref',required=True);p.add_argument('--output',type=Path);a=p.parse_args()
 def old(path):return subprocess.check_output(['git','-C',str(ROOT),'show',a.baseline_ref+':'+path])
 def normalize(b):return b.replace(b'\r\n',b'\n')
 checks=[]
 path='tutnt/actors/monsters.txt'
 expected=old(path).replace(b'actor TheSource 24999',b'actor TheSource : UTNTSourceBase 24999').replace(b'ACTOR SourceGuardians 16999',b'ACTOR SourceGuardians : UTNTSourceGuardianBase 16999')
 assert normalize(expected)==normalize((ROOT/path).read_bytes());checks.append('All monster defaults, states, damage and attack scheduling unchanged; two presentation base classes only')
 path='tutnt/source/tutnt.acs';actual=normalize((ROOT/path).read_bytes())
 for i in (1,2,3):actual=actual.replace(f'\n\tScriptCall("UTNTSourceSystem","Attack",{i});'.encode(),b'')
 assert actual==normalize(old(path));checks.append('Global ACS unchanged except three visual attack notifications; all RNG calls and delays preserved')
 path='tutnt/maps/tnt04cn.wad'
 with tempfile.TemporaryDirectory() as tmp:
  before=Path(tmp)/'before.wad';before.write_bytes(old(path))
  baseline={n.rstrip(b'\0'):d for n,d in read_wad(before)[1]}
 current={n.rstrip(b'\0'):d for n,d in read_wad(ROOT/path)[1]}
 assert baseline.keys()==current.keys()
 for name,data in baseline.items():
  if name in (b'SCRIPTS',b'BEHAVIOR'):continue
  assert data==current[name],name;checks.append(name.decode()+' byte-identical')
 script=current[b'SCRIPTS'].replace(b'\r\n\tScriptCall("UTNTSourceSystem","ShieldHit",PlayerNumber());',b'')
 assert script==baseline[b'SCRIPTS'];checks.append('Map ACS unchanged except impact notification; guardian spawning, seven-second wait and boss exit unchanged')
 for path in ['tutnt/sprites/sfx/SOURA0.png','tutnt/maps/tnt04c.wad']+[f'tutnt/patches/RUNE{i}.lmp' for i in range(1,10)]:
  assert (ROOT/path).read_bytes()==old(path),path
 checks.append('Original sigil, all nine rune patches and TNT04C byte-identical')
 result={'ok':True,'baseline':a.baseline_ref,'checks':checks}
 if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
