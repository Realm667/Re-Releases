"""Native UZDoom A/B brightmap galleries; generated test content stays in .codex."""
from pathlib import Path
import argparse,json,math,re,zipfile
import numpy as np
from PIL import Image
from build_utnt import write_wad
from build_custom_brightmaps import ROOT,OUT,MODULE,png
from check_engine import run_case

GROUPS=[
 [('DRKI','A'),('SLHV','A'),('HWAR','A')],
 [('APYT','A'),('RSPI','A'),('CYCL','A')],
 [('TROX','A'),('HFRY','A'),('TRO2','A')],
 [('PLEM','A'),('TORT','A'),('MNTR','A')],
 [('ENCD','B'),('REGN','A'),('PHRT','A')],
 [('APYT','G'),('APYT','H'),('APYT','I')],
 [('HWAR','F'),('SLHV','H'),('DRKI','G')],
 [('IKLITF01',),('IKLITF07',),('TLITE6_1',)],
 [('QRUNT62',),('QRUNT63',),('TELETOP',)],
 [('COMPBLUE',),('COMPRED',),('XA40TEX',)],
 [('SW1NEW1',),('SW2NEW1',),('TLITE6_5',)],
 [('SW1NEW3',),('SW2NEW3',),('XB40TEX',)],
 [('TORT','K'),('PLEM','K'),('MNTR','K')],
]
SETTINGS=[('vid_activeinbackground','true'),('i_pauseinbackground','false'),('use_mouse','false'),('use_joystick','false'),('r_drawplayersprites','false'),('con_notifytime',0),('gl_texture_filter',0),('cl_capfps','true'),('vid_maxfps',60),('UTNT_reducedfx','true'),('UTNT_tonalfilter','false'),('UTNT_distanceblur','false'),('UTNT_shaderoverlayswitch','false'),('gl_bloom','false'),('gl_lights','false'),('crosshair',0),('screenblocks',12),('fov',80)]

