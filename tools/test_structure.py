"""Structural regression checks: map integrity, localization, deterministic packaging."""
import argparse, hashlib, json, pathlib, re, tempfile, zipfile
from build_utnt import ROOT, read_wad, package
p=argparse.ArgumentParser();p.add_argument('--baseline',type=pathlib.Path,required=True);a=p.parse_args()
root=ROOT/'tutnt';base=a.baseline
report={'maps':[]}
for path in sorted((root/'maps').glob('*.wad')):
 old=read_wad(base/'maps'/path.name)[1];new=read_wad(path)[1]
 assert [n for n,d in old]==[n for n,d in new],path.name
 for (n,x),(_,y) in zip(old,new):
  if n.rstrip(b'\0') not in (b'SCRIPTS',b'BEHAVIOR'):assert x==y,(path.name,n)
 report['maps'].append({'map':path.name,'geometry_and_things_unchanged':True,'lumps':len(new)})
lang=(root/'language/LANGUAGE.enu').read_text(encoding='utf-8')
keys=set(re.findall(r'^\s*(\w+)\s*=',lang,re.M))
sources=[(root/'source/tutnt.acs').read_text()]
sources += [next(d.decode('cp1252') for n,d in read_wad(p)[1] if n.rstrip(b'\0')==b'SCRIPTS') for p in (root/'maps').glob('*.wad')]
used=set(re.findall(r'"(UTNT_[A-Z0-9_]+)"','\n'.join(sources)))
missing=used-keys;assert not missing,missing
report['localized_keys_referenced']=len(used)
# Control-flow effects of all five boss endings remain byte-for-byte source-equivalent,
# apart from localization of one text literal and whitespace.
old=(base/'source/tutnt.acs').read_text();new=sources[0]
x=old[old.index('\tif(boss==1)'):].strip()
y=new[new.index('\tif(boss==1)'):].split('script "UTNTCheckpoint"')[0].strip()
values=dict(re.findall(r'^\s*(UTNT_\w+)\s*=\s*"((?:\\.|[^"\\])*)"\s*;',lang,re.M))
y=re.sub(r'l:"(UTNT_\w+)"',lambda m:'s:"'+values[m[1]]+'"',y)
assert re.sub(r'\s+','',x)==re.sub(r'\s+','',y),'boss completion actions changed'
report['boss_completion_actions_preserved']=5
with tempfile.TemporaryDirectory(prefix='utnt-package-test-') as temp:
 t=pathlib.Path(temp);(t/'tutnt/acs').mkdir(parents=True)
 for path in ['zscript.zc','MAPINFO.txt','acs/tutnt.o','old-asset.txt']:
  (t/'tutnt'/path).write_text('fixture '+path)
 out=t/'test.pk3';first=package(t,out);second=package(t,out)
 assert first['sha256']==second['sha256'],'non-deterministic build'
 (t/'tutnt/old-asset.txt').unlink();package(t,out)
 with zipfile.ZipFile(out) as z:assert 'old-asset.txt' not in z.namelist()
 # A rejected package must leave the previous published archive untouched.
 previous=out.read_bytes()
 import check_engine
 saved=check_engine.run_case
 check_engine.run_case=lambda *args,**kwargs:{'ok':False,'log':'injected rejection'}
 try:
  try:package(t,out,engine='fixture',iwad='fixture')
  except RuntimeError:pass
  else:raise AssertionError('validation rejection ignored')
  assert out.read_bytes()==previous,'failed build replaced previous package'
 finally:check_engine.run_case=saved
report['packaging']={'deterministic':True,'deleted_assets_removed':True,'rejected_package_preserves_previous':True}
(ROOT/'logs/structural-tests.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
