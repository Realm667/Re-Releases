"""Native-engine voxel gallery, actor-default and save/load regression.

All screenshots and command files stay in tutnt/.codex; fixtures never ship.
"""
from pathlib import Path
import argparse,json,zipfile
from check_engine import ROOT,run_case

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--engine',type=Path,default=Path('F:/DoomDev/uzdoom.exe'));p.add_argument('--iwad',type=Path,default=Path('F:/DoomDev/DOOM2.WAD'))
 p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3');p.add_argument('--groups',type=int,nargs='+',default=None)
 p.add_argument('--overlay',action='store_true');p.add_argument('--label',default='gallery');p.add_argument('--renderer',default='1')
 p.add_argument('--work',type=Path,default=ROOT/'tutnt/.codex/work/voxel-integration');a=p.parse_args();w=a.work.resolve();w.mkdir(parents=True,exist_ok=True)
 actor_count=len(json.loads((ROOT/'tools/artwork/voxels/manifest.json').read_text())['actors'])
 if a.groups is None:a.groups=list(range((actor_count+3)//4))
 if any(g<0 or g*4>=actor_count for g in a.groups):p.error('Group outside actor gallery')
 # check_engine writes root/logs. Require the pre-created central log junction.
 if not (w/'logs').exists() or not (w/'logs').resolve().is_relative_to((ROOT/'tutnt/.codex/logs').resolve()):raise ValueError('Create work/logs junction into .codex/logs before running')
 addon=ROOT/'tools/fixtures/voxels'
 if a.overlay:
  addon=ROOT/'tutnt/.codex/builds/voxel-integration-review.pk3'
  with zipfile.ZipFile(addon,'w',zipfile.ZIP_DEFLATED) as z:
   for f in (ROOT/'tools/fixtures/voxels').rglob('*'):
    if f.is_file():z.write(f,f.relative_to(ROOT/'tools/fixtures/voxels').as_posix())
   for f in (ROOT/'tutnt/voxels').iterdir():z.write(f,'voxels/'+f.name)
   z.write(ROOT/'tutnt/VOXELDEF.txt','VOXELDEF.txt')
 results=[]
 # Console exec lines are bounded. Keep each wait chain below 4 KiB; splitting
 # a long chain across physical lines would schedule overlapping command queues.
 for batch_start in range(0,len(a.groups),4):
  groups=a.groups[batch_start:batch_start+4]
  commands=['unbindall','god','notarget','con_notifytime 0','vid_setsize 1600 900','screenblocks 12','crosshair 0','r_drawplayersprites false','fov 80','wait 160']
  for group in groups:
   commands += [f'netevent vxshow {group}','wait 25','netevent vxcheck','wait 3']
   for angle in (0,45,180):
    commands += [f'netevent vxangle {angle}','wait 8',f'screenshot "{(w/f"{a.label}-{group:02}-{angle:03}.png").as_posix()}"','wait 3']
  commands += ['save voxel-gallery','wait 6','load voxel-gallery','wait 70','netevent vxcheck','wait 8']
  if 10 in groups:
   commands += ['netevent vxshow 10','wait 3','netevent vxexplode']
   for frame,delay in zip('ABCDE',(2,5,5,7,10)):
    commands += [f'wait {delay}',f'screenshot "{(w/f"{a.label}-barrel-death-{frame}.png").as_posix()}"']
   commands += ['wait 10','netevent vxblastcheck','wait 3']
  commands += ['echo UTNT_TEST_END','wait 4','quit']
  chain='; '.join(commands);assert len(chain)<3900
  label='voxels-'+a.label+'-'+str(batch_start//4)
  r=run_case(a.engine,a.iwad,mod=a.mod,root=w,addon=addon,mapname='VXLAB',renderer=a.renderer,label=label,timeout=80,
   settings=[('UTNT_distanceblur',0),('UTNT_fxquality',2),('UTNT_reducedfx','false'),('gl_texture_filter',0)],commands=chain)
  out=Path(r['log']).read_text(encoding='utf-8')
  r['ok']=r['ok'] and r['assertions']>=sum(2*min(4,actor_count-g*4)+1 for g in groups)+1+(2 if 10 in groups else 0) and not any(x in out for x in ('not a valid voxel','Unknown voxel option','Voxel "'))
  results.append(r)
  (ROOT/'tutnt/.codex/validation'/f'voxels-{a.label}.json').write_text(json.dumps(results,indent=2))
  if not r['ok']:print(out[-9000:]);raise SystemExit(1)
if __name__=='__main__':main()
