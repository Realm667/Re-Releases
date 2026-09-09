"""ENDMAP sky binding, preserved finale viewpoint and save/load, both renderers."""
from pathlib import Path
import argparse,json,sys
REPO=Path(__file__).resolve().parent.parent
if not (REPO/'tutnt').exists(): REPO=Path('F:/DoomDev/Projects/realm667.git')
sys.path.insert(0,str(REPO/'tools'))
from check_engine import run_case
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--mod',type=Path,default=REPO/'tutnt.pk3')
p.add_argument('--out',type=Path,required=True)
p.add_argument('--engine',type=Path,required=True)
p.add_argument('--iwad',type=Path,required=True)
p.add_argument('--fixture',type=Path,default=REPO/'tools/endmap-sky-tests')
a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
results=[]
for backend in ['0','1']:
 label='endmap-sky-'+backend
 r=run_case(a.engine,a.iwad,root=a.out,mod=a.mod,addon=a.fixture,mapname='ENDMAP01',renderer=backend,label=label,timeout=60,settings=[('con_notifytime',0),('vid_maxfps',60),('win_w',1298),('win_h',767),('i_pauseinbackground',False),('use_mouse',False)],commands=f'wait 350; screenshot logs/{label}.png; save endmapsky; wait 10; load endmapsky; wait 35; netevent endmapskycheck; wait 5; echo UTNT_TEST_END; quit\n')
 if r['assertions']!=10:r['ok']=False;r['errors'].append('expected ten assertions')
 if not r['ok']:print(Path(r['log']).read_text()[-4000:])
 results.append(r)
(a.out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
assert all(r['ok'] for r in results),results
