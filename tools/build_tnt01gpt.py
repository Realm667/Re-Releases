"""Build TNT01GPT (The Ashen Liturgy) from authored geometry and ACS.
Requires Shapely 2.1+, ACC and ZDBSP. No original campaign map is modified.
"""
from pathlib import Path
import sys,math,json,collections,subprocess,hashlib,argparse
ROOT=Path(__file__).resolve().parent.parent
CACHE=ROOT/'tutnt/.codex/cache/tnt01gpt-python'
if CACHE.is_dir():sys.path.insert(0,str(CACHE))
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import unary_union,polygonize
from shapely.geometry.polygon import orient
from shapely.strtree import STRtree
from build_utnt import write_wad,read_wad
WORK=ROOT/'tutnt/.codex/work/tnt01gpt'
THEMES={
 'A':(-64,640,'QGRASS','F_SKY1',168,'QROCK3'),
 'B':(0,512,'QFLAT06','F_SKY1',176,'QBRICK6'),
 'C':(0,352,'WOODF1','WOODF1',152,'QWOOD1'),
 'D':(128,384,'QFLAT06','QFLAT06',144,'QCHURCH'),
 'E':(0,416,'METALF24','METALF09',168,'QTECH01'),
 'F':(-32,192,'GRAVE02','METALF09',144,'QMET13'),
 'G':(0,640,'QFLAT06','F_SKY1',184,'QCHURCH'),
 'H':(64,320,'QFLAT06','QFLAT06',184,'QCHURCH'),
 'hall':(0,256,'METALF09','WOODF1',152,'QBRICK6')}
FIELDS=('heightfloor','heightceiling','texturefloor','textureceiling','lightlevel','wall')
THEMES={k:dict(zip(FIELDS,v)) for k,v in THEMES.items()}
def octagon(x,y,r):
 return Polygon([(round(x+r*math.cos(i*math.pi/4),3),round(y+r*math.sin(i*math.pi/4),3)) for i in range(8)])
