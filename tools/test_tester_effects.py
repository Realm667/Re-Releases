"""Exercise projectile readability, real poison damage, native fire size and burn resurrection."""
from pathlib import Path
import argparse,json,shutil
from check_engine import run_case,ROOT

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--engine',type=Path,required=True);p.add_argument('--iwad',type=Path,required=True)
 p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
 p.add_argument('--work',type=Path,default=ROOT/'tutnt/.codex/validation/tester-effects')
 a=p.parse_args();a.work.mkdir(parents=True,exist_ok=True)
 fixture=a.work/'fixture';fixture.mkdir(exist_ok=True);(fixture/'maps').mkdir(exist_ok=True)
 for name in ['ZSCRIPT','MAPINFO']:shutil.copy2(ROOT/'tools/fixtures/tester-effects'/name,fixture/name)
 shutil.copy2(ROOT/'tools/fixtures/voxels/maps/VXLAB.wad',fixture/'maps/VXLAB.wad')
 results=[run_case(a.engine,a.iwad,root=a.work,mod=a.mod,addon=fixture,label='effects-compile')]
 if results[0]['ok']:
  results.append(run_case(a.engine,a.iwad,root=a.work,mod=a.mod,addon=fixture,mapname='VXLAB',label='effects-runtime',timeout=45,settings=[('vid_activeinbackground',True),('i_pauseinbackground',False),('use_mouse',False),('vid_maxfps',60)],commands='notarget; wait 25; netevent effectcheck; wait 240; echo UTNT_TEST_END; quit'))
  results[-1]['ok'] &= results[-1]['assertions']>=122
 (a.work/'results.json').write_text(json.dumps(results,indent=2)+'\n')
 return 0 if all(x['ok'] for x in results) and len(results)==2 else 1
if __name__=='__main__':raise SystemExit(main())
