"""Native-engine traversal and progression regression for TNT01GPT.
Uses the shipped player collision with non-solid frozen monsters for repeatability.
The separate combat roster assertions retain the real actors and skill filtering.
"""
from pathlib import Path
import sys,zipfile,subprocess,json,argparse,time
ROOT=Path(__file__).resolve().parent.parent
WORK=ROOT/'tutnt/.codex/work/tnt01gpt'
LOG=ROOT/'tutnt/.codex/logs/tnt01gpt'
# x,y,z teleports delimit checks; subsequent waypoints must be reached by walking.
ROUTES=[
 ([(464,304,-64),(560,550),(864,864),(1216,864),(1600,1248),(1760,1648),(1450,1648),(1248,1648),(704,1856),(704,2240),(736,2336),(272,2368),(272,2816),(320,3008),(944,3008),(944,3376)],1),
 ([(944,3376,128),(944,2880),(944,2752),(1280,2752),(1280,2112),(1720,2112),(2320,1824),(2688,1904),(3008,1904),(3008,1984)],9),
 ([(3008,1984,0),(3008,2912),(3344,2912),(3344,2832),(3360,2640),(4656,2640),(4672,2928),(4632,3072),(4632,3312)],2),
 ([(3536,3520,0),(3536,3504),(3360,3504),(3360,3616),(3360,3984),(3360,4112),(3008,4208),(2112,4208),(1424,4208),(1168,4208),(928,4288)],3),
 ([(928,4288,144),(928,4512),(928,3904),(928,3520),(944,2880),(1280,2752),(1280,2112),(1720,2112),(2112,2256)],5),
 ([(4032,2688,0),(4032,2112),(4032,1920),(3552,1808),(3360,1456),(2752,1456)],10),
 ([(2112,2256,0),(2112,2400),(2112,4000),(2112,4208),(2112,4464),(2112,4736)],6),
 ([(2112,4784,0),(2256,4832),(2256,5040),(2256,5504),(2256,5632),(2256,5808),(2240,5968)],16),
 ([(2240,5968,64),(2240,6176)],7)]
def fixture():
 WORK.mkdir(parents=True,exist_ok=True);LOG.mkdir(parents=True,exist_ok=True)
 f=WORK/'test-fixture';f.mkdir(exist_ok=True)
 nodes=[]
 for ri,(pts,act) in enumerate(ROUTES):
  for j,pt in enumerate(pts):nodes.append((*pt[:2],pt[2] if len(pt)>2 else -999,j==0,0,ri))
  x,y=pts[-1][:2];nodes.append((x,y,-999,False,act,ri))
 code='''version "5.0.0"
class GPTProbe:EventHandler {
 int node,stuck,pause; bool started,done; double lastx,lasty;
 void Check(bool ok,String s){Console.Printf("UTNT_ASSERT %s: %s",ok?"PASS":"FAIL",s);}
 int Progress(int k){return ACS_ExecuteWithResult(90,k);}
 void Use(int script){ for(int i=0;i<level.lines.Size();i++) {let l=level.lines[i];if(l.special==80 && l.args[0]==script){l.Activate(players[0].mo,0,SPAC_USE);return;}} Check(false,"missing authored switch");}
 override void WorldUnloaded(WorldEvent e){if(node>80){Console.Printf("GPT_ROUTE_COMPLETE: native exit reached");}}
 override void WorldLoaded(WorldEvent e){node=0;pause=90;}
 override void WorldTick(){
  if(done || !players[0].mo)return;let p=players[0].mo;p.bInvulnerable=true;p.bNoTarget=true;
  if(pause>0){pause--;return;}
  if(!started){started=true; int count=0;let it=ThinkerIterator.Create("Actor");Actor a;
   while(a=Actor(it.Next())){if(a.bCountKill){count++;a.bDormant=true;a.bSolid=false;}}
   int bad=0;it=ThinkerIterator.Create("Actor");while(a=Actor(it.Next()))if(a.bCountKill && !a.CheckPosition(a.Pos.XY)){bad++;Console.Printf("GPT_BADSPAWN %s %.0f %.0f",a.GetClassName(),a.Pos.X,a.Pos.Y);}
   Check(bad==0,"all monsters clear of blocking geometry");
   Check(count==120,"UV roster contains 120 monsters");Check(level.total_secrets==3,"three secrets");
   Use(9);Use(5);Check(Progress(0)==0 && Progress(1)==0 && Progress(2)==0,"locked start state");
  }
  double x,y,z;bool warp;int actcode,route;
  switch(node){
'''
 for i,(x,y,z,warp,actcode,route) in enumerate(nodes):code+=f'case {i}:x={x};y={y};z={z};warp={str(warp).lower()};actcode={actcode};route={route};break;\n'
 code+='''default:done=true;Console.Printf("GPT_ROUTE_COMPLETE");return;}
  if(warp){if(route==8)Check(Progress(4)==1,"guardian defeat unlocks exit");p.SetOrigin((x,y,z),false);p.Vel=(0,0,0);node++;pause=4;return;}
  if(actcode){
   Console.Printf("GPT_STAGE %d at %.0f %.0f %.0f",route,p.Pos.X,p.Pos.Y,p.Pos.Z);
   if(actcode==1)Check(Progress(0)==1,"blue skull pickup runs its script");
   if(actcode==9)Use(9);
   if(actcode==2){Check(p.FindInventory("UTNTRocketLauncher")!=null,"rocket launcher reached");Use(2);}
   if(actcode==3)Check(Progress(1)==1 && Progress(2)==1,"reactor and red skull reached in sequence");
   if(actcode==5)Use(5);
   if(actcode==6)Check(Progress(3)==1,"walking into arena activates encounter");
   if(actcode==16){let it=ThinkerIterator.Create("Actor");Actor a;while(a=Actor(it.Next()))if(a.tid==3005 || a.tid==3006)a.DamageMobj(p,p,100000,"None",DMG_FORCED);}
   if(actcode==7){Check(Progress(4)==1,"all guardians defeated; exit unlocked");Console.Printf("GPT_ROUTE_COMPLETE");done=true;}
   node++;pause=120;return;
  }
  double dx=x-p.Pos.X,dy=y-p.Pos.Y,dist=sqrt(dx*dx+dy*dy);
  if(dist<14){Console.Printf("GPT_WALK %d %.0f %.0f %.0f",node,p.Pos.X,p.Pos.Y,p.Pos.Z);node++;stuck=0;p.Vel=(0,0,0);return;}
  p.Angle=atan2(dy,dx);p.Vel=(dx/dist*12,dy/dist*12,p.Vel.Z);
  if(abs(p.Pos.X-lastx)+abs(p.Pos.Y-lasty)<1)stuck++;else stuck=0;
  lastx=p.Pos.X;lasty=p.Pos.Y;
  if(stuck>30){Check(false,String.Format("walk blocked node %d toward %.0f %.0f at %.1f %.1f %.1f",node,x,y,p.Pos.X,p.Pos.Y,p.Pos.Z));done=true;}
 }
}
'''
 (f/'ZSCRIPT').write_text(code)
 (f/'MAPINFO').write_text((ROOT/'tutnt/mapinfo/MAPINFO.tnt01gpt').read_text()+'\nGameInfo {AddEventHandlers="GPTProbe"}\n')
 (f/'maps').mkdir(exist_ok=True);(f/'maps/tnt01gpt.wad').write_bytes((ROOT/'tutnt/maps/tnt01gpt.wad').read_bytes())
 (f/'LANGUAGE').write_bytes((ROOT/'tutnt/LANGUAGE.txt').read_bytes())
 return f