def build(acc,zdbsp,output):
 WORK.mkdir(parents=True,exist_ok=True)
 regions=[];things=[];actions=[];rooms={};monsters=[]
 flags=dict(skill1=True,skill2=True,skill3=True,skill4=True,skill5=True,single=True,coop=True)
 def area(geom,theme=None,**props):
  if theme:props={**THEMES[theme],**props,'zone':theme}
  assert geom.is_valid and geom.area>0
  regions.append((geom,props));return geom
 def rect(x,y,w,h,theme=None,**props):return area(box(x,y,x+w,y+h),theme,**props)
 def room(name,geom):rooms[name]=geom;return area(geom,name)
 def hall(points,width=192,**props):
  return area(LineString(points).buffer(width/2,cap_style=2,join_style=2),'hall',**props)
 def thing(typ,x,y,z=0,**props):
  t={**flags,**props,'x':x,'y':y,'height':z,'angle':props.get('angle',90),'type':typ};things.append(t);return t
 def light(x,y,z=144,color=(255,190,100),radius=112,tid=0):
  return thing(9800,x,y,z,arg0=color[0],arg1=color[1],arg2=color[2],arg3=radius,id=tid)
 def torch(x,y,z=0):thing(46,x,y,z);light(x,y,z+64,(255,176,72),112)
 def pillar(x,y,w=96,h=256,theme='B',tex='QMET01'):
  rect(x-12,y-12,w+24,w+24,None,heightfloor=8 if theme!='D' else 136,texturefloor='METALF09',wall='QMET01')
  rect(x,y,w,w,None,heightfloor=h,texturefloor='METALF09',wall=tex,lightlevel=144)
 def stairs(x,y,w,length,start,end,n=8,axis='y'):
  for i in range(n):
   xx,yy=(x,y+length*i/n) if axis=='y' else (x+length*i/n,y)
   ww,ll=(w,length/n) if axis=='y' else (length/n,w)
   rect(xx,yy,ww,ll,None,heightfloor=start+(end-start)*(i+1)/n,texturefloor='METALF09',wall='QMET01',lightlevel=176)
 def door(x,y,w,h,tag,floor=0,script=12,arg=None,texture='QDOOR9'):
  rect(x,y,w,h,None,heightfloor=floor,heightceiling=floor,id=tag,textureceiling='METALF09',texturefloor='METALF09',lightlevel=160,wall=texture,door=tag,zone='door')
  actions.append(dict(door=tag,script=script,arg=tag if arg is None else arg))
 def monster(typ,x,y,group=0,rank=0,angle=270):
  props=dict(angle=angle,skill1=rank<2,skill2=rank<2,skill3=rank<3)
  if group:props.update(id=group,dormant=True)
  t=thing(typ,x,y,**props);monsters.append(t)
 approach=hall([(400,320),(576,576),(864,864),(1216,864),(1600,1248)],224,texturefloor='GRAVE02',heightceiling=512,textureceiling='F_SKY1')
 hall([(1488,1648),(1248,1648),(704,1856),(704,2240)],224)
 hall([(1088,2752),(1280,2752),(1280,2112),(1568,2112)],192)
 hall([(928,3488),(928,3968)],192,heightfloor=128,heightceiling=384)
 hall([(2688,1904),(3008,1904),(3008,2912),(3296,2912)],224)
 hall([(2704,1456),(3344,1456)],192)
 hall([(4032,2016),(4032,2688)],224)
 hall([(2112,2144),(2112,4736)],256,heightceiling=384)
 hall([(2240,5776),(2240,6160)],256,heightceiling=320)
 room('A',Polygon([(160,256),(784,192),(1136,512),(1056,880),(784,1136),(352,1056),(80,688)]))
 room('B',Polygon([(1456,1248),(1600,1104),(2608,1104),(2752,1248),(2752,2048),(2608,2208),(1600,2208),(1456,2048)]))
 room('C',box(0,2208,1120,3552));room('D',box(400,3904,1456,4656))
 room('E',box(3264,2608,4768,4000));room('F',box(3312,1152,4560,2064))
 room('G',Polygon([(1600,4656),(2896,4656),(3056,4816),(3056,5696),(2896,5856),(1600,5856),(1456,5696),(1456,4816)]))
 room('H',box(1904,6096,2512,6464))
 area(approach,None,heightfloor=0,texturefloor='GRAVE02',wall='QMET01')
 for ya,yb,h in [(192,384,-64),(384,480,-48),(480,576,-32),(576,672,-16)]:
  part=approach.intersection(box(-100,ya,1700,yb))
  if not part.is_empty:area(part,None,heightfloor=h)
 for x,y,r,h in [(220,800,150,32),(360,1032,126,72),(1010,460,105,24),(1000,1010,135,64),(124,464,92,-16)]:
  area(octagon(x,y,r).intersection(rooms['A']),None,heightfloor=h,texturefloor='QGRASS',wall='QROCK3')
  if r>110:area(octagon(x,y,r*.60).intersection(rooms['A']),None,heightfloor=h+32,texturefloor='QGRASS',wall='QROCK3')
 thing(54,360,992);thing(54,1000,900);torch(1120,896)
 area(approach.intersection(box(1248,850,1424,1136)),None,heightceiling=224,textureceiling='WOODF1',wall='QMET01',lightlevel=192)
 area(rooms['B'].difference(rooms['B'].buffer(-48)),None,texturefloor='METALF09',wall='QMET01',lightlevel=152)
 rect(1952,1536,288,288,None,heightfloor=16,texturefloor='QFLAT09',wall='QMET01')
 rect(2016,1600,160,160,None,heightfloor=80,texturefloor='METALF24',wall='QWIZ')
 for x in (1584,2496):
  for y in (1280,1920):pillar(x,y,112,288,'B','QBRICK6');torch(x-32,y+56)
 # Reading pit, accessible upper gallery, and a real bridge overhead.
 rect(320,2592,480,576,None,heightfloor=-64,texturefloor='QFLAT09',wall='QMET01',lightlevel=144)
 stairs(480,2464,160,128,0,-64,4);stairs(480,3168,160,128,-64,0,4)
 for x in (16,1024):
  for y in range(2288,3489,192):
   if x==1024 and y==2672:continue
   rect(x,y,80,144,None,heightfloor=160,texturefloor='WOODF1',wall='PANBOOK',lightlevel=144)
 stairs(176,2400,192,384,0,128,8);rect(176,2784,224,320,None,heightfloor=128,texturefloor='WOODF1',wall='QMET01')
 rect(864,2896,144,656,None,heightfloor=128,texturefloor='WOODF1',wall='PANBOOK')
 rect(832,3472,192,96,None,heightfloor=128,texturefloor='WOODF1',wall='QMET01')
 rect(400,2912,464,160,None,id=801,bridge=True,lightlevel=128)
 for x in (192,832):
  for y in (2304,3168,3392):pillar(x,y,64,352,'C','QBRICK6')
 for y in (2384,2800,3264,3472):rect(0,y,1120,32,None,heightceiling=304,textureceiling='WOODF1',lightlevel=144)
 for x in (96,960):
  for y in (2448,2832,3216):light(x,y,240,(255,191,96),140)
 rect(480,2208,160,96,None,textureceiling='F_SKY1',heightceiling=512)
 for x,y in [(352,2688),(672,2688),(352,3104),(672,3104)]:rect(x,y,96,48,None,heightfloor=-24,texturefloor='WOODF1',wall='QWOOD1')

 # Crypt altar and ribbed ceiling.
 for x in (432,1248):
  for y in (3984,4208,4432):
   rect(x,y,144,144,None,heightfloor=160,texturefloor='QFLAT09',wall='QCHURCH');torch(x+72,y+72,32)
 rect(800,4160,240,240,None,heightfloor=144,texturefloor='QFLAT09',wall='QMET13')
 for y in (4000,4304,4576):rect(400,y,1056,32,None,heightceiling=336,textureceiling='QMET13')
 for x,y in [(704,4000),(1120,4512)]:light(x,y,176,(255,157,80),152)
 # Reactor: layered octagonal base, green core and three mechanical pistons.
 area(octagon(4000,3264,320),None,heightfloor=16,texturefloor='METALF09',wall='QMET01')
 area(octagon(4000,3264,288),None,heightfloor=32,texturefloor='METALF24',wall='QMET13')
 area(octagon(4000,3264,112),None,heightfloor=272,texturefloor='NUKAGE1',wall='SFALL1',lightlevel=240,id=802,lightcolor=0xa3ff96)
 for a in (30,150,270):
  x=4000+184*math.cos(math.radians(a));y=3264+184*math.sin(math.radians(a))
  area(octagon(x,y,48),None,heightfloor=288,texturefloor='METALF09',wall='QMET13',lightlevel=176)
 for x in (3408,4496):
  for y in (2720,3744):pillar(x,y,128,416,'E','QMET01')
 rect(4512,3024,192,464,None,heightfloor=96,texturefloor='METALF09',wall='QMET13')
 stairs(4512,2736,192,288,0,96,6)
 for x in (3552,4320):rect(x,2896,80,640,None,heightfloor=-16,texturefloor='METALF09',wall='QMET01')
 for y in (2768,3120,3616,3872):rect(3264,y,1504,24,None,heightceiling=352,textureceiling='METALF09',lightlevel=184)
 for x in (3488,4512):
  for y in (2800,3648):light(x,y,256,(220,232,220),160)
 for a in (0,120,240):light(4000+220*math.cos(math.radians(a)),3264+220*math.sin(math.radians(a)),160,(112,255,112),128,4500)
 rect(4576,3376,80,48,None,heightfloor=144,texturefloor='METALF09',wall='SW1BRCOM',id=900,console=2)
 # Upper return bridge physically crosses the lower north passage.
 bridge=hall([(3360,3936),(3360,4112),(3008,4208),(1424,4208)],192,heightfloor=160,heightceiling=416,texturefloor='WOODF1',wall='QMET13')
 area(bridge.intersection(box(1984,4064,2240,4336)),None,heightfloor=0,id=800,bridge=True,texturefloor='METALF09')
 for yy in (4112,4288):rect(1984,yy,256,16,None,id=803,moreids='800')
 stairs(3264,3552,192,384,0,160,10);stairs(1376,4112,192,128,128,160,2,axis='x')
 # Optional drainage loop, with walking-height steps at both entrances.
 rect(3440,1536,992,160,None,heightfloor=-48,texturefloor='FWATER1',wall='QMET13',lightlevel=128)
 for x in (3520,3808,4096):rect(x,1504,144,224,None,heightfloor=-32,texturefloor='METALF09',wall='QMET01')
 stairs(3280,1360,192,128,0,-32,2,axis='x');stairs(3920,1936,224,128,-32,0,2)
 for x in (3424,4416):light(x,1856,96,(120,190,168),136)
 # Final arena: recessed seal, two stairs and a continuous outer combat loop.
 area(octagon(2256,5264,368),None,heightfloor=-48,texturefloor='QFLAT09',wall='QMET13',lightlevel=176)
 area(octagon(2256,5264,240),None,heightfloor=-48,texturefloor='QFLAT06',lightlevel=216)
 stairs(2144,4832,224,112,0,-48,3);stairs(2144,5616,224,112,-48,0,3)
 for x in (1712,2672):
  for y in (4896,5488):pillar(x,y,128,256,'G','QWIZ');torch(x-32,y+64)
 for x in (1456,2912):
  for y in (5072,5488):rect(x,y,144,224,None,heightfloor=64,texturefloor='QGRASS',wall='QROCK3')
 stairs(2112,5728,256,192,0,64,4);rect(2112,5920,256,192,None,heightfloor=64,texturefloor='QFLAT06')
 for x in (1952,2480):light(x,6264,160,(255,175,72),128)
 # Reinforcement closets are real rooms behind moving walls.
 closets={}
 def closet(name,x,y,w,h,theme,edge,tag):
  rect(x,y,w,h,theme,heightceiling=224)
  if edge=='east':door(x+w-24,y,24,h,tag,arg=0,texture='PANCASE2' if theme=='C' else 'QMET13')
  else:door(x,y,24,h,tag,arg=0,texture='PANCASE2' if theme=='C' else 'QMET13')
  closets[name]=(x+64,y+64,x+w-64,y+h-64)
 closet('C1',-256,2432,280,256,'C','east',111);closet('C2',-256,2816,280,256,'C','east',111)
 closet('C3',1096,3072,280,224,'C','west',111);closet('C4',1096,3328,280,224,'C','west',111)
 closet('E1',4744,2832,344,288,'E','west',112);closet('E2',4744,3504,344,288,'E','west',112)
 closet('B1',1176,1280,304,256,'B','east',114);closet('B2',2728,1168,304,240,'B','west',114)
 for n,x,y,e in [('G1',1168,4864,'east'),('G2',1168,5360,'east'),('G3',3032,4864,'west'),('G4',3032,5360,'west')]:
  closet(n,x,y,312,304,'G',e,113)
 # Wall ribs, altar windows and ceiling fixtures give each area a distinct rhythm.
 for x in (512,736,960):
  rect(x,4632,144,24,None,heightfloor=384,wall='QWINDOW1',texturefloor='METALF09')
  light(x+72,4576,192,(255,152,80),128)
 for y in (2384,2800,3264,3472):
  rect(480,y,160,32,None,textureceiling='CEIL1_2',lightlevel=192)
  light(560,y+16,272,(255,196,112),160)
 for y in (2800,3200,3600):
  for x in (3264,4744):
   if x==3264 and y==2800:continue
   rect(x,y,24,144,None,heightfloor=416,wall='QMET13',texturefloor='METALF09')
 for x in (1888,2352):
  rect(x,5832,192,24,None,heightfloor=384,wall='QCARCH1',texturefloor='QFLAT06')
  light(x+96,5784,192,(255,160,72),144)
 # Three secrets contain optional supplies, never progression requirements.
 rect(-352,3248,352,224,'C',lightlevel=192);door(-24,3248,24,224,108,texture='PANCASE2')
 rect(4536,1776,304,224,'F',lightlevel=184);door(4536,1776,24,224,109,floor=-32,texture='QMET13')
 area(box(80,1088,304,1296),'A',heightfloor=-32,heightceiling=512)
 hall([(256,1008),(208,1200)],160,heightfloor=-32,heightceiling=512,textureceiling='F_SKY1',texturefloor='QGRASS',wall='QROCK3')
 stairs(176,1008,128,96,-64,-32,2)
 for k,(x,y) in enumerate([(-240,3328),(4656,1840),(160,1168)]):rect(x,y,64,64,None,special=1024,secret=k)
 # Colored lamps identify the two progression locks and reactor console.
 light(3008,1984,112,(72,120,255),112);light(2112,2256,112,(255,64,40),112)
 light(4592,3312,208,(96,224,128),96)
 # Gate strips span their entire corridors. Script-only doors cannot be used early.
 door(2896,2032,224,32,101,script=9,arg=0)
 door(1984,2320,256,32,102,script=5,arg=0)
 door(3264,3536,192,32,103,script=10,arg=0)
 door(3920,2256,224,32,104,script=10,arg=0)
 door(3008,1360,32,192,105,script=10,arg=0)
 door(832,3712,192,32,106,floor=128,script=12,arg=0)
 door(1184,2632,192,32,107,script=12,arg=0,texture='PANCASE2')
 door(1984,4512,256,32,115,script=15,arg=0)
 thing(14,2112,4768,id=4601,angle=90)
 rect(1984,4512,256,32,None,heightceiling=384)
 door(2112,6016,256,32,116,floor=64,script=12,arg=0)

 # Skill ranks: 0/1 all, 2 HMP+, 3 UV+. Delayed groups remain in their closets.
 for i,(x,y) in enumerate([(304,736),(400,960),(992,736),(1024,944),(848,416),(192,544)]):monster(3001,x,y,rank=2 if i==5 else 0)
 for i,(x,y) in enumerate([(736,1056),(832,1008),(928,480),(608,960)]):monster([3002,3001,9,3001][i],x,y,3001,3 if i==3 else 0)
 for i,(x,y) in enumerate([(1760,1456),(2416,1456),(1696,1824),(2448,1824),(2288,2048),(1808,2048),(2352,1216),(1744,1248),(1856,1600),(2384,1664)]):
  monster([9,3001,3001,9,66,3002,3004,3004,3001,3001][i],x,y,rank=3 if i in (5,9) else 0)
 for i,(x,y) in enumerate([(448,2368),(736,2416),(288,3264),(752,3360),(512,3424),(704,2816),(480,3008),(944,3184)]):
  monster([3001,9,3001,9,3100,3002,66,3001][i],x,y,rank=2 if i in (3,7) else 0)
 for i,(x,y) in enumerate([(640,4016),(1120,4000),(656,4528),(1136,4528),(608,4288),(1200,4336),(704,4368),(1072,4208),(752,4112),(1104,4096),(832,4464),(1056,4496),(640,4160),(1184,4432)]):
  monster([3117,3001,3002,3109,3001,66,9,3001,3002,3117,3001,3001,3004,3004][i],x,y,3007,3 if i in (3,9,13) else 0)
 for i,(x,y) in enumerate([(3648,2848),(4448,2880),(3504,3584),(4432,3600),(3744,3808),(4256,3808),(3504,3168),(4464,3200),(3696,2752),(4224,2752),(3696,3472),(4272,3440),(3504,3920),(4656,3760),(3792,3920),(4336,3936)]):
  monster([67,65,9,65,3100,3001,3002,3001,9,3001,3001,3001,3004,3004,3001,3001][i],x,y,rank=3 if i in (7,11,13,15) else 0)
 for i,(x,y) in enumerate([(3504,1264),(4352,1264),(3600,1904),(4240,1904),(3840,1280),(4016,1840),(3392,1760),(4416,1760)]):
  monster([3001,3002,9,3001,3004,3001,3002,3001][i],x,y,3008,2 if i in (4,7) else 0)
 for i,(x,y) in enumerate([(1920,5552),(2608,5552),(1536,5568),(2976,5568),(1872,4800),(2640,4800),(1856,5744),(2720,5744)]):
  monster([22250,22250,66,66,3001,3001,3001,3001][i],x,y,3005,2 if i in (1,3) else 0)
 def fill(names,types,count,group):
  grouped=[]
  for n in names:
   x0,y0,x1,y1=closets[n]
   grouped.append([(x,y) for y in range(int(y0),int(y1)+1,96) for x in range(int(x0),int(x1)+1,96)])
  spots=[v[i] for i in range(max(map(len,grouped))) for v in grouped if i<len(v)]
  assert len(spots)>=count
  for i,(x,y) in enumerate(spots[:count]):monster(types[i%len(types)],x,y,group,3 if i%5==4 else 2 if i%5==3 else 0)
 fill(['C1','C2','C3','C4'],[3001,3002,9,3100],14,3002)
 fill(['E1','E2'],[9,3001,3002,3100],10,3003)
 fill(['B1','B2'],[3001,9,3002],8,3004)
 fill(['G1','G2','G3','G4'],[3001,69,3001,3002],14,3006)
 assert len(monsters)==120,len(monsters)
 # Weapon progression and key pickups are actual gameplay triggers.
 thing(82,880,864,special=80,arg0=11);thing(2002,736,2336)
 thing(2003,3344,2832);thing(2004,704,4048)
 thing(40,944,3376,special=80,arg0=1);thing(38,928,4288,special=80,arg0=3)
 thing(2018,2096,1872);thing(2019,1040,4064)
 thing(2013,-224,3360);thing(8,4736,1888);thing(2046,176,1216)
 for x,y in [(784,832),(944,864),(1712,1552),(2416,1552),(672,2304),(752,2528),(448,3376),(976,3440),(720,4016),(1120,4096),(3456,2672),(4336,2688),(3520,3680),(4448,3824),(3408,1296),(4368,1904),(1856,4816),(2624,4816)]:thing(2049,x,y)
 for x,y in [(928,896),(2048,1936),(768,2320),(272,3376),(752,4064),(3376,2864),(4464,2672),(1824,4784)]:thing(2048,x,y)
 for x,y in [(3376,2768),(3568,2736),(4528,3504),(4320,3904),(736,4496),(1072,4000),(1824,4800),(1888,4800),(2608,4800),(2672,4800)]:thing(2046,x,y)
 for x,y in [(736,4048),(784,4016),(1088,4576),(2080,4448),(2160,4448),(1936,4800),(2544,4800)]:thing(17,x,y)
 for x,y in [(704,832),(1808,1360),(2336,1968),(576,2272),(768,3408),(624,4480),(1120,4032),(3408,2672),(4432,3904),(3600,1984),(1888,4832),(2656,4832)]:thing(2012,x,y)
 for x,y in [(768,896),(1664,1168),(2544,2128),(288,2448),(736,3328),(608,4560),(1216,3952),(3344,3936),(4672,2704),(3424,1952),(2944,5728)]:thing(10,x,y)
 for x,y in [(1824,2112),(2512,1200),(448,2448),(816,3472),(448,4560),(1376,4576),(3312,3200),(4704,3360),(1664,5760),(2848,5760)]:torch(x,y)
 for i,(x,y) in enumerate([(384,304),(464,304),(544,304),(384,384),(464,384),(544,384),(384,464),(464,464)]):
  thing([1,2,3,4,4001,4002,4003,4004][i],x,y,angle=45)

 # Polygon arrangement nodes every geometric intersection into shared boundaries.
 boundaries=unary_union([g.boundary for g,_ in regions]);faces=list(polygonize(boundaries))
 tree=STRtree([g for g,_ in regions]);sectors=[];polys=[]
 for face in faces:
  q=face.representative_point();props={}
  for idx in sorted(tree.query(q)):
   geom,fields=regions[idx]
   if geom.covers(q):props.update(fields)
  if 'heightceiling' not in props:continue
  if props['heightceiling']<props['heightfloor']:props['heightceiling']=props['heightfloor']
  sectors.append(props);polys.append(face)
 for k in range(3):
  ids=[i for i,s in enumerate(sectors) if s.get('secret')==k]
  keep=max(ids,key=lambda i:polys[i].area)
  for i in ids:
   if i!=keep:sectors[i].pop('special')
 # One moving sector per door tag: split overlay faces must not obstruct each other.
 face_to_sector=[];joined={};unified=[]
 for i,s in enumerate(sectors):
  key=('door',s['door']) if s.get('door') else ('face',i)
  if key not in joined:joined[key]=len(unified);unified.append(s)
  face_to_sector.append(joined[key])
 sectors=unified
 vertices=[];vid={};sides=[];lines=[];edges=collections.defaultdict(list)
 def vertex(p):
  p=tuple(round(n,5) for n in p)
  if p not in vid:vid[p]=len(vertices);vertices.append(dict(x=p[0],y=p[1]))
  return vid[p]
 for fi,face in enumerate(polys):
  si=face_to_sector[fi]
  face=orient(face,sign=-1)
  for ring in [face.exterior,*face.interiors]:
   pts=list(ring.coords)
   for a,b in zip(pts,pts[1:]):
    va,vb=vertex(a),vertex(b)
    if va!=vb:edges[tuple(sorted((va,vb)))].append((va,vb,si))
 def side(si,solid,neighbor=None):
  s=sectors[si];i=len(sides)
  sides.append(dict(sector=si,texturemiddle=s.get('wall','QBRICK6') if solid else '-',texturetop=s.get('wall','QBRICK6'),texturebottom=s.get('wall','QBRICK6')))
  if neighbor is not None:
   adjacent=sectors[neighbor]
   if adjacent['heightfloor']>s['heightfloor']:sides[i]['texturebottom']=adjacent.get('wall','QBRICK6')
   if adjacent['heightceiling']<s['heightceiling']:sides[i]['texturetop']=adjacent.get('wall','QBRICK6')
  return i
 action_by_door={a['door']:a for a in actions}
 for key,records in edges.items():
  # Polygonization may leave a zero-width spike traversed both ways by one face.
  counts=collections.Counter(records)
  for a,b,si in list(counts):
   n=min(counts[(a,b,si)],counts[(b,a,si)])
   counts[(a,b,si)]-=n;counts[(b,a,si)]-=n
  records=list(counts.elements())
  if not records:continue
  assert len(records)<=2,(key,records)
  a,b,si=records[0];l=dict(v1=a,v2=b,sidefront=side(si,len(records)==1,records[1][2] if len(records)==2 else None))
  if len(records)==2:
   sj=records[1][2];l.update(sideback=side(sj,False,si),twosided=True)
   for sidx in (si,sj):
    sec=sectors[sidx]
    if sec.get('door') and sectors[si].get('door')!=sectors[sj].get('door'):
     act=action_by_door[sec['door']]
     if act['arg']!=0 or act['script']!=12:l.update(special=80,arg0=act['script'],arg2=act['arg'],playeruse=True,repeatspecial=True)
    if sec.get('console'):l.update(special=80,arg0=sec['console'],playeruse=True,repeatspecial=True)
   v,w=vertices[a],vertices[b]
   if sectors[si].get('zone')!=sectors[sj].get('zone') and 'G' in (sectors[si].get('zone'),sectors[sj].get('zone')):
    if 1960<(v['x']+w['x'])/2<2260 and 4600<(v['y']+w['y'])/2<4700:l.update(special=80,arg0=6,playercross=True,repeatspecial=True)
   if 'H' in (sectors[si].get('zone'),sectors[sj].get('zone')) and sectors[si].get('zone')!=sectors[sj].get('zone'):
    l.update(special=80,arg0=7,playercross=True,repeatspecial=True)
  else:l['blocking']=True
  lines.append(l)
 def control(tag,bottom,top,floor='WOODF1'):
  si=len(sectors);sectors.append(dict(heightfloor=bottom,heightceiling=top,texturefloor=floor,textureceiling=floor,lightlevel=144))
  x=6000+tag%10*128;y=0
  vv=[vertex((x,y)),vertex((x,y+64)),vertex((x+64,y+64)),vertex((x+64,y))]
  for i in range(4):
   line=dict(v1=vv[i],v2=vv[(i+1)%4],sidefront=side(si,True),blocking=True)
   if i==0:line.update(special=160,arg0=tag,arg1=1,arg3=255)
   lines.append(line)
 control(800,128,160);control(801,112,128);control(803,160,224)
 ptree=STRtree(polys)
 def locate(x,y):
  pt=Point(x,y);found=[int(i) for i in ptree.query(pt) if polys[i].covers(pt)]
  return face_to_sector[min(found)] if found else -1
 bad=[]
 for i,t in enumerate(things):
  si=locate(t['x'],t['y'])
  if si<0:bad.append((i,t['type'],t['x'],t['y'],'outside'));continue
  s=sectors[si]
  if t in monsters and s['heightceiling']-s['heightfloor']<64:bad.append((i,t['type'],t['x'],t['y'],'closed'))
 for t in things:
  si=locate(t['x'],t['y'])
  if si>=0 and sectors[si].get('id') in (800,801):
   top=160 if sectors[si]['id']==800 else 128
   if t['type'] in (66,40):t['height']=top-sectors[si]['heightfloor']
 if bad:raise ValueError('Invalid thing placement: '+str(bad))
 def block(kind,fields):
  return kind+' { '+''.join(k+'='+json.dumps(v,separators=(',',':'))+';' for k,v in fields.items())+' }\n'
 clean=[{k:v for k,v in s.items() if k not in ('wall','zone','door','console','bridge','secret')} for s in sectors]
 text='namespace="ZDoom";\n'+''.join(block(kind,s) for kind,objs in [('vertex',vertices),('sector',clean),('sidedef',sides),('linedef',lines),('thing',things)] for s in objs)
 source=(ROOT/'tools/map-sources/tnt01gpt.acs').read_text(encoding='utf-8-sig').encode()
 acs=WORK/'tnt01gpt.acs';obj=WORK/'tnt01gpt.o';acs.write_bytes(source)
 p=subprocess.run([str(acc),'-i',str(acc.parent),str(acs),str(obj)],capture_output=True)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace'))
 raw=WORK/'tnt01gpt-unnoded.wad'
 raw.write_bytes(write_wad(b'PWAD',[(b'TNT01GPT',b''),(b'TEXTMAP',text.encode()),(b'BEHAVIOR',obj.read_bytes()),(b'SCRIPTS',source),(b'ENDMAP',b'')]))
 built=WORK/'tnt01gpt-noded.wad'
 p=subprocess.run([str(zdbsp),'-X','-o',str(built),str(raw)],capture_output=True)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace'))
 output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(built.read_bytes())
 summary=dict(map='TNT01GPT',sectors=len(sectors),linedefs=len(lines),vertices=len(vertices),things=len(things),monsters_uv=len(monsters),monsters_hmp=sum(t['skill3'] for t in monsters),monsters_easy=sum(t['skill1'] for t in monsters),secrets=sum(s.get('special')==1024 for s in sectors),sha256=hashlib.sha256(output.read_bytes()).hexdigest(),doors={str(s['door']):i for i,s in enumerate(sectors) if s.get('door')})
 (WORK/'geometry.json').write_text(json.dumps(summary,indent=2))
 (WORK/'TEXTMAP.txt').write_text(text)
 (WORK/'sectors.json').write_text(json.dumps([dict(index=i,**s) for i,s in enumerate(sectors)]))
 print(json.dumps(summary,indent=2));return summary
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--acc',type=Path,default=Path('F:/DoomDev/Tools/UltimateDoombuilder/Compilers/ZDoom/acc.exe'))
 p.add_argument('--zdbsp',type=Path,default=Path('F:/DoomDev/Tools/UltimateDoombuilder/Compilers/Nodebuilders/zdbsp.exe'))
 p.add_argument('--output',type=Path,default=ROOT/'tutnt/maps/tnt01gpt.wad')
 p.add_argument('--check',action='store_true',help='Rebuild in the work directory and compare the shipped WAD')
 a=p.parse_args()
 if a.check:
  expected=a.output.read_bytes();candidate=WORK/'tnt01gpt-check.wad'
  build(a.acc,a.zdbsp,candidate)
  if candidate.read_bytes()!=expected:raise SystemExit('TNT01GPT WAD is stale; rebuild it.')
  print('TNT01GPT reproducibility: PASS')
 else:build(a.acc,a.zdbsp,a.output)
