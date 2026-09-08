"""Caldera visual tour on both hardware renderers, including save/load.
Set UTNT_ENGINE / UTNT_IWAD or pass --engine / --iwad.
"""
import argparse,json,os
from pathlib import Path
from check_engine import run_case,ROOT
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--engine',type=Path,default=os.environ.get('UTNT_ENGINE'));p.add_argument('--iwad',type=Path,default=os.environ.get('UTNT_IWAD'))
 p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3');p.add_argument('--work',type=Path,default=ROOT)
 p.add_argument('--renderer',choices=['0','1','both'],default='both');p.add_argument('--width',type=int,default=1920)
 a=p.parse_args();results=[]
 if not a.engine or not a.iwad:p.error('Configure the engine and IWAD paths')
 for backend in ['0','1'] if a.renderer=='both' else [a.renderer]:
  label='sky-caldera-'+backend
  commands=['notarget','wait 350']
  for view in range(12):
   commands += [f'netevent calderaview {view}','wait 8',f'screenshot logs/{label}-view{view}.png']
  commands += ['netevent calderaview 0','wait 8',f'save {label}','wait 8',f'load {label}','wait 15','netevent calderacheck','wait 8',f'screenshot logs/{label}-loaded.png','echo UTNT_TEST_END','wait 5','quit']
  r=run_case(a.engine,a.iwad,root=a.work,mod=a.mod,addon=ROOT/'tools/caldera-tests',mapname='TNT03B',renderer=backend,label=label,timeout=60,commands='; '.join(commands)+'\n',settings=[('win_w',a.width+18),('win_h',a.width*9//16+47),('screenblocks',10),('vid_maxfps',60),('gl_texture_filter',0),('con_notifytime',0)])
  if r['assertions']<6:r['ok']=False;r['errors'].append('missing caldera assertions')
  results.append(r)
  if not r['ok']:print(Path(r['log']).read_text()[-5000:])
 (a.work/'logs/caldera-results.json').write_text(json.dumps(results,indent=2))
 return 0 if all(r['ok'] for r in results) else 1
if __name__=='__main__':raise SystemExit(main())
