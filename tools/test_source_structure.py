"""Verify unchanged Source combat contracts against a supplied pre-change commit."""
from pathlib import Path
import argparse,subprocess,json,tempfile,re
from build_utnt import read_wad
ROOT=Path(__file__).resolve().parent.parent
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--baseline-ref',required=True);p.add_argument('--output',type=Path);p.add_argument('--baseline-maps',type=Path,help='Optional pre-edit map snapshots named tnt04c-before.wad and tnt04cn-before.wad');a=p.parse_args()
 def old(path):return subprocess.check_output(['git','-c',f'safe.directory={ROOT.as_posix()}','-C',str(ROOT),'show',a.baseline_ref+':'+path])
 def normalize(b):return b.replace(b'\r\n',b'\n')
 checks=[]
 path='tutnt/actors/monsters.txt'
 expected=old(path).replace(b'actor TheSource 24999',b'actor TheSource : UTNTSourceBase 24999').replace(b'ACTOR SourceGuardians 16999',b'ACTOR SourceGuardians : UTNTSourceGuardianBase 16999')
 expected=normalize(expected).replace(b'Death:\n\t\tSOUR A 0 A_Scream\n\t\tSOUR A 3 A_FadeOut\n\t\tWait',b'Death:\n\t\tTNT1 A 1 A_SourceDefeat\n\t\tWait')
 assert expected==normalize((ROOT/path).read_bytes());checks.append('Monster defaults, living states, damage and attack scheduling unchanged; only Source death now uses its saved finale clock')
 path='tutnt/source/tutnt.acs';actual=normalize((ROOT/path).read_bytes())
 expected=normalize(old(path))
 for i in (1,2,3):
  cue=f'\n\tScriptCall("UTNTSourceSystem","Attack",{i});'.encode();actual=actual.replace(cue,b'');expected=expected.replace(cue,b'')
 def without_finale(data):
  return re.sub(rb'\n        // TNT04CN(?:/TNT04C)?:.*?            terminate;\n        }\n',b'',data,flags=re.S)
 assert without_finale(actual)==without_finale(expected);checks.append('Global ACS preserves living attacks and other boss endings')
 for mapname in ('tnt04cn','tnt04c'):
  path=f'tutnt/maps/{mapname}.wad'
  with tempfile.TemporaryDirectory() as tmp:
   before=Path(tmp)/'before.wad'
   before.write_bytes((a.baseline_maps/f'{mapname}-before.wad').read_bytes() if a.baseline_maps else old(path))
   baseline={n.rstrip(b'\0'):d for n,d in read_wad(before)[1]}
  current={n.rstrip(b'\0'):d for n,d in read_wad(ROOT/path)[1]}
  assert baseline.keys()==current.keys()
  for name,data in baseline.items():
   if name in (b'SCRIPTS',b'BEHAVIOR'):continue
   assert data==current[name],(mapname,name);checks.append(mapname+': '+name.decode()+' byte-identical')
  def without_hit(data):
   return normalize(data).replace(b'\n\tScriptCall("UTNTSourceSystem","ShieldHit",PlayerNumber());',b'')
  assert without_hit(current[b'SCRIPTS'])==without_hit(baseline[b'SCRIPTS'])
  checks.append(mapname+': guardian spawning, specials and seven-second damage window preserved')
 for path in ['tutnt/sprites/sfx/SOURA0.png']+[f'tutnt/patches/RUNE{i}.lmp' for i in range(1,10)]:
  assert (ROOT/path).read_bytes()==old(path),path
 checks.append('Original sigil and all nine rune patches byte-identical')
 result={'ok':True,'baseline':a.baseline_ref,'map_snapshots':str(a.baseline_maps) if a.baseline_maps else None,'checks':checks}
 if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
