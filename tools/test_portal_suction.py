from pathlib import Path
import sys,json,argparse,os
R=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser(description="Portal activation, proximity shader, occlusion and save/load checks.")
p.add_argument('--mod',type=Path,default=R/'tutnt.pk3')
p.add_argument('--out',type=Path,default=R/'logs/portal-suction')
p.add_argument('--engine',type=Path,default=os.environ.get('UTNT_ENGINE',R/'engine/uzdoom.exe'))
p.add_argument('--iwad',type=Path,default=os.environ.get('UTNT_IWAD','F:/DoomDev/DOOM2.WAD'))
p.add_argument('--renderer',choices=['0','1','both'],default='both')
p.add_argument('--campaign',action='store_true')
a=p.parse_args(); W=a.out.resolve(); W.mkdir(parents=True,exist_ok=True)
fixture=R/'tools/portal-tests/suction'
sys.path.insert(0,str(R/'tools'))
from check_engine import run_case
cmds=['unbindall','wait 100','netevent suctiontest 0','wait 10','netevent suctiontest 1','wait 70','netevent suctiontest 3']
for distance,enabled in [(240,0),(128,0),(96,1),(64,1),(24,1)]:
 cmds += [f'netevent suctiontest 5 {distance}','wait 15',f'netevent suctiontest 9 {enabled}','wait 10']
cmds+=['netevent suctiontest 5 64','wait 20','save suction-active','wait 15','load suction-active','wait 80','netevent suctiontest 5 64','wait 20','netevent suctiontest 3','netevent suctiontest 9 1','wait 15']
for setting in ['UTNT_reducedfx','UTNT_shaderoverlayswitch','UTNT_fxquality']:
 off='true' if setting=='UTNT_reducedfx' else 'false' if setting=='UTNT_shaderoverlayswitch' else '0'
 on='false' if setting=='UTNT_reducedfx' else 'true' if setting=='UTNT_shaderoverlayswitch' else '3'
 cmds += [setting+' '+off,'wait 30','netevent suctiontest 9 0','wait 10',setting+' '+on,'wait 50','netevent suctiontest 9 1','wait 10']
for mode in [6,7,8]:
 cmds += [f'netevent suctiontest {mode} 64','wait 20','netevent suctiontest 9 0','wait 10']
cmds+=['netevent suctiontest 5 64','wait 20','netevent suctiontest 2','wait 70','netevent suctiontest 4','netevent suctiontest 9 0','wait 15','save suction-off','wait 15','load suction-off','wait 70','netevent suctiontest 4','netevent suctiontest 9 0','wait 15','echo UTNT_TEST_END','quit']
renderers=['0','1'] if a.renderer=='both' else [a.renderer]
results=[]
for renderer in renderers:
 r=run_case(a.engine,a.iwad,root=W,mod=a.mod,addon=fixture,mapname='PORTEST',renderer=renderer,label='suction-'+renderer,timeout=90,commands='; '.join(cmds)+'\n',settings=[('vid_maxfps',60),('i_pauseinbackground',False),('use_mouse',False),('use_joystick',False)])
 s=Path(r['log']).read_text(encoding='utf-8')
 r['ok']=r['ok'] and r['assertions']>=50 and s.count('proximity shader expected')>=16 and 'shader compilation failed' not in s.lower()
 results.append(r)
 r=run_case(a.engine,a.iwad,root=W,mod=a.mod,addon=fixture,mapname='PORBLOCK',renderer=renderer,label='occlusion-'+renderer,timeout=75,commands='wait 100; netevent suctiontest 1; wait 70; netevent suctiontest 5 64; wait 30; netevent suctiontest 9 0; wait 15; echo UTNT_TEST_END; quit\n',settings=[('vid_maxfps',60),('i_pauseinbackground',False),('use_mouse',False),('use_joystick',False)])
 r['ok']=r['ok'] and r['assertions']>=4
 results.append(r)
if a.campaign:
 for name in ['TNT03B','TNT04A','TNT04B']:
  commands='unbindall; god; notarget; wait 100; netevent suctiontest 0; wait 10; netevent suctiontest 11; wait 70; netevent suctiontest 5 240; wait 70; netevent suctiontest 3; wait 10; screenshot logs/'+name+'-particles.png; netevent suctiontest 5 64; wait 40; netevent suctiontest 9 1; wait 10; screenshot logs/'+name+'-suction.png; echo UTNT_TEST_END; quit\n'
  r=run_case(a.engine,a.iwad,root=W,mod=a.mod,addon=fixture,mapname=name,renderer='1',label='campaign-'+name,timeout=45,commands=commands,settings=[('vid_maxfps',60),('i_pauseinbackground',False),('use_mouse',False),('use_joystick',False)])
  r['ok']=r['ok'] and r['assertions']>=5
  results.append(r)
(W/'results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
assert all(r['ok'] for r in results),results
