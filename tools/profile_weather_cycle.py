"""Compare disabled, light and peak weather in a short fixed camera window."""
from pathlib import Path
import os,sys,json,re,statistics,argparse,shutil
from check_engine import ROOT,run_case
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--mod',type=Path);p.add_argument('--map',choices=['TNT02','TNT03A1']);p.add_argument('--phase',choices=['off','light','storm']);a=p.parse_args()
addon=a.root/'logs/weather-cycle-profile-addon';addon.mkdir(parents=True,exist_ok=True)
fixture=ROOT/'tools/weather-tests/ZSCRIPT'
(addon/'fixture.zc').write_text(fixture.read_text(encoding='utf-8').replace('version "5.0.0"',''),encoding='utf-8')
(addon/'ZSCRIPT').write_text('''version "5.0.0"
#include "fixture.zc"
class UTNTCycleProfileClock : EventHandler
{
 override void WorldTick()
 {
  if(level.time==20 && level.MapName~=="TNT02")
  {
   let p=players[0].mo; let ti=ThinkerIterator.Create('BigTree'); Actor tree; int n=0;
   while(tree=Actor(ti.Next())) if(n++==3)
   {
    Vector3 pos=tree.Pos+(0,256,12); pos.Z=level.PointInSector(pos.XY).floorplane.ZatPoint(pos.XY)+12;
    p.SetOrigin(pos,false); p.Vel=(0,0,0); p.bNoGravity=true; p.Angle=270; p.Pitch=9; break;
   }
  }
 }
 override void NetworkProcess(ConsoleEvent e)
 {
  if(e.Name=="profilephase")
  {
   let h=UTNTWeatherHandler(EventHandler.Find('UTNTWeatherHandler'));
   h.WeatherTics=e.Args[0]*35;
  }
 }
}
class UTNTCycleFrames : StaticEventHandler
{
 ui Array<double> Frames;
 ui double Previous;
 ui bool Done;
 override void RenderOverlay(RenderEvent e)
 {
  double now=MSTimeF();
  if(level.time>=210 && level.time<350 && Previous>0) Frames.Push(now-Previous);
  Previous=now;
  if(level.time>=350 && !Done)
  {
   Done=true; String samples="";
   for(int i=0;i<Frames.Size();i++) samples=samples..String.Format(i ? ",%.4f" : "%.4f",Frames[i]);
   Console.Printf("WEATHER_CYCLE_FRAMES %s",samples);
  }
 }
}
''',encoding='utf-8')
(addon/'MAPINFO').write_text('gameinfo { AddEventHandlers="UTNTWeatherTests", "UTNTCycleProfileClock", "UTNTCycleFrames" }\n')
records=[]
for mapname in ['TNT02','TNT03A1']:
 if a.map and a.map!=mapname:continue
 for phase,enabled,seconds in [('off',False,190),('light',True,0),('storm',True,190)]:
  if a.phase and a.phase!=phase:continue
  label=f'weather-cycle-profile-{mapname}-{phase}'
  camera=''
  cmd=f'wait 30; {camera} netevent profilephase {seconds}; wait 340; echo UTNT_TEST_END; wait 5; quit\n'
  r=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],root=a.root,mod=a.mod,mapname=mapname,addon=addon,label=label,commands=cmd,timeout=40,settings=[('weatherfx',enabled),('UTNT_fxquality',3),('UTNT_lod',2048),('vid_vsync',False),('vid_maxfps',0),('cl_capfps',False),('i_pauseinbackground',False),('vid_activeinbackground',True),('vid_lowerinbackground',False)])
  log=Path(r['log']).read_text(encoding='utf-8');m=re.search(r'WEATHER_CYCLE_FRAMES ([\d.,]+)',log)
  values=sorted(map(float,m[1].split(','))) if m else []
  r.update(map=mapname,phase=phase,samples=len(values));r['ok'] &= len(values)>80
  if values:r['frame_ms']={'median':round(statistics.median(values),3),'p95':round(values[int(len(values)*.95)],3)}
  records.append(r);print(json.dumps(r),flush=True)
(a.root/'logs'/('weather-cycle-profile-'+a.map+'-'+a.phase+'-results.json' if a.map and a.phase else 'weather-cycle-profile-results.json')).write_text(json.dumps(records,indent=2))
raise SystemExit(0 if all(r['ok'] for r in records) else 1)
