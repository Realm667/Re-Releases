"""Exercise the real defeat clock, saved reconstruction and uncut level ending."""
from pathlib import Path
import argparse,json
from check_engine import ROOT,run_case

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--engine',type=Path,required=True);p.add_argument('--iwad',type=Path,required=True)
 p.add_argument('--mod',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
 p.add_argument('--renderer',choices=['0','1'],default='1');a=p.parse_args()
 W=a.work.resolve();W.mkdir(parents=True,exist_ok=True)
 results=[]
 common=dict(engine=a.engine,iwad=a.iwad,mod=a.mod,addon=ROOT/'tools/source-tests',mapname='TNT04CN',renderer=a.renderer,timeout=200,
  settings=[('win_w',1298),('win_h',767),('screenblocks',12),('con_notifytime',0),('r_drawplayersprites','false'),('crosshair',0),('vid_maxfps',60),('i_pauseinbackground','false'),('vid_activeinbackground','true')])
 # Network events can be delivered several tics after a restored frame.
 cmd=['wait 450','netevent sourceview 4','wait 15','screenshot logs/ceiling.png','netevent sourcekill',
  'wait 20','netevent sourcedeathcheck 18 23','screenshot logs/hold.png',
  'wait 55','netevent sourcedeathcheck 72 78','screenshot logs/fracture.png',
  'save source-finale','wait 10','load source-finale','wait 20','netevent sourcedeathcheck 90 105','screenshot logs/restored-fracture.png',
  'wait 17','netevent sourcedeathcheck 107 120','screenshot logs/lightning.png',
  'wait 49','netevent sourcedeathcheck 156 166','screenshot logs/sever.png',
  'UTNT_reducedfx true','UTNT_fxquality 0','wait 54','netevent sourcedeathcheck 210 220','screenshot logs/reduced-afterglow.png',
  'wait 45','netevent sourcedeathcheck 255 265','screenshot logs/empty.png',
  'save source-empty','wait 5','load source-empty','wait 20','netevent sourcedeathcheck 270 290','wait 5',
  'map TNT04C','wait 100','netevent sourcecheck','echo UTNT_TEST_END','wait 3','quit']
 out=W/'restore';out.mkdir(exist_ok=True)
 results.append(run_case(root=out,label='finale-restore',commands='; '.join(cmd),**common))
 # Start the actual encounter/BOSSHP ACS; do not bypass the ending with a map command.
 cmd=['wait 450','netevent sourceview 4','netevent sourcebegin','wait 20','netevent sourcekill',
  'wait 111','netevent sourcedeathcheck 108 114','screenshot logs/real-lightning.png',
  'wait 149','netevent sourcedeathcheck 257 263','screenshot logs/real-empty.png',
  'wait 43','netevent sourcedeathcheck 300 306','wait 22','netevent sourceendcheck 322 328','screenshot logs/real-ending.png','wait 138','netevent sourceexitcheck','echo UTNT_TEST_END','wait 3','quit']
 out=W/'ending';out.mkdir(exist_ok=True)
 results.append(run_case(root=out,label='finale-ending',commands='; '.join(cmd),**common))
 (W/'runtime.json').write_text(json.dumps(results,indent=2)+'\n')
 print(json.dumps(results,indent=2))
 return 0 if all(r['ok'] and r['assertions']>0 for r in results) else 1
if __name__=='__main__':raise SystemExit(main())
