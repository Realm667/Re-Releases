"""Deterministic engine fixtures for environmental effects. Outputs stay local."""
from pathlib import Path
import shutil
import argparse,json,sys,struct,os,re
from PIL import Image,ImageChops,ImageStat
from check_engine import run_case
ROOT=Path(__file__).resolve().parent.parent
WORK=ROOT/'tutnt/.codex/validation/environment-fx'
ENGINE=Path('F:/DoomDev/Projects/wolfendoom.dev/#standalone/uzdoom.exe')
IWAD=Path('F:/DoomDev/DOOM2.WAD')
def wad(path,text):
 body=text.encode();entries=[(b'ENVTEST',b''),(b'TEXTMAP',body),(b'ENDMAP',b'')]
 data=bytearray();directory=bytearray()
 for name,payload in entries:
  directory+=struct.pack('<II8s',12+len(data),len(payload),name);data+=payload
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_bytes(struct.pack('<4sII',b'PWAD',3,12+len(data))+data+directory)
def fixture():
 addon=ROOT/'tools/fixtures/environment'
 addon.mkdir(parents=True,exist_ok=True)
 vertices=[];sides=[];lines=[];edges={};sectors=[]
 def polygon(points,sector):
  ids=[]
  for p in points:
   if p not in vertices:vertices.append(p)
   ids.append(vertices.index(p))
  for a,b in zip(ids,ids[1:]+ids[:1]):
   side=len(sides);sides.append(sector)
   if (b,a) in edges:lines[edges[b,a]]['back']=side
   else:edges[a,b]=len(lines);lines.append(dict(a=a,b=b,front=side,back=-1))
 for y in range(3):
  for x in range(4):
   i=y*4+x
   polygon([(x*256,y*256),(x*256,y*256+256),(x*256+256,y*256+256),(x*256+256,y*256)],i)
   sectors.append((-64 if i==9 else 0,96 if i==5 else 256,'SNOW3' if i==4 else 'QLAVA' if i==3 else 'GRAVE01','CEIL1_1' if i==5 else 'F_SKY1',90 if i==9 else 66 if i==6 else 50 if i==7 else 0))
 for i,(f,c,flat,ceil,tag) in enumerate([(64,80,'GRAVE01','CEIL1_1',0),(-192,32,'QWATER1','QWATER1',0)],12):
  x=1400+(i-12)*128;polygon([(x,0),(x,64),(x+64,64),(x+64,0)],i);sectors.append((f,c,flat,ceil,tag))
 # Long, wide submerged hall; distances of 256/512/1024 are easy to compare.
 for points,record in [
  ([(0,1024),(0,2560),(1024,2560),(1024,1024)],(-192,256,'GRAVE01','CEIL1_1',90)),
  ([(1152,512),(1152,640),(1408,640),(1408,512)],(0,0,'GRAVE01','CEIL1_1',51)),
  ([(1152,256),(1152,512),(1408,512),(1408,256)],(0,192,'GRAVE01','CEIL1_1',0)),
  ([(1152,640),(1152,896),(1408,896),(1408,640)],(0,192,'GRAVE01','CEIL1_1',0)),
  ([(1152,1024),(1152,1536),(1664,1536),(1664,1024)],(0,192,'GRAVE01','CEIL1_1',52))]:
  polygon(points,len(sectors));sectors.append(record)
 t='namespace="ZDoom";\n'
 for x,y in vertices:t+=f'vertex {{ x={x}.0; y={y}.0; }}\n'
 interior={s for l in lines if l['back']>=0 for s in (l['front'],l['back'])}
 for i,s in enumerate(sides):
  middle='-' if i in interior else 'STARTAN3'
  if s==3 and any(l['front']==i and vertices[l['a']][0]==1024 and vertices[l['b']][0]==1024 for l in lines):middle='QLAVA'
  t+=f'sidedef {{ sector={s}; texturemiddle="{middle}"; texturetop="STARTAN3"; texturebottom="STARTAN3"; }}\n'
 for l in lines:
  ctrl=sides[l['front']]
  special='special=160; arg0=66; arg1=1; arg4=255;' if ctrl==12 else 'special=160; arg0=90; arg1=2; arg3=96;' if ctrl==13 else ''
  if ctrl in (12,13) and l!=next(q for q in lines if sides[q['front']]==ctrl):special='' # one is sufficient, duplicates have same harmless effect
  t+=f'linedef {{ v1={l["a"]}; v2={l["b"]}; sidefront={l["front"]}; '+(f'sideback={l["back"]}; twosided=true;' if l['back']>=0 else 'blocking=true;')+special+' }\n'
 for f,c,flat,ceil,tag in sectors:t+=f'sector {{ heightfloor={f}; heightceiling={c}; texturefloor="{flat}"; textureceiling="{ceil}"; lightlevel=192; id={tag}; }}\n'
 t+='thing { x=128.0;y=128.0;type=1;angle=0;skill1=true;skill2=true;skill3=true;skill4=true;skill5=true;single=true;coop=true; }\n'
 for x,y in [(128,128),(384,384),(640,384),(640,128),(896,128)]:
  t+=f'thing {{ x={x}.0;y={y}.0;type=19021;skill1=true;skill2=true;skill3=true;skill4=true;skill5=true;single=true;coop=true; }}\n'
 wad(addon/'maps/envtest.wad',t)
 (addon/'MAPINFO').write_text('gameinfo { AddEventHandlers="UTNTEnvironmentRegression" }\nmap ENVTEST "Environment regression" { levelnum=92 }\n')
 (addon/'CVARINFO').write_text('user bool UTNT_localheatprototype = false;\nuser bool UTNT_heatlabmask = false;\n')
 (addon/'ZSCRIPT').write_text(TEST_SCRIPT+'\n#include "heat-prototype.zc"\n')
 for filename in ('heat-prototype.zc','heat-prototype.fp'):shutil.copy2(ROOT/'tools/fixtures/environment-prototype'/filename,addon/filename)
 with (addon/'MAPINFO').open('a') as stream:stream.write('\ngameinfo { AddEventHandlers="UTNTLocalHeatLab" }\n')
 env=addon/'environment';env.mkdir(exist_ok=True)
 rows=[]
 for k,si,x,y in [(0,0,0,0),(1,5,256,256),(2,6,512,256)]:
  rows.append(f'0|{si}|0|GRAVE01|EVTEST{k}|{k}|{x}|{y}|0|1|0|0|256|256|1|1')
 (env/'ENVTEST-surfaces.txt').write_text('\n'.join(rows))
 (env/'ENVTEST-mechanisms.txt').write_text('7|896|384|1|50\n15|1280|576|1|51\n18|1408|1280|1|52\n')

 textures=[];defs=[]
 src=(ROOT/'tutnt/shaders/environment/surface.glsl').read_text().replace('ENV_ORIGINAL_BODY','mat.Base=getTexel(vTexCoord.st);mat.Normal=normalize(vWorldNormal.xyz);')
 (addon/'surface.fp').write_text(src)
 (addon/'materials').mkdir(exist_ok=True)
 for k,si,x,y in [(0,0,0,0),(1,5,256,256),(2,6,512,256)]:
  textures.append(f'Texture EVTEST{k},64,64 {{ Patch "GRAVE01",0,0 }}')
  values=[k,1,1,int((x+65536)*16),int((y+65536)*16),65536*16,65534,32767,32767,4096,4096,0,0,0,0,0]
  im=Image.new('RGB',(16,1));im.putdata([((v>>16)&255,(v>>8)&255,v&255) for v in values]);im.save(addon/'materials'/f'meta{k}.png')
  defs.append(f'Material Texture EVTEST{k} {{ Shader "surface.fp" Texture envMeta "materials/meta{k}.png" Texture envState "UENVSTATE" }}')
 (addon/'TEXTURES').write_text('\n'.join(textures));(addon/'GLDEFS').write_text('\n'.join(defs)+'\nHardwareShader PostProcess scene { Name "UTNTLocalHeatLab" Shader "heat-prototype.fp" 330 Uniform vec3 sourceDelta Uniform vec3 sourceRadius  Uniform vec3 rayForward  Uniform vec3 rayRight  Uniform vec3 rayUp  Uniform vec4 viewRect Uniform vec4 depthA Uniform vec4 depthB  }\n')
 from build_local_heat import detect, parse
 heat=detect(parse(addon/'maps/envtest.wad'))
 (env/'ENVTEST-heat.txt').write_text(''.join('|'.join(map(str,row))+'\n' for row in heat))
 return addon