def state_test(mod):
 from check_engine import run_case
 vr=ROOT/'tutnt/.codex/validation/tnt01gpt';vr.mkdir(parents=True,exist_ok=True)
 f=fixture()
 (f/'ZSCRIPT').write_bytes((ROOT/'tools/fixtures/tnt01gpt-state/ZSCRIPT').read_bytes())
 (f/'MAPINFO').write_text((ROOT/'tutnt/mapinfo/MAPINFO.tnt01gpt').read_text()+'\n'+(ROOT/'tools/fixtures/tnt01gpt-state/MAPINFO').read_text())
 commands='wait 100;netevent gptroster 120;wait 5;netevent gptseed;wait 140;netevent gptverify;wait 5;save gptstate;wait 15;map TNT01GPT;wait 80;netevent gptzero;wait 5;load gptstate;wait 100;netevent gptverify;wait 5;skill 2;map TNT01GPT;wait 100;netevent gptroster 103;wait 5;skill 1;map TNT01GPT;wait 100;netevent gptroster 87;wait 5;echo UTNT_TEST_END;quit'
 result=run_case(Path('F:/DoomDev/uzdoom.exe'),Path('F:/DoomDev/DOOM2.WAD'),root=vr,mod=mod,addon=f,mapname='TNT01GPT',settings=[('skill',3),('use_mouse','false')],label='state-skills',timeout=90,commands=commands)
 log=Path(result['log']).read_text();result['ok'] &= 'invalid characters' not in log and result['assertions']==29 and (vr/'logs/saves/gptstate.zds').exists()
 (vr/'state-skills.json').write_text(json.dumps(result,indent=2));print(log[-4000:]);return result['ok']

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3');p.add_argument('--state',action='store_true',help='Test three skills and real save/load restoration');a=p.parse_args()
 if a.state:sys.exit(0 if state_test(a.mod) else 1)
 f=fixture();vr=ROOT/'tutnt/.codex/validation/tnt01gpt';vr.mkdir(parents=True,exist_ok=True)
 cfg=LOG/'traversal.ini';cfg.write_text('[GlobalSettings]\nvid_fullscreen=false\nwin_w=960\nwin_h=540\nvid_vsync=false\nvid_maxfps=120\n')
 logpath=LOG/'traversal.log'
 args=['F:/DoomDev/uzdoom.exe','-iwad','F:/DoomDev/DOOM2.WAD','-file',str(a.mod),str(f),'-config',str(cfg),'-savedir',str(LOG),'-noautoload','-nosound','-stdout','-noidle','-rngseed','667','+vid_fullscreen','false','+vid_preferbackend','1','+playerclass','Marine','+skill','3','+use_mouse','false','+i_timescale','5','+map','TNT01GPT']
 si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
 start=time.monotonic();log=''
 with logpath.open('w',encoding='utf-8') as stream:
  game=subprocess.Popen(args,cwd=WORK,stdout=stream,stderr=subprocess.STDOUT,startupinfo=si,creationflags=subprocess.CREATE_NO_WINDOW)
  while game.poll() is None and time.monotonic()-start<240:
   time.sleep(.3);log=logpath.read_text(encoding='utf-8',errors='replace')
   if any(marker in log for marker in ['GPT_ROUTE_COMPLETE','UTNT_ASSERT FAIL','Script error,','VM execution aborted']):break
  if game.poll() is None:game.terminate()
  game.wait(timeout=10)
 log=logpath.read_text(encoding='utf-8',errors='replace')
 result=dict(ok='GPT_ROUTE_COMPLETE' in log and 'UTNT_ASSERT FAIL' not in log,seconds=round(time.monotonic()-start,2),assertions=log.count('UTNT_ASSERT PASS'),log=str(logpath))
 (vr/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));print(log[-5500:]);sys.exit(0 if result['ok'] else 1)
