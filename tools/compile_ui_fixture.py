"""Compile the test-only campaign adapter; never modify shipped ACS or map sources."""
from pathlib import Path
import os,subprocess
from check_engine import ROOT
def compile_fixture():
 addon=ROOT/'tools/ui-regression-tests';(addon/'acs').mkdir(exist_ok=True)
 acc=Path(os.environ.get('UTNT_ACC',r'F:\DoomDev\Tools\UltimateDoombuilder\Compilers\ZDoom\acc.exe'))
 p=subprocess.run([str(acc),'-i',str(acc.parent),str(addon/'chapter-fixture.acs'),str(addon/'acs/UTNTUIT.o')],capture_output=True)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace'))
 return addon
if __name__=='__main__':compile_fixture()
