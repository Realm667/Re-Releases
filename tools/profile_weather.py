from pathlib import Path
import sys,os,re,json,statistics
ROOT=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(ROOT/'tools'))
from check_engine import run_case
addon=ROOT/'tools/weather-profile';addon.mkdir(exist_ok=True)
(addon/'ZSCRIPT').write_text('''version "5.0.0"
class UTNTWeatherFrames : StaticEventHandler
{
 ui Array<double> Frames;
 ui double Previous;
 ui bool Finished;
 override void RenderOverlay(RenderEvent e)
 {
  double now=MSTimeF();
  if(level.time>=140 && level.time<315 && Previous>0) Frames.Push(now-Previous);
  Previous=now;
  if(level.time>=315 && !Finished)
  {
   Finished=true; String samples="";
   for(int i=0;i<Frames.Size();i++) samples=samples..String.Format(i ? ",%.4f" : "%.4f",Frames[i]);
   Console.Printf("UTNT_WEATHER_FRAMES %s",samples);
  }
 }
}
''')
(addon/'MAPINFO').write_text('gameinfo { AddEventHandlers="UTNTWeatherFrames", "UTNTWeatherTests" }\n')
# Reuse only the camera fixture; no duplicate includes or private test map.
(addon/'fixture.zc').write_bytes((ROOT/'tools/weather-tests/ZSCRIPT').read_bytes().replace(b'version "5.0.0"',b''))
with (addon/'ZSCRIPT').open('a') as f:f.write('\n#include "fixture.zc"\n')
results=[]
for name in ['TNT02','TNT03A1']:
 for enabled in [False,True]:
  label=f'weather-profile-{name}-{int(enabled)}'
  r=run_case(os.environ['UTNT_ENGINE'],os.environ['UTNT_IWAD'],mapname=name,addon=addon,label=label,duration=335,timeout=30,
   settings=[('weatherfx',enabled),('UTNT_fxquality',3),('vid_maxfps',0),('vid_vsync',False),('i_pauseinbackground',False),('vid_activeinbackground',True)])
  text=Path(r['log']).read_text();match=re.search(r'UTNT_WEATHER_FRAMES ([\d.,]+)',text)
  values=sorted(map(float,match[1].split(','))) if match else []
  r.update(map=name,weather=enabled,samples=len(values))
  r['ok'] &= len(values)>100
  if values:r['frame_ms']={'median':round(statistics.median(values),3),'p95':round(values[int(len(values)*.95)],3)}
  results.append(r); print(json.dumps(r),flush=True)
(ROOT/'logs/weather-profile-results.json').write_text(json.dumps(results,indent=2)+'\n')
raise SystemExit(0 if all(r['ok'] for r in results) else 1)
