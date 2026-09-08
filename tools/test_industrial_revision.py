"""Run the native revised particle/rocket checks. Python 3.11+."""
from pathlib import Path
import argparse,os,json
from check_engine import run_case
root=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--engine',type=Path,default=os.environ.get('UTNT_ENGINE',root/'engine/uzdoom.exe'))
parser.add_argument('--iwad',type=Path,default=os.environ.get('UTNT_IWAD','F:/DoomDev/DOOM2.WAD'))
parser.add_argument('--mod',type=Path,default=root/'tutnt')
parser.add_argument('--renderer',choices=['0','1'],default='1')
a=parser.parse_args();addon=root/'tools/industrial-revision-tests'
compile=run_case(a.engine,a.iwad,root=root,mod=a.mod,addon=addon,label='industrial-revision-compile')
if not compile['ok']:raise SystemExit(1)
result=run_case(a.engine,a.iwad,root=root,mod=a.mod,addon=addon,mapname='UTNTIFX',renderer=a.renderer,label='industrial-revision-'+a.renderer,commands=(addon/'checks.cfg').read_text(),timeout=120)
raise SystemExit(not result['ok'])
