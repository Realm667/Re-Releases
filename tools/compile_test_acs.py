"""Compile the regression add-on against the current common ACS library."""
import os, pathlib, subprocess
ROOT=pathlib.Path(__file__).resolve().parent.parent

def compile_tests():
    compiler=pathlib.Path(os.environ.get('UTNT_ACC',r'F:\DoomDev\Tools\UltimateDoombuilder\Compilers\ZDoom\acc.exe'))
    out=ROOT/'tools/runtime-tests/acs/UTNTREG.o';out.parent.mkdir(exist_ok=True)
    r=subprocess.run([str(compiler),'-i',str(compiler.parent),'-i',str(ROOT/'tutnt/source'),str(ROOT/'tools/runtime-tests/portal-regression.acs'),str(out)],capture_output=True)
    if r.returncode:raise RuntimeError((r.stdout+r.stderr).decode(errors='replace'))

if __name__=='__main__':compile_tests()
