"""Run the complete UI regression suite against one explicitly selected source tree or PK3.
Set UTNT_ENGINE / UTNT_IWAD / UTNT_ACC. --quick omits full finale timelines and legacy suites.
"""
import argparse,json,pathlib,subprocess,sys,time
from check_engine import ROOT
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mod',type=pathlib.Path,default=ROOT/'tutnt');p.add_argument('--quick',action='store_true')
a=p.parse_args();mod=str(a.mod.resolve())
cases=[['test_build_snapshot.py'],['test_ui_contracts.py'],
 ['check_engine.py','--mod',mod,'--addon',str(ROOT/'tools/ui-regression-tests'),'--label','ui-suite-compile'],
 ['test_ui_regression.py','--mod',mod,'--mode','hud','--width','640','--height','480','--scale','1.5'],
 ['test_ui_regression.py','--mod',mod,'--mode','hud','--width','1920','--height','1080','--language','enu','--renderer','0'],
 ['test_ui_regression.py','--mod',mod,'--mode','hud','--width','2560','--height','1080','--scale','1.5'],
 ['test_ui_regression.py','--mod',mod,'--mode','chapter','--width','640','--height','480','--scale','1.5'],
 ['test_ui_regression.py','--mod',mod,'--mode','chapter','--episode','10','--width','1920','--height','1080','--language','enu','--renderer','0'],
 ['test_chapter_coop.py','--mod',mod]]
if not a.quick:
 cases += [['test_ui_effects.py','--mod',mod],['test_minor_notices.py','--mod',mod,'--lang','deu'],
 ['test_minor_notices.py','--mod',mod,'--mode','locks','--lang','enu'],
 ['test_objective_controls.py','--mod',mod,'--width','640','--height','480'],
 ['test_chapter_routes.py','--mod',mod]]
from compile_ui_fixture import compile_fixture
compile_fixture();results=[]
for args in cases:
 start=time.monotonic();print('UI suite: '+' '.join(args),flush=True)
 r=subprocess.run([sys.executable,str(ROOT/'tools'/args[0]),*args[1:]],cwd=ROOT)
 results.append(dict(command=args,ok=r.returncode==0,seconds=round(time.monotonic()-start,2)))
 (ROOT/'logs/ui-suite-results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
 if r.returncode:raise SystemExit(r.returncode)
