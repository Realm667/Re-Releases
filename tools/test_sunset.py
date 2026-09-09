"""Actual sky-mask, cardinal sunset, freeze and occluded glare captures."""
from pathlib import Path
import argparse,sys,json
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'tools'))
from check_engine import run_case

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--work',type=Path,required=True);p.add_argument('--engine',type=Path,required=True);p.add_argument('--iwad',type=Path,required=True)
 p.add_argument('--renderer',default='0');p.add_argument('--mod',type=Path,default=ROOT/'tutnt')
 a=p.parse_args();a.work.mkdir(parents=True,exist_ok=True)
 addon=a.work/'addon';addon.mkdir(exist_ok=True)
 extension=Path(__file__).with_name('sunset-tests.zc')
 if not extension.exists():extension=ROOT/'tools/sunset-tests/sunset-tests.zc'
 (addon/'ZSCRIPT').write_text((ROOT/'tools/cursed-tests/ZSCRIPT').read_text()+'\n'+extension.read_text())
 (addon/'MAPINFO').write_text('gameinfo { AddEventHandlers="UTNTCursedSunTests" }')
 label='sunset-'+a.renderer
 compilation=run_case(a.engine,a.iwad,root=a.work,mod=a.mod,addon=addon,label=label+'-compile')
 if not compilation['ok']:
  print(Path(compilation['log']).read_text()[-5000:]);raise RuntimeError('Test compilation failed')
 cmd=['notarget','wait 300','vid_setsize 1440 810','screenblocks 12','con_notifytime 0','UTNT_subtitles false','crosshair 0','UTNT_visoreffects false','UTNT_atmosphere false','weatherfx false','pukename UTNT_CursedSkySetTime 10800','netevent sunview 270 0','wait 20']
 def shot(name):cmd.extend(['wait 35','netevent sunstate',f'screenshot logs/{label}-{name}.png'])
 cmd+=['UTNT_shaderoverlayswitch false'];shot('south-bare')
 cmd+=['UTNT_shaderoverlayswitch true','netevent sunexpect 1'];shot('south-flare')
 for angle,name in [(0,'east'),(90,'north'),(180,'west')]:
  cmd += [f'netevent sunview {angle} 0','wait 10','netevent sunexpect 0'];shot(name)
 cmd+=['netevent sunview 270 1','wait 10','netevent sunexpect 0'];shot('roof')
 cmd+=['netevent sunview 270 0','wait 10','netevent sunblock 1','wait 10','netevent sunexpect 0'];shot('actor')
 cmd+=['netevent sunblock 0','UTNT_reducedfx true','wait 10','netevent sunexpect 0'];shot('reduced')
 cmd+=['UTNT_reducedfx false','pukename UTNT_CursedSkySetTime 0','wait 10','netevent sunexpect 0'];shot('day')
 cmd+=['pukename UTNT_CursedSkySetTime 18000','wait 10','netevent sunexpect 0'];shot('night')
 # Fixed night removes all cloud/fade drift when toggling the sky-only snow.
 cmd+=['UTNT_shaderoverlayswitch false','freeze','netevent sunmask 0'];shot('snow-off')
 cmd+=['netevent sunmask 1'];shot('snow-on');shot('snow-frozen')
 cmd+=['freeze','wait 35'];shot('snow-moved')
 cmd+=['netevent sunmask 0','pukename UTNT_CursedSkySetTime 14400','wait 10','freeze'];shot('afterglow-off')
 cmd+=['UTNT_shaderoverlayswitch true'];shot('afterglow-on')
 cmd+=['freeze','pukename UTNT_CursedSkySetTime 10800','wait 10','freeze','netevent sunstorm 1'];shot('storm')
 cmd+=['freeze','changemap TNT03A2','wait 100','pukename UTNT_CursedSkySetTime 10800','netevent sunview 270 0','wait 20','netevent sunexpect 1'];shot('a2-sun')
 cmd+=['netevent peakcheck 10800 11000','echo UTNT_TEST_END','wait 5','quit']
 r=run_case(a.engine,a.iwad,root=a.work,mod=a.mod,addon=addon,mapname='TNT03A1',renderer=a.renderer,label=label,commands='; '.join(cmd),timeout=140,
  settings=[('vid_activeinbackground',True),('vid_lowerinbackground',False),('i_pauseinbackground',False),('vid_maxfps',60),('UTNT_fxquality',2)])
 (a.work/f'{label}-result.json').write_text(json.dumps(r,indent=2))
 if not r['ok']:print(Path(r['log']).read_text()[-7000:])
 assert r['ok'] and r['assertions']>=20
if __name__=='__main__':main()
