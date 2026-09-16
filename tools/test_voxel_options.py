"""Check live voxel switching, explicit KVX fallback, save/load and menu rendering."""
from pathlib import Path
import argparse,json,zipfile,re
from check_engine import ROOT,run_case


def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--engine',default='F:/DoomDev/uzdoom.exe')
 p.add_argument('--iwad',default='F:/DoomDev/DOOM2.WAD')
 p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
 p.add_argument('--overlay',action='store_true')
 p.add_argument('--renderer',default='1',choices=['0','1'])
 a=p.parse_args()
 expected=set(re.findall(r'^([A-Z0-9]{4})[A-Z] =',(ROOT/'tutnt/VOXELDEF.txt').read_text(),re.M))
 actual=set(re.findall(r"'([A-Z0-9]{4})'",(ROOT/'tutnt/zscript/UTNT_VoxelOptions.zc').read_text()))
 assert expected==actual,(expected-actual,actual-expected)
 w=ROOT/'tutnt/.codex/work/voxel-option';w.mkdir(parents=True,exist_ok=True)
 addon=ROOT/'tutnt/.codex/builds/voxel-option-runtime.pk3'
 with zipfile.ZipFile(addon,'w') as z:
  for f in (ROOT/'tools/fixtures/voxel-options').iterdir():z.write(f,f.name)
  z.write(ROOT/'tools/fixtures/voxels/maps/VXLAB.wad','maps/VXLAB.wad')
  if a.overlay:
   z.writestr('ZSCRIPT.option','version "5.0.0"\n#include "zscript/UTNT_VoxelOptions.zc"')
   z.write(ROOT/'tutnt/zscript/UTNT_VoxelOptions.zc','zscript/UTNT_VoxelOptions.zc')
   z.writestr('CVARINFO','user bool UTNT_voxels = true;')
   z.writestr('MAPINFO.option','gameinfo { AddEventHandlers = "UTNTVoxelOptions" }\nmap TITLEMAP lookup "UTNT_TITLEMAP_NAME" { }')
   for rel in ['LANGUAGE.txt','MENUDEF.txt']:z.write(ROOT/'tutnt'/rel,rel)
 cmd=['vid_setsize 1280 720','wait 100','netevent voptioncheck 1',f'screenshot "{(w/"on.png").as_posix()}"',
      'UTNT_voxels false','wait 5','netevent voptioncheck 0',f'screenshot "{(w/"off.png").as_posix()}"',
      'netevent voptionspawn','wait 5','netevent voptionnew','save voxel-option','wait 5',
      'UTNT_voxels true','wait 5','netevent voptioncheck 1','wait 3','load voxel-option','wait 70','netevent voptioncheck 1',
      'UTNT_voxels false','wait 5','netevent voptioncheck 0','netevent voptionexplode','wait 3','netevent voptionframe',
      'event voptionmenu','wait 10',f'screenshot "{(w/"menu.png").as_posix()}"','echo UTNT_TEST_END','quit']
 result=run_case(a.engine,a.iwad,mod=a.mod,addon=addon,mapname='VXLAB',renderer=a.renderer,label='voxel-option-runtime',timeout=65,
  commands='; '.join(cmd),settings=[('vid_activeinbackground','true'),('i_pauseinbackground','false'),('use_mouse','false'),('use_joystick','false'),('language','en'),('con_notifytime',0),('UTNT_tonalfilter','false'),('UTNT_distanceblur','false')])
 result['ok'] &= result['assertions']==53
 (ROOT/'tutnt/.codex/validation/voxel-option.json').write_text(json.dumps(result,indent=2))
 if not result['ok']:print(Path(result['log']).read_text()[-6000:])
 return 0 if result['ok'] else 1

if __name__=='__main__':raise SystemExit(main())
