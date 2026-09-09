"""Cursed Peak: real day/dusk/night views, cube directions, hub and persistence."""
from pathlib import Path
import sys,argparse,json
from check_engine import run_case,ROOT

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--work',type=Path,default=ROOT);p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
 p.add_argument('--engine',type=Path,required=True);p.add_argument('--iwad',type=Path,required=True)
 p.add_argument('--renderer',choices=['0','1'],default='1');p.add_argument('--case',choices=['views','hub','freeze'],default='views')
 p.add_argument('--software',action='store_true',help='Inspect the three static software fallback skies')
 a=p.parse_args();label='cursed-'+a.case+'-'+a.renderer+('-software' if a.software else '')
 a.work.mkdir(parents=True,exist_ok=True)
 compile_result=run_case(a.engine,a.iwad,root=a.work,mod=a.mod,addon=ROOT/'tools/cursed-tests',label=label+'-compile',timeout=20)
 if not compile_result['ok']:
  print(Path(compile_result['log']).read_text()[-6000:]);return 1
 cmd=['notarget','wait 100','vid_setsize 1440 810','UTNT_subtitles false','crosshair 0','wait 260']
 if a.case=='views':
  for name,t in [('day',0),('dusk',10800),('night',18000)]:
   cmd += [f'netevent peaktime {t}','wait 10',f'netevent peakcheck {t} {min(18000,t+100)}',f'screenshot logs/{label}-{name}.png']
  cmd+=['netevent peaktime 18000','weatherfx false','netevent peakview 6','wait 10','netevent peakweatheroff',f'screenshot logs/{label}-motion-a.png','wait 175',f'screenshot logs/{label}-motion-b.png']
  for v in range(1,6):cmd += [f'netevent peakview {v}','wait 8',f'screenshot logs/{label}-view{v}.png']
  cmd+=['weatherfx true','netevent peakview 0','netevent peaktime 10800','netevent peakstorm 1','wait 25',f'screenshot logs/{label}-storm.png','changemap TNT03A2','wait 100','netevent peaktime 10800','wait 10',f'screenshot logs/{label}-a2-dusk.png','netevent peakcheck 10800 11000']
 elif a.case=='hub':
  cmd+=['netevent peaktime 10000','wait 10','netevent peakcheck 10000 10100','changemap TNT03A2','wait 90','netevent peakcheck 10050 10300','changemap TNT03A1','wait 90','netevent peakcheck 10100 10500','netevent peaksnapshot','wait 2',f'save {label}','wait 15','netevent peaktime 18000','wait 10',f'load {label}','wait 70','netevent peakrestore','netevent peakcheck 10100 10600',f'screenshot logs/{label}-loaded.png']
 else:
  cmd+=['freeze','wait 5','netevent peaksnapshot','wait 40','netevent peakfreeze','freeze','wait 5']
 cmd+=['wait 35','echo UTNT_TEST_END','wait 5','quit']
 r=run_case(a.engine,a.iwad,root=a.work,mod=a.mod,addon=ROOT/'tools/cursed-tests',mapname='TNT03A1',renderer=a.renderer,label=label,commands='; '.join(cmd),timeout=100,
 settings=[('win_w',1458),('win_h',857),('vid_maxfps',60),('vid_rendermode',0 if a.software else 4),('screenblocks',10),('con_notifytime',0),('gl_texture_filter',0),('UTNT_visoreffects',False),('UTNT_atmosphere',False),('motionblur',False),('vid_activeinbackground',True),('vid_lowerinbackground',False),('i_pauseinbackground',False)])
 expected={'views':44,'hub':45,'freeze':2}[a.case]
 if r['assertions']!=expected:
  r['ok']=False;r['errors'].append(f"expected {expected} assertions, got {r['assertions']}")
 (a.work/'logs'/f'{label}-result.json').write_text(json.dumps(r,indent=2))
 if not r['ok']: print(Path(r['log']).read_text()[-6000:])
 return 0 if r['ok'] else 1
if __name__=='__main__':raise SystemExit(main())