TEST_SCRIPT=r'''version "5.0.0"
class UTNTEnvironmentRegression : EventHandler
{
 int WalkUntil,OriginalTerrain,BirthTics,MaxBirths,PreviousPuffs;bool Fly,RecordMotion;Vector3 CameraAt;UTNTEnvironmentDust TrackedDust;double PreviousAlpha;int AlphaSamples,AlphaRises;
 bool RecordArea;int AreaStart,SmallBefore,LargeBefore,SmallAtEnd,LargeAtEnd;
 int Coverage[8],TimeBins[8];Vector2 LastSmall;bool HaveLast;int Jumps,FarJumps,ContactBad;
 Array<UTNTEnvironmentDust> SeenDust;
 bool RecordGuides;int GuideBirths,GuideBad,GuideSamples,ShakeUntil,ShakeLabel;
 UTNTEnvironmentDust GuideDust;double GuideStartZ,GuideStartCeiling;
 UTNTEnvironmentDust CarryDust[2];double CarryZ[2],CarryPlane[2],CarryAlpha[2];int CarrySamples[2],CarryBad;
 ui int ShakeTic,ShakeFrames;ui Vector3 ViewLow,ViewHigh;
 override void RenderOverlay(RenderEvent e)
 {
  if(ShakeUntil<=0)return;
  if(ShakeTic!=ShakeUntil){ShakeTic=ShakeUntil;ShakeFrames=0;ViewLow=(1e30,1e30,1e30);ViewHigh=(-1e30,-1e30,-1e30);}
  if(level.time<ShakeUntil)
  {
   ViewLow=(min(ViewLow.X,e.ViewPos.X),min(ViewLow.Y,e.ViewPos.Y),min(ViewLow.Z,e.ViewPos.Z));
   ViewHigh=(max(ViewHigh.X,e.ViewPos.X),max(ViewHigh.Y,e.ViewPos.Y),max(ViewHigh.Z,e.ViewPos.Z));ShakeFrames++;
  }
  else if(ShakeFrames>0)
  {
   Console.Printf("SHAKEVIEW|label=%d|frames=%d|x=%.5f|y=%.5f|z=%.5f",ShakeLabel,ShakeFrames,ViewHigh.X-ViewLow.X,ViewHigh.Y-ViewLow.Y,ViewHigh.Z-ViewLow.Z);ShakeFrames=0;
  }
 }
 void Check(bool ok,String message){Console.Printf("UTNT_ASSERT %s: %s",ok?"PASS":"FAIL",message);}
 override void WorldTick()
 {
  let mo=players[0].mo;if(!mo)return;
  if(level.time==2){mo.bInvulnerable=true;mo.Angle=0;OriginalTerrain=level.Sectors[0].GetTerrain(Sector.floor);}
  if(Fly){mo.bNoGravity=true;mo.Vel=(0,0,0);mo.SetOrigin(CameraAt,false);players[0].camera=mo;}
  if(level.time<WalkUntil)mo.Vel=(2,0,mo.Vel.Z);
  if(!TrackedDust && RecordMotion)
  {
   let it=ThinkerIterator.Create('UTNTEnvironmentDust',Thinker.MAX_STATNUM+1,true);TrackedDust=UTNTEnvironmentDust(it.Next());
   if(TrackedDust)PreviousAlpha=TrackedDust.Alpha;
  }
  if(TrackedDust)
  {
   if(TrackedDust.Age>7){AlphaSamples++;if(TrackedDust.Alpha>PreviousAlpha+.00001)AlphaRises++;}
   PreviousAlpha=TrackedDust.Alpha;
  }
  if(RecordMotion)
  {
   let env=UTNTEnvironment.Get();int births=env.DustPuffs-PreviousPuffs;
   if(births>0)BirthTics++;MaxBirths=max(MaxBirths,births);PreviousPuffs=env.DustPuffs;
  }
  if(RecordArea)
  {
   let env=UTNTEnvironment.Get();
   let it=ThinkerIterator.Create('UTNTEnvironmentDust',Thinker.MAX_STATNUM+1,true);
   UTNTEnvironmentDust d;
   while((d=UTNTEnvironmentDust(it.Next()))!=null)
   {
    if(d.Age>1 || SeenDust.Find(d)<SeenDust.Size())continue;
    SeenDust.Push(d);int which=d.Support==level.Sectors[7]?0:d.Support==level.Sectors[18]?1:-1;
    if(which<0)continue;
    double edgeDistance=which==0?abs(d.Pos.X-1024):min(min(abs(d.Pos.X-1152),abs(d.Pos.X-1664)),min(abs(d.Pos.Y-1024),abs(d.Pos.Y-1536)));
    if(edgeDistance<d.WallRadius()-.5 || edgeDistance>d.WallRadius()+6)ContactBad++;
    Vector2 center=which==0?(896,384):(1408,1280);
    int quadrant=(d.Pos.X>center.X?1:0)+(d.Pos.Y>center.Y?2:0);
    Coverage[which*4+quadrant]++;
    int bin=(level.time-AreaStart)/64;if(bin>=0 && bin<4)TimeBins[which*4+bin]++;
    if(which==0){if(HaveLast){Jumps++;if((d.Pos.XY-LastSmall).Length()>128)FarJumps++;}LastSmall=d.Pos.XY;HaveLast=true;}
   }
   if(level.time-AreaStart==260){SmallAtEnd=env.Mechanisms[0].EmissionCursor;LargeAtEnd=env.Mechanisms[2].EmissionCursor;}
  }
  if(RecordArea)
  {
   for(int k=0;k<2;k++)
   {
    if(!CarryDust[k])
    {
     let it=ThinkerIterator.Create('UTNTEnvironmentDust',Thinker.MAX_STATNUM+1,true);UTNTEnvironmentDust d;
     while((d=UTNTEnvironmentDust(it.Next()))!=null)if(d.Support==level.Sectors[k==0?7:18] && d.Age<3)
     {CarryDust[k]=d;CarryZ[k]=d.Pos.Z;CarryPlane[k]=k==0?d.Support.floorplane.ZatPoint(d.Pos.XY):d.Support.ceilingplane.ZatPoint(d.Pos.XY);CarryAlpha[k]=d.Alpha;break;}
    }
    let d=CarryDust[k];if(!d)continue;
    double plane=k==0?d.Support.floorplane.ZatPoint(d.Pos.XY):d.Support.ceilingplane.ZatPoint(d.Pos.XY);
    double delta=plane-CarryPlane[k];
    if(abs(delta)>.01)
    {
     double clearance=k==0?d.Pos.Z-plane:plane-d.Pos.Z;
     double wallGap=k==0?1024-d.Pos.X:min(min(d.Pos.X-1152,1664-d.Pos.X),min(d.Pos.Y-1024,1536-d.Pos.Y));
     if(wallGap<d.WallRadius()-.5)CarryBad++;
     CarrySamples[k]++;if(clearance<10 || (d.Age>7 && abs(d.Alpha-CarryAlpha[k])>.025))CarryBad++;
    }
    CarryZ[k]=d.Pos.Z;CarryPlane[k]=plane;CarryAlpha[k]=d.Alpha;
   }
  }
  if(RecordGuides)
  {
   let it=ThinkerIterator.Create('UTNTEnvironmentDust',Thinker.MAX_STATNUM+1,true);UTNTEnvironmentDust d;
   while((d=UTNTEnvironmentDust(it.Next()))!=null)
   {
    if(d.Support!=level.Sectors[15] || d.Age!=1)continue;
    GuideBirths++;double gap=min(abs(d.Pos.X-1152),abs(d.Pos.X-1408));if(gap<d.WallRadius()-.5 || gap>d.WallRadius()+6)GuideBad++;
    if(!GuideDust){GuideDust=d;GuideStartZ=d.Pos.Z;GuideStartCeiling=level.Sectors[15].ceilingplane.ZatPoint(d.Pos.XY);}
   }
   if(GuideDust && GuideDust.Age==15)
   {
    double plane=level.Sectors[15].ceilingplane.ZatPoint(GuideDust.Pos.XY);
    Check(plane-GuideStartCeiling>16 && abs(GuideDust.Pos.Z-GuideStartZ)<12,"door dust stays in guide while door rises");GuideSamples++;
   }
  }
  if(level.time==105 && level.MapName~=="ENVTEST")
  {
   let h=UTNTEnvironment.Get();
   Check(h && h.Ready,"environment initialized");
   Check(h.Surfaces.Size()==3,"rain surfaces bound");
   Check(h.Surfaces[0].Exposed[0]>0,"open floor receives rain");
   Check(h.Surfaces[1].Exposed[0]==0,"roofed floor stays dry");
   Check(h.Surfaces[2].Exposed[0]==0,"solid 3D floor blocks rain below");

   Check(level.Sectors[0].GetTerrain(Sector.floor)==OriginalTerrain,"material binding preserves terrain behavior");
   Check(h.Mechanisms.Size()==3,"mechanism watcher created");
   Check(h.Mechanisms[0].ContactLength()==256,"coplanar open joins do not count as rubbing walls");
  }
 }
 override void NetworkProcess(ConsoleEvent e)
 {
  let mo=players[0].mo;let h=UTNTEnvironment.Get();
  if(e.Name=="envpos"){CameraAt=(e.Args[0],e.Args[1],e.Args[2]);players[0].camera=mo;mo.SetOrigin((e.Args[0],e.Args[1],e.Args[2]),false);mo.Vel=(0,0,0);mo.Pitch=45;mo.Angle=0;}
  if(e.Name=="envfly"){Fly=true;CameraAt=mo.Pos;mo.bNoGravity=true;mo.bNoClip=true;mo.Vel=(0,0,0);}
  if(e.Name=="envview"){mo.Angle=e.Args[0];mo.Pitch=e.Args[1];}
  if(e.Name=="envwalk"){WalkUntil=level.time+e.Args[0];}
  if(e.Name=="envwet"){h.Feet[0].WetSole=1;}
  if(e.Name=="envmove"){Floor_RaiseByValue(50,16,32);}
  if(e.Name=="envstream"){RecordMotion=true;BirthTics=MaxBirths=AlphaSamples=AlphaRises=0;TrackedDust=null;PreviousPuffs=h.DustPuffs;Floor_RaiseByValue(50,8,96);}
  if(e.Name=="envshort"){Floor_RaiseByValue(50,32,2);}
  if(e.Name=="envstreamcheck")
  {
   Check(AlphaSamples>12 && AlphaRises==0,"existing dust fades continuously through mover stop");
   Check(BirthTics>=8,"dust births spread across moving tics");Check(MaxBirths<=4,"per-mover emission safety cap respected");
   Check(h.Mechanisms[0].Starts>0 && h.Mechanisms[0].Stops>0,"start and stop tracked");
   Check(h.Mechanisms[0].LastQuake>0,"nearby motion produces cosmetic quake");
   Console.Printf("STREAM|birth_tics=%d|max_births=%d|puffs=%d",BirthTics,MaxBirths,h.DustPuffs);RecordMotion=false;
  }
  if(e.Name=="envareastart")
  {
   RecordArea=true;AreaStart=level.time;SmallBefore=h.Mechanisms[0].EmissionCursor;LargeBefore=h.Mechanisms[2].EmissionCursor;
   Floor_RaiseByValue(50,4,128);Ceiling_LowerByValue(52,4,128);
  }
  if(e.Name=="envareacheck")
  {
   Check(CarrySamples[0]>8 && CarrySamples[1]>8 && CarryBad==0,"growing clouds keep wall clearance and continuous alpha");
   Console.Printf("CARRY|floor=%d|ceiling=%d|bad=%d",CarrySamples[0],CarrySamples[1],CarryBad);
   int small=h.Mechanisms[0].EmissionCursor-SmallBefore,large=h.Mechanisms[2].EmissionCursor-LargeBefore;
   double ratio=large/double(max(1,small));
   Check(h.Mechanisms[0].Area==65536 && h.Mechanisms[2].Area==262144,"actual moving polygon areas measured");
   Check(small>12 && ratio>5 && ratio<12,"dust frequency scales with rubbing edge length");
   Check(ContactBad==0,"all births stay at physical contact edges, never in plane interiors");
   bool covered=true,continuous=true;
   for(int i=0;i<8;i++){if((i==1 || i==3 || i>=4) && Coverage[i]<2)covered=false;if(TimeBins[i]<2)continuous=false;}
   Check(covered,"random births cover both wall halves and all ceiling edges");
   Check(continuous,"both movers emit in every quarter of movement duration");
   Check(Jumps>12 && FarJumps>1,"successive births scatter along contacts instead of forming a chain");
   Check(h.Mechanisms[0].EmissionCursor==SmallAtEnd && h.Mechanisms[2].EmissionCursor==LargeAtEnd,"births cease when movement stops");
   Console.Printf("AREA|small=%d|large=%d|ratio=%.3f|jumps=%d|far=%d",small,large,ratio,Jumps,FarJumps);RecordArea=false;
  }
  if(e.Name=="envheatcheck")
  {
   let heat=UTNTLocalHeat(EventHandler.Find('UTNTLocalHeat'));int count=0;
   for(int i=0;i<6;i++)if(heat.Anchors[i])count++;
   Check(heat.Sources.Size()>0,"map-derived lava volumes loaded");Check(count>0 && count<=6,"local heat anchor pool bounded and active");
  }
  if(e.Name=="envlakecheck")
  {
   let heat=UTNTLocalHeat(EventHandler.Find('UTNTLocalHeat'));int lake=0,wall=0;
   for(int i=0;i<6;i++)if(heat.Anchors[i])
   {
    let s=heat.Sources[heat.Anchors[i].Source];
    Vector3 position=s.Position();if(s.Kind==2 && s.Index==46 && s.Valid() && position.Z>-512 && position.Z<=-416)lake++;
    if(s.Kind==1 && s.Valid())wall++;
   }
   Check(lake>0,"first TNT02 lake has active heat above its visible 3D floor");
   Check(wall>0,"visible lavafall retains a heat slot beside the broad lake");
  }
  if(e.Name=="envheatoffcheck")
  {
   let heat=UTNTLocalHeat(EventHandler.Find('UTNTLocalHeat'));int count=0;for(int i=0;i<6;i++)if(heat.Anchors[i])count++;
   Check(count==0,"disabled heat releases all local anchors");
  }
  if(e.Name=="envwallfitcheck")
  {
   let d=UTNTEnvironmentDust(level.SpawnClientSideVisualThinker('UTNTEnvironmentDust'));
   d.Support=level.Sectors[12];d.Pos=(1402,2,72);d.Prev=d.Pos;d.Scale=(.3,.3);
   bool fits=d.FitWalls();double r=d.WallRadius();
   Check(fits && d.Pos.X>=1400+r-.01 && d.Pos.Y>=r-.01 && d.Pos.X<=1464-r+.01 && d.Pos.Y<=64-r+.01,"smoke clears both walls at a narrow room corner");
   d.Scale=(.5,.5);Check(!d.FitWalls(),"oversized smoke is rejected in a narrow guide");d.Destroy();
  }
  if(e.Name=="envguides"){RecordGuides=true;Door_Raise(51,16,105);}
  if(e.Name=="envguidescheck")
  {
   Check(GuideBirths>=3 && GuideBad==0,"door births confined to both side guides");
   Check(GuideSamples>0,"stationary door dust observed over multiple movement tics");RecordGuides=false;
   Console.Printf("GUIDES|births=%d|outside=%d|samples=%d",GuideBirths,GuideBad,GuideSamples);
  }
  if(e.Name=="envshakemove"){Floor_RaiseByValue(50,2,128);}
  if(e.Name=="envfog"){for(int i=0;i<level.Sectors.Size();i++){level.Sectors[i].SetLightLevel(32);level.Sectors[i].SetFade(Color(24,10,0));level.Sectors[i].SetFogDensity(e.Args[0]);}}
  if(e.Name=="envshakecapture"){ShakeLabel=e.Args[0];ShakeUntil=level.time+28;}
  if(e.Name=="envdoor"){Door_Raise(51,16,105);}
  if(e.Name=="envceiling"){Ceiling_LowerByValue(52,8,96);}
  if(e.Name=="envceilingup"){Ceiling_RaiseByValue(52,8,96);}
  if(e.Name=="envmotioncheck"){Check(h.Mechanisms[1].LastBurst>0,"door emits dust");Check(h.Mechanisms[2].LastBurst>0,"ceiling emits dust");Check(h.DustPuffs>0,"visible dust thinkers spawned");}
  if(e.Name=="envmirroroffcheck"){Check(!h.Surfaces[0].Reflecting && level.Sectors[0].GetPlaneReflectivity(0)==0 && level.Sectors[0].GetAlpha(0)==1,"disabled wetness restores opaque floor");}
  if(e.Name=="envmirrorcheck"){Console.Printf("NATIVE|r=%.6f|a=%.6f|can=%d|active=%d",level.Sectors[0].GetPlaneReflectivity(0),level.Sectors[0].GetAlpha(0),h.Surfaces[0].CanReflect,h.Surfaces[0].Reflecting);Check(h.Surfaces[0].Reflecting && level.Sectors[0].GetPlaneReflectivity(0)>0,"native rain mirror active");Check(!h.Surfaces[1].Reflecting && !h.Surfaces[2].Reflecting,"sheltered floors have no mirror");}

  if(e.Name=="envchecks")
  {
   Console.Printf("ENV_FOOT|t=%d|x=%.1f|y=%.1f|ground=%d|floor=%.1f|distance=%.1f|marks=%d",level.time,mo.Pos.X,mo.Pos.Y,players[0].onground,mo.FloorZ,h.Feet[0].Distance,h.Prints);Check(h.Prints>0,"footstep produces a visible mark");
   Check(h.MechanismBursts>0,"moving platform produces reaction");
   Check(h.Marks.Size()<=160,"footprint budget bounded");
   Console.Printf("UTNT_REGRESSION_COMPLETE");
  }
  if(e.Name=="environmentstats"){let cam=players[0].camera;Console.Printf("ENV_NATIVE_CAMERA|sector=%d|reflect=%.5f|3dfloors=%d|heightsec=%d",cam.CurSector.Index(),cam.CurSector.GetPlaneReflectivity(0),cam.CurSector.Get3DFloorCount(),cam.CurSector.heightsec!=null);Console.Printf("ENV_CAMERA|mo=%.1f,%.1f,%.1f|camera=%.1f,%.1f,%.1f",mo.Pos.X,mo.Pos.Y,mo.Pos.Z,cam.Pos.X,cam.Pos.Y,cam.Pos.Z);}
  if(e.Name=="envloadcheck"){Check(h.Ready && h.Surfaces[0].Wet[0]>0,"wet state survives save/load");Check(h.Prints==0,"save/load restores footprint state");}
  if(e.Name=="envwatercheck"){Console.Printf("ENV_WATER|z=%.2f|depth=%.2f|level=%d|sector=%d|heightsec=%d",mo.Pos.Z,mo.WaterDepth,mo.WaterLevel,mo.CurSector.Index(),mo.CurSector.heightsec?mo.CurSector.heightsec.Index():-1);Check(mo.WaterLevel>=3,"camera actually submerged");}
 }
}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',default='fixture',choices=['fixture','campaign','compile','prototype','motion','area','lake','guides','fog']);p.add_argument('--renderer',default='1');p.add_argument('--map',default='TNT02');p.add_argument('--at',nargs=3,type=int);p.add_argument('--angle',type=int,default=0);p.add_argument('--pitch',type=int,default=10);p.add_argument('--mod',type=Path,default=ROOT/'tutnt/.codex/builds/environment-dev.pk3');a=p.parse_args()
 WORK.mkdir(parents=True,exist_ok=True)
 addon=fixture()
 if a.case!='compile':
  preflight=run_case(ENGINE,IWAD,root=WORK,mod=a.mod,addon=addon,label='environment-preflight')
  if not preflight['ok']:
   print(Path(preflight['log']).read_text(encoding='utf-8')[-5000:]);sys.exit(1)
 if a.case=='compile':
  r=run_case(ENGINE,IWAD,root=WORK,mod=a.mod,addon=addon,label='fixture-compile')
  print(Path(r['log']).read_text()[-5000:]);sys.exit(0 if r['ok'] else 1)
 settings=[('vid_activeinbackground',True),('vid_lowerinbackground',False),('vid_maxfps',35),('cl_capfps',True),('motionblur',False),('UTNT_visoreffects',False),('use_mouse',False),('use_joystick',False),('i_pauseinbackground',False),('r_drawplayersprites',False)]
 if a.case in ('guides','fog'):
  cmds='wait 140; netevent envfly; netevent envpos 1280 384 0; netevent envview 90 0; wait 20; netevent envguides; wait 48; screenshot logs/door.png; wait 32; netevent envguidescheck; wait 5; netevent envpos 256 384 32; netevent envview 0 0; wait 30; netevent envshakecapture 0; wait 35; netevent envshakemove; wait 35; noclip; wait 5; netevent environmentstats; netevent envshakecapture 999; wait 35; noclip; wait 5; netevent environmentstats; netevent envshakecapture 512; wait 35; netevent envpos 384 384 32; wait 15; netevent envshakecapture 384; wait 35; netevent envpos 736 384 32; wait 15; netevent envshakecapture 32; wait 35; echo UTNT_TEST_END; quit' if a.case=='guides' else 'wait 175; netevent envfly; netevent envpos 3480 -5330 -239; netevent envview 90 24; wait 35; screenshot logs/fog.png; echo UTNT_TEST_END; quit'
  r=run_case(ENGINE,IWAD,root=WORK,mod=a.mod,addon=addon,mapname='ENVTEST' if a.case=='guides' else 'TNT02',renderer=a.renderer,label='environment-'+a.case+'-'+a.renderer,timeout=90,commands=cmds,settings=settings+[('con_notifytime',0),('UTNT_fxquality',3),('UTNT_reducedfx',False)])
 elif a.case=='lake':
  cmds='wait 175; netevent envfly; netevent envpos 700 -320 -128; netevent envview 0 8; wait 35; netevent localheatstats; netevent envlakecheck; wait 5; screenshot logs/lake-on.png; wait 12; screenshot logs/lake-motion.png; freeze; wait 3; screenshot logs/lake-frozen-on.png; UTNT_shaderoverlayswitch false; wait 3; screenshot logs/lake-frozen-off.png; freeze; wait 20; netevent envheatoffcheck; wait 5; echo UTNT_TEST_END; quit'
  r=run_case(ENGINE,IWAD,root=WORK,mod=a.mod,addon=addon,mapname='TNT02',renderer=a.renderer,label='environment-lake-'+a.renderer,timeout=90,commands=cmds,settings=settings+[('con_notifytime',0),('UTNT_fxquality',3),('UTNT_reducedfx',False)])
 elif a.case=='area':
  cmds='wait 140; netevent envfly; netevent envpos 1100 800 64; netevent envview 45 15; netevent envareastart; wait 128; screenshot logs/area-half.png; wait 155; netevent envareacheck; netevent envwallfitcheck; wait 5; echo UTNT_TEST_END; quit'
  r=run_case(ENGINE,IWAD,root=WORK,mod=a.mod,addon=addon,mapname='ENVTEST',renderer=a.renderer,label='environment-area-'+a.renderer,timeout=90,commands=cmds,settings=settings+[('UTNT_fxquality',3),('UTNT_reducedfx',False)])
 elif a.case=='motion':
  cmds='wait 140; netevent envfly; netevent envpos 690 128 0; netevent envview 0 0; wait 35; netevent localheatstats; netevent envheatcheck; screenshot logs/heat-live.png; wait 12; screenshot logs/heat-motion.png; UTNT_shaderoverlayswitch false; wait 20; netevent envheatoffcheck; screenshot logs/heat-off.png; UTNT_shaderoverlayswitch true; netevent envpos 650 384 112; netevent envview 0 25; netevent envstream; wait 40; screenshot logs/dust-during.png; wait 85; netevent envstreamcheck; screenshot logs/dust-end.png; netevent envshort; wait 8; screenshot logs/dust-short.png; wait 120; screenshot logs/dust-gone.png; netevent envpos 1280 384 0; netevent envview 90 0; netevent envdoor; wait 40; screenshot logs/door.png; netevent envpos 1408 1088 0; netevent envview 90 -15; netevent envceiling; wait 45; screenshot logs/ceiling.png; wait 75; netevent envmotioncheck; wait 5; echo UTNT_TEST_END; quit'
  r=run_case(ENGINE,IWAD,root=WORK,mod=a.mod,addon=addon,mapname='ENVTEST',renderer=a.renderer,label='environment-motion-'+a.renderer,timeout=90,commands=cmds,settings=settings+[('UTNT_fxquality',3),('UTNT_reducedfx',False)])
 elif a.case=='prototype':
  cmds='wait 350; netevent envfly; netevent envpos 690 128 0; wait 5; netevent envview 0 0; wait 140; UTNT_localheatprototype true; wait 10; netevent heatlabstats; wait 5; screenshot logs/heatlab-on.png; UTNT_localheatprototype false; wait 5; screenshot logs/heatlab-off.png; netevent heatlabmode 1; UTNT_localheatprototype true; wait 10; netevent heatlabstats; wait 5; screenshot logs/heatlab-wall.png; netevent heatlabmode 2; wait 10; netevent heatlabstats; wait 5; screenshot logs/heatlab-hidden.png; echo UTNT_TEST_END; quit'
  r=run_case(ENGINE,IWAD,root=WORK,mod=a.mod,addon=addon,mapname='ENVTEST',renderer=a.renderer,label='heatlab-'+a.renderer,timeout=45,commands=cmds,settings=settings)
 elif a.case=='fixture':
  cmds='wait 140; netevent envview 0 55; wait 5; netevent environmentstats; netevent envmirrorcheck; screenshot logs/env-rain.png; UTNT_wetsurfaces false; wait 5; screenshot logs/env-rain-off.png; UTNT_wetsurfaces true; wait 5; save env-state; wait 5; netevent envpos 32 384 0; wait 10; netevent envwalk 80; wait 90; netevent envview 180 60; wait 5; screenshot logs/env-snow.png; netevent envmove; wait 70; netevent envpos 512 1280 -192; wait 10; netevent envwatercheck; wait 5; screenshot logs/env-water.png; UTNT_underwateratmosphere false; wait 5; screenshot logs/env-water-off.png; UTNT_underwateratmosphere true; netevent envpos 32 128 0; wait 10; netevent envwet; netevent envwalk 80; wait 90; netevent envchecks; wait 5; netevent envview 180 60; wait 5; netevent environmentstats; wait 5; screenshot logs/env-wetprints.png; load env-state; wait 20; netevent envloadcheck; wait 5; netevent environmentstats; wait 5; echo UTNT_TEST_END; quit'
  r=run_case(ENGINE,IWAD,root=WORK,mod=a.mod,addon=addon,mapname='ENVTEST',renderer=a.renderer,label='environment-fixture-'+a.renderer,timeout=100,commands=cmds,settings=settings,regression=True)
 else:
  r=run_case(ENGINE,IWAD,root=WORK,mod=a.mod,addon=addon,mapname=a.map,renderer=a.renderer,label='environment-'+a.map+'-'+a.renderer,timeout=90,commands='wait 220; netevent envfly; wait 5; '+('netevent envpos '+' '.join(map(str,a.at))+'; wait 5; ' if a.at else '')+f'netevent envview {a.angle} {a.pitch}; wait 70; netevent environmentstats; wait 5; screenshot logs/env-'+a.map+'.png; echo UTNT_TEST_END; quit',settings=settings)
 if a.case=='guides' and r['ok']:
  output=Path(r['log']).read_text(encoding='utf-8')
  samples={int(label):float(x) for label,x in re.findall(r'SHAKEVIEW\|label=(\d+)\|frames=\d+\|x=([\d.]+)',output)}
  visible=all(k in samples for k in (0,999,512,384,32)) and samples[0]<.01 and samples[999]<.01 and .10<samples[512]<samples[384]<samples[32]
  r['camera_motion_x']=samples
  if not visible:r['ok']=False;r['errors'].append('camera shake must stop under noclip, be visible at 512 and increase toward mover')
 (WORK/(a.case+'-'+a.renderer+'.json')).write_text(json.dumps(r,indent=2))
 if not r['ok']:print(Path(r['log']).read_text()[-5000:]);sys.exit(1)
if __name__=='__main__':main()
