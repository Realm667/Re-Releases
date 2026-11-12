"""Compile the test-only campaign adapter; never modify shipped ACS or map sources."""
from pathlib import Path
import os,subprocess,shutil
from work_paths import codex_root
from check_engine import ROOT
def compile_fixture():
 source=ROOT/'tools/ui-regression-tests'
 addon=codex_root(ROOT)/'cache/ui-regression-fixture'
 shutil.copytree(source,addon,dirs_exist_ok=True,ignore=shutil.ignore_patterns('acs','__pycache__'))
 (addon/'acs').mkdir(exist_ok=True)
 acc=Path(os.environ.get('UTNT_ACC',codex_root(ROOT)/'dependencies/UltimateDoombuilder/Compilers/ZDoom/acc.exe'))
 p=subprocess.run([str(acc),'-i',str(acc.parent),str(addon/'chapter-fixture.acs'),str(addon/'acs/UTNTUIT.o')],cwd=addon,capture_output=True)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace'))
 return addon
if __name__=='__main__':compile_fixture()
