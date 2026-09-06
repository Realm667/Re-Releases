"""Run every campaign map on both hardware renderers and all three player classes in the regression arena."""
import json, os, pathlib
from check_engine import ROOT, run_case
from compile_test_acs import compile_tests
compile_tests()
engine=pathlib.Path(os.environ.get('UTNT_ENGINE',ROOT/'engine/uzdoom.exe'))
iwad=pathlib.Path(os.environ.get('UTNT_IWAD',r'F:\DoomDev\DOOM2.WAD'))
results=[]
for renderer in ('0','1'):
    for path in sorted((ROOT/'tutnt/maps').glob('*.wad')):
        name=path.stem.upper()
        result=run_case(engine,iwad,mapname=name,renderer=renderer,label=f'map-{name}-{renderer}',duration=140,
            settings=[('UTNT_atmosphere','true')] if name in ('TNT03A1','TNT03A2','TNTLE') else [])
        results.append(result)
        (ROOT/'logs/runtime-matrix.json').write_text(json.dumps(results,indent=2))
    for player in ('Marine','Scout','Commando'):
        result=run_case(engine,iwad,mapname='UTNTTEST',addon=ROOT/'tools/runtime-tests',renderer=renderer,
            playerclass=player,label=f'arena-{player}-{renderer}',regression=True)
        results.append(result)
        (ROOT/'logs/runtime-matrix.json').write_text(json.dumps(results,indent=2))
raise SystemExit(0 if all(r['ok'] for r in results) else 1)
