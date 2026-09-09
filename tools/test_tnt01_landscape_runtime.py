"""Verify TNT01 landscape planes, BSP ownership, passage collision and save/load in UZDoom."""
import argparse,collections,json,math,shutil
from pathlib import Path
from check_engine import run_case
from build_tnt01_organic import parse

def prepare(work,mapfile,manifest):
 r=json.loads(manifest.read_text());fixture=work/'landscape-runtime-fixture';(fixture/'maps').mkdir(parents=True,exist_ok=True)
 shutil.copyfile(mapfile,fixture/'maps/tnt01.wad')
 points=[];sectors=parse(mapfile)[3]['sector'];equivalent=collections.defaultdict(list)
 for m in r['mesh']:
  equivalent[m['parent'],tuple(sorted(sectors[m['sector']].items()))].append(m['sector'])
 for m in r['mesh']:
  x,y,z=[sum(p[k] for p in m['points'])/3 for k in range(3)]
  points.append(f'PointCheck({x:.8f},{y:.8f},{z:.8f},{m["sector"]});')
 walks=[]
 for i,route in enumerate(r['routes']):
  ps=route['points']
  for reverse in (False,True):
   chain=list(reversed(ps)) if reverse else ps
   walks.append(f'StartWalk({chain[0][0]},{chain[0][1]});')
   walks.extend(f'Walk({p[0]},{p[1]},{q[0]},{q[1]},{i});' for p,q in zip(chain,chain[1:]))
 chunks=[''.join(points[i:i+150]) for i in range(0,len(points),150)]
 code='''version "4.14"
class LandscapeRuntime : EventHandler
{
 int HeightErrors,OwnershipErrors,WalkErrors,WalkSteps,CoplanarAliases; double MaxError;
 void Assert(bool ok,String name){Console.Printf("UTNT_ASSERT %s: %s",ok?"PASS":"FAIL",name);}
 void PointCheck(double x,double y,double expected,int index)
 {
  let s=level.PointInSector((x,y));if(s.Index()!=index)
  {
   if(Equivalence(s.Index())==Equivalence(index))CoplanarAliases++;
   else {OwnershipErrors++;Console.Printf("LANDSCAPE_OWNER expected=%d actual=%d x=%.8f y=%.8f",index,s.Index(),x,y);}
  }
  double error=abs(s.floorplane.ZatPoint((x,y))-expected);MaxError=max(MaxError,error);if(error>0.001)HeightErrors++;
 }
 void StartWalk(double x,double y)
 {
  let p=players[0].mo;p.bInvulnerable=true;p.bNoGravity=false;p.bNoclip=false;p.Vel=(0,0,0);
  double z=level.PointInSector((x,y)).floorplane.ZatPoint((x,y));p.SetOrigin((x,y,z),false);
 }
 void Walk(double x,double y,double xx,double yy,int route)
 {
  let p=players[0].mo;int steps=max(1,int(ceil(sqrt((xx-x)*(xx-x)+(yy-y)*(yy-y))/4)));
  for(int step=1;step<=steps;step++)
  {
   Vector2 next=(x+(xx-x)*step/steps,y+(yy-y)*step/steps);
   if(!p.TryMove(next,1)){WalkErrors++;Console.Printf("LANDSCAPE_BLOCK route=%d x=%.3f y=%.3f z=%.3f floor=%.3f line=%d",route,next.x,next.y,p.Pos.Z,p.FloorZ,p.BlockingLine?p.BlockingLine.Index():-1);if(p.BlockingMobj)Console.Printf("LANDSCAPE_BLOCK_ACTOR %s",p.BlockingMobj.GetClassName());break;}
   WalkSteps++;p.SetOrigin((p.Pos.X,p.Pos.Y,p.FloorZ),false);
  }
 }
'''
 # Nodes can merge identical coplanar surfaces. Only allow aliases with the same
 # original parent and every sector field byte-identical, including materials.
 code+='int Equivalence(int index){switch(index){'
 for group in equivalent.values():
  if len(group)>1:code+=''.join(f'case {i}:' for i in group)+f'return {min(group)};'
 code+='default:return index;}}\n'
 code+=''.join(f'void Points{i}(){{{s}}}\n' for i,s in enumerate(chunks))
 # The source map has a solid tree on one terrain connector. Temporarily remove
 # only its actor collision in this test fixture to isolate the changed terrain.
 # The delivered map retains every Thing; player/wall/floor collision stays on.
 code+='void Check(){HeightErrors=0;OwnershipErrors=0;WalkErrors=0;WalkSteps=0;CoplanarAliases=0;MaxError=0;Array<Actor> trees;let it=ThinkerIterator.Create("BigTree");Actor tree;while((tree=Actor(it.Next()))){if(tree.bSolid){trees.Push(tree);tree.bSolid=false;}}'
 code+=''.join(f'Points{i}();' for i in range(len(chunks)))+''.join(walks)
 code+='for(uint i=0;i<trees.Size();i++)trees[i].bSolid=true;Report();let p=players[0].mo;p.SetOrigin((-3100,-100,0),false);p.Vel=(0,0,0);}\n'
 code+=f'''void Report()
 {{
  Assert(level.Sectors.Size()=={r['after']['sector']},"expected landscape sector count");
  Assert(HeightErrors==0,"all {len(points)} floor planes match intended heights");
  Assert(OwnershipErrors==0,"all {len(points)} triangles have correct BSP surface properties");
  Assert(WalkErrors==0,"seven terrain passages pass wall and floor collision in both directions (trees isolated)");
  Console.Printf("LANDSCAPE_MEASURE maximum_height_error=%.9f walk_errors=%d height_errors=%d ownership_errors=%d walk_steps=%d identical_coplanar_aliases=%d",MaxError,WalkErrors,HeightErrors,OwnershipErrors,WalkSteps,CoplanarAliases);
 }}
 override void NetworkProcess(ConsoleEvent e){{if(e.Name=="landscapecheck")Check();}}
}}
'''
 (fixture/'zscript.zc').write_text(code);(fixture/'MAPINFO.txt').write_text('GameInfo { AddEventHandlers="LandscapeRuntime" }')
 return fixture

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ('work','mapfile','manifest','mod','engine','iwad'):p.add_argument('--'+key,type=Path,required=True)
 p.add_argument('--renderer',default='1');p.add_argument('--playerclass',default='Marine');a=p.parse_args()
 fixture=prepare(a.work,a.mapfile,a.manifest);label='landscape-runtime-'+a.renderer+'-'+a.playerclass
 commands=f'notarget; wait 350; netevent landscapecheck; wait 8; save {label}; wait 8; load {label}; wait 15; netevent landscapecheck; wait 8; screenshot logs/{label}.png; echo UTNT_TEST_END; wait 5; quit'
 r=run_case(a.engine,a.iwad,root=a.work,mod=a.mod,addon=fixture,mapname='TNT01',renderer=a.renderer,playerclass=a.playerclass,label=label,commands=commands,timeout=60,settings=[('vid_maxfps',60),('con_notifytime',0)])
 if r['assertions']!=8:r['ok']=False;r['errors'].append('expected eight assertions')
 output=Path(r['log']).read_text();r['measurements']=[s for s in output.splitlines() if 'LANDSCAPE_MEASURE' in s]
 (a.work/(label+'.json')).write_text(json.dumps(r,indent=2))
 if not r['ok']:print(output[-5000:]);return 1
 return 0
if __name__=='__main__':raise SystemExit(main())
