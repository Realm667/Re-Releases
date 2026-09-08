"""TNT04A caldera/comet views, both renderers, real intro and save/load.
Requires configured UTNT_ENGINE / UTNT_IWAD. Test cameras are not packaged.
"""
import argparse,os,json
from pathlib import Path
from check_engine import run_case,ROOT

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--engine',type=Path,default=os.environ.get('UTNT_ENGINE'))
 p.add_argument('--iwad',type=Path,default=os.environ.get('UTNT_IWAD'))
 p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
 p.add_argument('--work',type=Path,default=ROOT)
 p.add_argument('--resume',help='Existing post-intro save in work/logs/saves; useful for renderer comparison')
 p.add_argument('--renderer',choices=['0','1','both'],default='both')
 a=p.parse_args()
 if not a.engine or not a.iwad:p.error('Configure engine and IWAD')
 results=[]
 for backend in ['0','1'] if a.renderer=='both' else [a.renderer]:
  label='war-sky-'+backend
  cmd=['notarget','wait 70']
  cmd += ['load '+a.resume,'wait 350','netevent calderacheck','wait 70'] if a.resume else ['wait 2300']
  for view in [7,8,12,13,14,11]:cmd += [f'netevent calderaview {view}','wait 70',f'screenshot logs/{label}-view{view}.png']
  cmd += ['netevent calderaview 12','wait 70',f'screenshot logs/{label}-motion-a.png','wait 175',f'screenshot logs/{label}-motion-b.png',f'save {label}','wait 70',f'load {label}','wait 140','netevent calderacheck','wait 70','echo UTNT_TEST_END','wait 5','quit']
  r=run_case(a.engine,a.iwad,root=a.work,mod=a.mod,addon=ROOT/'tools/war-sky-tests',mapname='TNT04A',renderer=backend,label=label,timeout=200,commands='; '.join(cmd),settings=[('win_w',1938),('win_h',1127),('screenblocks',12),('vid_maxfps',60),('gl_texture_filter',0),('con_notifytime',0)])
  log=Path(r['log']).read_text(encoding='utf-8')
  if 'Dieser Spielstand ben' in log or 'requires these files' in log:
   r['ok']=False;r['errors'].append('save resources do not match current mod')
  if r['assertions']<6:r['ok']=False;r['errors'].append('expected at least six map/sky/save assertions')
  results.append(r)
 (a.work/'logs/war-sky-results.json').write_text(json.dumps(results,indent=2))
 return 0 if all(r['ok'] for r in results) else 1
if __name__=='__main__':raise SystemExit(main())
