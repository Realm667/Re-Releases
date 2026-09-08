from pathlib import Path
import sys,json,re,shutil,math,argparse,os
from check_engine import run_case,ROOT
p=argparse.ArgumentParser(description="Render normal comets, a deterministic rare breakup and live motion in UZDoom.")
p.add_argument('--engine',type=Path,default=os.environ.get('UTNT_ENGINE'))
p.add_argument('--iwad',type=Path,default=os.environ.get('UTNT_IWAD'))
p.add_argument('--mod',type=Path,default=ROOT/'tutnt')
p.add_argument('--work',type=Path,required=True)
p.add_argument('--case',action='append',choices=['normal-gl','normal-vk','split-early','split-late','split-gl','live-vk'])
a=p.parse_args()
if not a.engine or not a.iwad:p.error('Configure engine and IWAD')
R=ROOT;W=a.work.resolve();W.mkdir(parents=True,exist_ok=True);E=a.engine;I=a.iwad
events=[]
for i in range(7):
 for cycle in range(32):
  if (cycle*13+i*7+(cycle//32)*11+19)%32==0:
   events.append(((cycle+.60)*(32+i*2.7)-i*7.31,i,cycle))
event=min(e for e in events if e[0]>0);t,track,cycle=event
print('First rare event at phase .60:',event,flush=True)
results=[]
for label,renderer,clock in [('normal-gl','0',70),('normal-vk','1',70),('split-early','1',(cycle+.35)*(32+track*2.7)-track*7.31),('split-late','1',t),('split-gl','0',t),('live-vk','1',None)]:
 if a.case and label not in a.case:continue
 fixture=W/label;fixture.mkdir(exist_ok=True)
 shutil.copy2(R/'tools/war-sky-tests/MAPINFO',fixture/'MAPINFO')
 script=(R/'tools/war-sky-tests/ZSCRIPT').read_text()
 if label.startswith('split'):
  # Follow this particular flight, retaining the same composition at both stages.
  phase=(clock+track*7.31)/(32+track*2.7)-cycle
  lon=track*.8976+.28-phase*.43;lat=1.02-phase*1.28
  # Shader longitude corresponds directly to the world yaw.
  angle=math.degrees(lon)
  script=script.replace('p.SetOrigin(pos,false);',f'pos=(18000,18000,0);angle={angle};pitch={-math.degrees(lat)};p.SetOrigin(pos,false);')
 (fixture/'ZSCRIPT').write_text(script)
 if clock is not None:
  for f in 'NESWUD':
   dst=fixture/f'shaders/caldera-war/sky-{f}.fp';dst.parent.mkdir(parents=True,exist_ok=True)
   dst.write_text(re.sub(r'\btimer\b',f'({clock:.8f})',(R/f'tutnt/shaders/caldera-war/sky-{f}.fp').read_text()))
 commands=['wait 35','+use','wait 5','-use','screenblocks 12','wait 200','netevent calderaview 12','wait 70',f'screenshot "{(W/(label+".png")).as_posix()}"']
 if clock is None:commands+=['wait 175',f'screenshot "{(W/"live-motion.png").as_posix()}"']
 commands+=['netevent calderacheck','echo UTNT_TEST_END','wait 5','quit']
 results.append(run_case(E,I,root=W,mod=a.mod,addon=fixture,mapname='TNT04A',renderer=renderer,label=label,timeout=45,commands='; '.join(commands),settings=[('i_pauseinbackground','false'),('vid_activeinbackground','true'),('vid_maxfps',60),('con_notifytime',0),('crosshair',0),('r_drawplayersprites','false')]))
 (W/'render-results.json').write_text(json.dumps(results,indent=2))
 if not results[-1]['ok']:print(Path(results[-1]['log']).read_text(encoding='utf-8')[-5000:])
 assert results[-1]['ok']
(W/'render-results.json').write_text(json.dumps(results,indent=2))