def fixture(z,groups):
 decorate=[];nums=[];maps=[];heart_class=None
 for gi in groups:
  entries=GROUPS[gi];verts=[(-256,-300),(-256,128),(-192,128),(-64,128),(64,128),(192,128),(256,128),(256,-300)]
  text=['namespace="ZDoom";']+[f'vertex {{x={x};y={y};}}' for x,y in verts]
  text.append('sector {heightfloor=0;heightceiling=192;texturefloor="FLOOR0_1";textureceiling="CEIL5_2";lightlevel=96;}')
  for i in range(len(verts)):
   tex=entries[i-2][0] if len(entries[0])==1 and 2<=i<=4 else 'STARTAN3'
   text.append(f'sidedef {{sector=0;texturemiddle="{tex}";}}')
   text.append(f'linedef {{v1={i};v2={(i+1)%len(verts)};sidefront={i};blocking=true;}}')
  text.append('thing {x=0;y=-180;angle=90;type=1;skill1=true;skill2=true;skill3=true;skill4=true;skill5=true;single=true;}')
  if len(entries[0])==2:
   for j,(prefix,frame) in enumerate(entries):
    name=f'BMC{gi}_{j}';ident=31500+gi*3+j;x=(j-1)*128;angle=round(math.degrees(math.atan2(-190,-x)))%360
    # Original sprite resources, frozen for exact A/B comparison; actor logic is
    # deliberately absent so RNG, attacks, death effects and bob cannot differ.
    decorate.append(f'actor {name} {{ +NOGRAVITY Radius 1 Height 1 Scale {0.55 if gi==5 else 0.8} States {{ Spawn:\n {prefix} {frame} -1\n Stop\n }} }}')
    nums.append(f'{ident}={name}');text.append(f'thing {{x={x};y=10;height=24;angle={angle};type={ident};skill1=true;skill2=true;skill3=true;skill4=true;skill5=true;single=true;}}')
    if prefix=='PHRT':heart_class=name
  wad=write_wad(b'PWAD',[(b'MAP01',b''),(b'TEXTMAP','\n'.join(text).encode()),(b'ENDMAP',b'')]);z.writestr(f'maps/BM{gi:02}.wad',wad)
  maps.append(f'map BM{gi:02} "Brightmap validation {gi}" {{ nointermission }}')
 z.writestr('MAPINFO','GameInfo { AddEventHandlers = "BMCTestCamera" }\n'+'\n'.join(maps)+'\nDoomEdNums {\n'+'\n'.join(nums)+'\n}')
 z.writestr('ZSCRIPT', '\n'.join(['version "5.0.0"', 'class BMCTestCamera : EventHandler {', 'Actor Cam;', 'override void NetworkProcess(ConsoleEvent e) { if(e.Name=="bmview") {', "if(!Cam)Cam=Actor.Spawn('MapSpot',(0,-180,41));", 'Cam.SetOrigin((0,-180,41),false);Cam.Angle=90;Cam.Pitch=0;players[0].camera=Cam;', 'let it=ThinkerIterator.Create("Actor");Actor a;while(a=Actor(it.Next())){String n=a.GetClassName();if(n.Left(3)=="BMC")Console.Printf("BMC %s pos %f %f %f sprite %d frame %d alpha %f",n,a.Pos.X,a.Pos.Y,a.Pos.Z,a.Sprite,a.Frame,a.Alpha);}', '}}', 'override void WorldTick(){if(Cam)players[0].camera=Cam;}', '}']))
 z.writestr('DECORATE','\n'.join(decorate));return heart_class

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mode',choices=['on','off','base'],default='on');p.add_argument('--overlay',action='store_true');p.add_argument('--groups',type=int,nargs='+',default=list(range(len(GROUPS))));p.add_argument('--renderer',default='1');p.add_argument('--compare',action='store_true');a=p.parse_args()
 c=ROOT/'tutnt/.codex';w=c/'work/brightmap-rollout/runtime';w.mkdir(parents=True,exist_ok=True);v=c/'validation/brightmap-rollout';v.mkdir(parents=True,exist_ok=True)
 if a.compare:
  results=[]
  for gi in a.groups:
   off=np.array(Image.open(v/f'brightmaps-off-{a.renderer}-{gi:02}.png').convert('RGB'))
   on=np.array(Image.open(v/f'brightmaps-on-{a.renderer}-{gi:02}.png').convert('RGB'))
   delta=np.any(off!=on,axis=2)
   counts=[int(delta[40:360,left:right].sum()) for left,right in ((80,360),(360,600),(600,880))]
   expected=[entry[0] not in ('SW1NEW1','SW1NEW3') for entry in GROUPS[gi]]
   ok=all((count>0)==emit for count,emit in zip(counts,expected))
   results.append({'group':gi,'subjects':GROUPS[gi],'changed_pixels_by_subject':counts,'ok':ok})
  (v/f'comparison-{a.renderer}.json').write_text(json.dumps(results,indent=2))
  print(json.dumps(results,indent=2));raise SystemExit(0 if all(r['ok'] for r in results) else 1)
 if not (w/'logs').exists() or not (w/'logs').resolve().is_relative_to((c/'logs').resolve()):raise ValueError('Create the central log junction first')
 manifest=json.loads((ROOT/'tools/artwork/brightmaps/custom-manifest.json').read_text());label='brightmaps-'+a.mode+'-'+a.renderer;addon=c/'builds'/(label+'.pk3');mod=ROOT/'tutnt'
 with zipfile.ZipFile(addon,'w',zipfile.ZIP_DEFLATED) as z:
  heart=fixture(z,a.groups)
  if a.overlay and a.mode!='base':
   for rel in manifest['outputs']:
    if rel.startswith(('materials/','voxels/','sprites/')):z.write(mod/rel,rel)
   z.write(mod/'shaders/portal.gldefs','shaders/portal.gldefs')
   z.writestr('GLDEFS.new',re.sub(r'\bthiswad\b','',(mod/MODULE).read_text()))
  if a.mode=='off':
   lines=[]
   for i,r in enumerate(manifest['bindings']):
    if r['status']!='mapped':continue
    rel=f'black/m{i}.png';z.writestr(rel,png(Image.new('RGB',r['size'])));lines.append(f'brightmap {r["kind"]} {r["target"]} {{ map "{rel}" }}')
   z.writestr('GLDEFS.off','\n'.join(lines))
  includes=[]
  if a.overlay and a.mode!='base':includes.append('#include "GLDEFS.new"')
  if a.mode=='off':includes.append('#include "GLDEFS.off"')
  if includes:z.writestr('GLDEFS', '\n'.join(includes))
  if heart and a.mode!='base':
   model=(mod/'modeldef/MODELDEF.brightmaps-custom').read_text().replace('PortalCoreHeart',heart)
   z.writestr('MODELDEF',model)
  elif heart and a.mode=='base':
   # Base mode is intended for overlay runs against the previous shared PK3.
   pass
 result=run_case('F:/DoomDev/uzdoom.exe','F:/DoomDev/DOOM2.WAD',root=w,mod=ROOT/'tutnt.pk3',addon=addon,label=label+'-compile')
 if not result['ok']:raise RuntimeError(Path(result['log']).read_text()[-5000:])
 commands=['vid_setsize 960 540']
 for i,gi in enumerate(a.groups):
  if i:commands.append(f'map BM{gi:02}')
  commands+=['wait 210','netevent bmview','screenblocks 12','wait 8',f'screenshot "{(v/f"{label}-{gi:02}.png").as_posix()}"','wait 3']
 commands+=['echo UTNT_TEST_END','wait 3','quit']
 result=run_case('F:/DoomDev/uzdoom.exe','F:/DoomDev/DOOM2.WAD',root=w,mod=ROOT/'tutnt.pk3',addon=addon,mapname=f'BM{a.groups[0]:02}',label=label,renderer=a.renderer,settings=SETTINGS,commands='; '.join(commands),timeout=35+18*len(a.groups))
 log=Path(result['log']).read_text(errors='replace');result['unexpected']=[s for s in log.splitlines() if any(x in s for x in ('Unknown type','Unknown command','model not found','Unable to load','Unrecognized string','Unknown model format','not a valid voxel'))];result['ok']&=not result['unexpected'];result['groups']=a.groups
 expected_actors={f'BMC{gi}_{j}' for gi in a.groups if len(GROUPS[gi][0])==2 for j in range(3)}
 actual_actors=set(re.findall(r'BMC (BMC\d+_\d+) pos',log))
 result['fixture_actors_ok']=actual_actors==expected_actors;result['ok']&=result['fixture_actors_ok']
 (v/(label+'.json')).write_text(json.dumps(result,indent=2));
 if not result['ok']:raise RuntimeError(log[-6000:])
if __name__=='__main__':main()
