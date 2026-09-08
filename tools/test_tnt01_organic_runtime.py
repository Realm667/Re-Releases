"""Check actual UZDoom terrain heights, BSP ownership, collision and save/load."""
import argparse,json,math,shutil,sys
from pathlib import Path
from check_engine import run_case
from build_tnt01_organic import parse,sector_of
def prepare(work,mapfile,manifest):
 report=json.loads(Path(manifest).read_text());_,_,_,g=parse(mapfile)
 fixture=work/'runtime-fixture';(fixture/'maps').mkdir(parents=True,exist_ok=True)
 shutil.copyfile(mapfile,fixture/'maps/tnt01.wad')
 points=[]
 for si in range(report['original_counts']['sector'],len(g['sector'])):
  ids=set()
  for l in g['linedef']:
   if sector_of(g,l,'sidefront')==si or sector_of(g,l,'sideback')==si:ids.update((int(l['v1']),int(l['v2'])))
  assert len(ids)==3
  x=sum(float(g['vertex'][i]['x']) for i in ids)/3;y=sum(float(g['vertex'][i]['y']) for i in ids)/3;s=g['sector'][si]
  z=-(float(s['floorplane_a'])*x+float(s['floorplane_b'])*y+float(s['floorplane_d']))/float(s['floorplane_c'])
  points.append(f'PointCheck({x:.8f},{y:.8f},{z:.8f},{si});')
 walks=[]
 for m in report['meshes']:
  N=(len(m['vertices'])-1)//2;p=m['vertices'][0];q=m['vertices'][N//2]
  walks.append(f'Walk({p[0]:.8f},{p[1]:.8f},{q[0]:.8f},{q[1]:.8f});')
 code='''class OrganicRuntime : EventHandler
{
 int HeightErrors, OwnershipErrors, WalkErrors; double MaxError;
 void Assert(bool ok,String name){Console.Printf("UTNT_ASSERT %s: %s",ok?"PASS":"FAIL",name);}
 void PointCheck(double x,double y,double expected,int index)
 {
  let s=level.PointInSector((x,y));if(s.Index()!=index)OwnershipErrors++;
  double error=abs(s.floorplane.ZatPoint((x,y))-expected);MaxError=max(MaxError,error);if(error>0.001)HeightErrors++;
 }
 void Walk(double x,double y,double xx,double yy)
 {
  let p=players[0].mo;p.bInvulnerable=true;p.bNoGravity=false;p.bNoclip=false;p.Vel=(0,0,0);
  double z=level.PointInSector((x,y)).floorplane.ZatPoint((x,y));p.SetOrigin((x,y,z),false);
  for(int step=1;step<=48;step++)
  {
   Vector2 next=(x+(xx-x)*step/48.0,y+(yy-y)*step/48.0);
   if(!p.TryMove(next,1)){WalkErrors++;break;}
   p.SetOrigin((p.Pos.X,p.Pos.Y,p.FloorZ),false);
  }
 }
 void Check()
 {
  HeightErrors=0;OwnershipErrors=0;WalkErrors=0;MaxError=0;
 '''+''.join(points)+''.join(walks)+'''
  Report();
  let p=players[0].mo;p.SetOrigin((-3100,-100,0),false);p.Vel=(0,0,0);
 }
 void Report()
 {
 '''+f'''
  Assert(level.Sectors.Size()=={len(g['sector'])},"expected terrain sector count");
  Assert(HeightErrors==0,"all {len(points)} sloped floor heights match design");
  Assert(OwnershipErrors==0,"all {len(points)} triangles resolve to correct BSP sector");
  Assert(WalkErrors==0,"collision traversal across {len(walks)} terrain formations");
  Console.Printf("ORGANIC_MEASURE maximum_height_error=%.9f walk_errors=%d height_errors=%d ownership_errors=%d",MaxError,WalkErrors,HeightErrors,OwnershipErrors);
 }}
 override void NetworkProcess(ConsoleEvent e){{if(e.Name=="organiccheck")Check();}}
}}
'''
 (fixture/'zscript.zc').write_text('version "4.14"\n'+code)
 (fixture/'MAPINFO.txt').write_text('GameInfo { AddEventHandlers="OrganicRuntime" }')
 return fixture
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for key in ('work','mapfile','manifest','mod','engine','iwad'):p.add_argument('--'+key,type=Path,required=True)
 p.add_argument('--renderer',default='1');p.add_argument('--playerclass',default='Marine');a=p.parse_args()
 fixture=prepare(a.work,a.mapfile,a.manifest);label='organic-runtime-'+a.renderer+'-'+a.playerclass
 commands=f'notarget; wait 350; netevent organiccheck; wait 8; save {label}; wait 8; load {label}; wait 15; netevent organiccheck; wait 8; screenshot logs/{label}.png; echo UTNT_TEST_END; wait 5; quit'
 r=run_case(a.engine,a.iwad,root=a.work,mod=a.mod,addon=fixture,mapname='TNT01',renderer=a.renderer,playerclass=a.playerclass,label=label,commands=commands,timeout=60,settings=[('vid_maxfps',60),('con_notifytime',0)])
 if r['assertions']!=8:r['ok']=False;r['errors'].append('expected eight assertions')
 output=Path(r['log']).read_text();r['measurements']=[s for s in output.splitlines() if 'ORGANIC_MEASURE' in s]
 (a.work/(label+'.json')).write_text(json.dumps(r,indent=2))
 if not r['ok']:print(output[-4000:]);return 1
 return 0
if __name__=='__main__':raise SystemExit(main())
