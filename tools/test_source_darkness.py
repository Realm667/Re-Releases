"""Verify Source gravity light, saved fades, quality toggles and material seam views."""
from pathlib import Path
import argparse,json
from check_engine import ROOT,run_case

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--map',dest='mapname',choices=['TNT04CN','TNT04C'],default='TNT04CN')
 for n in ('engine','iwad','mod','work'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--renderer',choices=['0','1'],default='1');a=p.parse_args()
 W=a.work.resolve();W.mkdir(parents=True,exist_ok=True)
 cmd=['wait 450','netevent sourceview 8','wait 35','screenshot logs/01-seams.png',
  'netevent sourceview 7','wait 35','screenshot logs/02-shaft.png',
  'netevent sourceview 4','wait 20','netevent sourcedarkcheck 0','netevent sourcekill',
  'wait 45','netevent sourcedarkcheck 1','screenshot logs/03-growing.png',
  'wait 15','netevent sourcedarkcheck 1','screenshot logs/04-darkness.png',
  'save source-darkness','wait 5','load source-darkness','wait 30','netevent sourcedarkcheck 1',
  'UTNT_reducedfx true','wait 10','netevent sourcedarkcheck 1 1','UTNT_fxquality 0','wait 10','netevent sourcedarkcheck 0',
  'UTNT_reducedfx false','UTNT_fxquality 3','wait 10','netevent sourcedarkcheck 1',
  'wait 15','netevent sourcedarkcheck 1','screenshot logs/05-recovery.png',
  'wait 30','netevent sourcedarkcheck 0','screenshot logs/06-collapse.png',
  'wait 70','screenshot logs/07-room.png','wait 20','screenshot logs/08-fade.png',
  'save source-ending','wait 5','load source-ending','wait 40','netevent sourceendcheck 290 310','screenshot logs/09-restored-fade.png',
  'UTNT_reducedfx true','UTNT_fxquality 0','UTNT_shaderoverlayswitch false','netevent sourceview 5',
  'wait 10','screenshot logs/10-away-fade.png','netevent sourceview 4','wait 45','screenshot logs/11-black.png',
  'map TNT04B','wait 100','netevent sourcedarkcheck 0','netevent sourcecheck','screenshot logs/12-next-map.png',
  'echo UTNT_TEST_END','wait 3','quit']
 r=run_case(a.engine,a.iwad,root=W,mod=a.mod,addon=ROOT/'tools/source-tests',mapname=a.mapname,renderer=a.renderer,timeout=200,label='source-darkness',commands='; '.join(cmd),
 settings=[('win_w',1298),('win_h',767),('screenblocks',12),('con_notifytime',0),('r_drawplayersprites','false'),('crosshair',0),('vid_maxfps',60),('i_pauseinbackground','false'),('vid_activeinbackground','true'),('UTNT_fxquality',3),('UTNT_reducedfx','false'),('UTNT_shaderoverlayswitch','true')])
 if r['ok']:
  from PIL import Image
  # Exclude HUD/counters: a rendered black room proves the PP transition is active.
  im=Image.open(W/'logs/11-black.png').convert('RGB');w,h=im.size
  black=im.crop((w//4,h//4,w*3//4,h*3//4))
  if max(v[1] for v in black.getextrema())>2:
   r['ok']=False;r['errors'].append('ending scene did not reach black')
 if r['assertions']<38:r['ok']=False;r['errors'].append('missing darkness assertions')
 (W/'runtime.json').write_text(json.dumps(r,indent=2)+'\n');return 0 if r['ok'] else 1
if __name__=='__main__':raise SystemExit(main())
