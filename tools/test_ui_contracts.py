"""Verify the chapter migration preserves every geometry lump and original panorama script."""
import hashlib,json,re
from pathlib import Path
from build_utnt import ROOT,read_wad
contract=json.loads((ROOT/'tools/ui-regression-tests/contracts.json').read_text())
_,entries=read_wad(ROOT/'tutnt/maps/intermap.wad')
geometry={n.rstrip(b'\0').decode():hashlib.sha256(b).hexdigest() for n,b in entries if n.rstrip(b'\0') not in (b'SCRIPTS',b'BEHAVIOR')}
assert geometry==contract['geometry'],'INTERMAP geometry/resource contract changed'
source=next(b for n,b in entries if n.rstrip(b'\0')==b'SCRIPTS').decode().replace('\r','')
panoramas=re.sub(r'\s+','',source[source.lower().index('script 254 (void)'):])
assert hashlib.sha256(panoramas.encode()).hexdigest()==contract['panoramas_sha256'],'Original panorama scripts changed'
assert 'Delay(70);\n    Teleport_Newmap(nextmap,0);' in source
print(f'PASS: {len(geometry)} non-script lumps, original panorama scripts 254/251 and travel timing preserved.')
