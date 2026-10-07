"""Native distance-density, ownership and live-menu regression in isolated configs."""
import argparse,json,zipfile
from pathlib import Path
from check_engine import ROOT,run_case
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--engine',default='F:/DoomDev/uzdoom.exe');p.add_argument('--iwad',default='F:/DoomDev/DOOM2.WAD')
p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3');p.add_argument('--renderer',default='0',choices=['0','1']);a=p.parse_args()
addon=ROOT/'tutnt/.codex/builds/distance-fx-fixture.pk3'
addon.parent.mkdir(parents=True,exist_ok=True)
(ROOT/'tutnt/.codex/validation').mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(addon,'w') as z:
 for f in (ROOT/'tools/fixtures/distance-fx').iterdir():z.write(f,f.name)
 z.write(ROOT/'tools/fixtures/voxels/maps/VXLAB.wad','maps/VXLAB.wad')
commands=['wait 70','UTNT_lod 4096','wait 3','netevent distancecheck 0','wait 3',
 'UTNT_fxfull 256','UTNT_fxhalf 512','UTNT_fxminimal 1024','wait 3','netevent distancecheck 1',
 'UTNT_fxfull 1536','UTNT_fxhalf 3072','UTNT_fxminimal 4096','wait 3','netevent distancecheck 2',
 'UTNT_fxhalf 256','UTNT_fxminimal 128','wait 3','netevent distancecheck 3',
 'UTNT_fxgraduated false','wait 3','netevent distancecheck 4','event distancereset','wait 3','netevent distancecheck 5',
 'save distance-fx','wait 3','load distance-fx','wait 70','netevent distancecheck 5','wait 3','echo UTNT_TEST_END','quit']
r=run_case(a.engine,a.iwad,mod=a.mod,addon=addon,mapname='VXLAB',renderer=a.renderer,label='distance-fx',timeout=75,commands='; '.join(commands),settings=[('i_pauseinbackground','false'),('vid_activeinbackground','true')])
r['ok'] &= r['assertions']==43
results=[r]
if r['ok']:
 for lang in ['en','de','es','fr']:
  shot=ROOT/'tutnt/.codex/validation'/('distance-menu-'+lang+'.png')
  result=run_case(a.engine,a.iwad,mod=a.mod,addon=addon,mapname='VXLAB',renderer=a.renderer,label='distance-menu-'+lang,timeout=40,commands=f'wait 70; event distancemenu; wait 10; screenshot {shot.as_posix()}; echo UTNT_TEST_END; quit',settings=[('language',lang),('con_notifytime',0),('i_pauseinbackground','false'),('vid_activeinbackground','true')])
  results.append(result)
(ROOT/'tutnt/.codex/validation/distance-fx.json').write_text(json.dumps(results,indent=2))
for r in results:
 if not r['ok']:print(Path(r['log']).read_text()[-8000:])
raise SystemExit(0 if all(r['ok'] for r in results) else 1)
