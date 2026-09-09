"""Verify Cursed Peak patch boundaries against explicit pre-change WADs."""
import argparse,re,json,hashlib
from pathlib import Path
from build_utnt import read_wad
ROOT=Path(__file__).resolve().parent.parent
def check(before,after):
 old=dict(read_wad(before)[1]);new=dict(read_wad(after)[1]);assert old.keys()==new.keys()
 changes=[n.rstrip(b'\0').decode() for n in old if old[n]!=new[n]]
 assert set(changes)=={'TEXTMAP','SCRIPTS','BEHAVIOR'},changes
 tm=next(n for n in old if n.rstrip(b'\0')==b'TEXTMAP')
 a=old[tm].decode();b=new[tm].decode();count=0
 def replace(m):
  nonlocal count
  if re.search(r'type\s*=\s*9080\s*;',m[0]):
   assert not re.search(r'id\s*=\s*[1-9]',m[0]);count+=1
   return re.sub(r'(type\s*=\s*)9080(?=\s*;)',r'\g<1>9001',m[0])
  return m[0]
 expected=re.sub(r'thing\s*(?://[^\n]*)?\s*\{[^}]*\}',replace,a)
 assert count==1 and expected==b,'geometry or other things changed'
 scripts=next(n for n in old if n.rstrip(b'\0')==b'SCRIPTS')
 a=old[scripts].decode('cp1252');b=new[scripts].decode('cp1252')
 head='//Global Variables';tail='//Objective 1'
 assert a[:a.index(head,a.index('//DAY TO NIGHT TRANSITION//'))]==b[:b.index(head,b.index('//DAY TO NIGHT TRANSITION//'))]
 assert a[a.index(tail):]==b[b.index(tail):],'unrelated scripts changed'
 assert 'UTNT_CursedSkyResume" RETURN' in b and 'global int 12 : g_cursedskytime' in b
 return {'map':after.name,'changed_lumps':changes,'geometry_and_nodes_preserved':True,'other_scripts_preserved':True,'camera_types_changed':count,'sha256':hashlib.sha256(after.read_bytes()).hexdigest()}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--before',type=Path,required=True);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--output',type=Path)
 a=p.parse_args();result=[check(a.before/f'tutnt/maps/{name}.wad',a.root/f'tutnt/maps/{name}.wad') for name in ['tnt03a1','tnt03a2']]
 text=json.dumps(result,indent=2);print(text)
 if a.output:a.output.write_text(text)
