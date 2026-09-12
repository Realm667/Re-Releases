"""CRT material/render checks and a reproducible gallery; results live under .codex."""
from pathlib import Path
import argparse,json,struct,zipfile,time
from build_utnt import write_wad,read_wad
from check_engine import run_case
from build_crt_materials import generate
ROOT=Path(__file__).resolve().parents[1];C=ROOT/'tutnt/.codex'
ENGINE=Path('F:/DoomDev/Projects/wolfendoom.dev/#standalone/uzdoom.exe')
def fixture(packaged=False):
 items=json.loads((ROOT/'tools/crt-materials.json').read_text())['screens']
 order=['Q2COMP4','Q2COMP8','OCOMP','QTWALL04','Q2COMP14','Q2RCMP8','Q2FCMP08','Q2COMP10','QPLANET1','EE_ENJ','Q2CMP091','Q2FCMP18']
 names=order+[r['name'] for r in items if r['name'] not in order]
 specs={r['name']:r for r in items};text=['namespace="ZDoom";'];vi=si=li=0
 for room,name in enumerate(names):
  x=room*512;w,h=specs[name]['size']
  # Clockwise polygon; front side is the room interior.
  points=[(x-64,-128),(x-64,128),(x+64,128),(x+64,-128)]
  for px,py in points:text.append(f'vertex {{ x={px}; y={py}; }}')
  floor='Q2FCMP03' if room==6 else 'FLOOR0_1'
  text.append(f'sector {{ heightfloor=0; heightceiling=128; texturefloor="{floor}"; textureceiling="CEIL5_2"; lightlevel=160; }}')
  for edge in range(4):
   tex=name if edge==1 else 'REDWALL' if edge==3 else 'STARTAN3'
   scale=f'scalex_mid={w/128}; scaley_mid={h/128}; offsetx_mid={-w};' if edge==1 else ''
   text.append(f'sidedef {{ sector={room}; texturemiddle="{tex}"; {scale} }}')
   text.append(f'linedef {{ v1={vi+edge}; v2={vi+(edge+1)%4}; sidefront={si}; blocking=true; }}');si+=1
  vi+=4
  if room==0:text.append(f'thing {{ x={x}; y=0; angle=90; type=1; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; coop=true; }}')
  for xx,kind in [(-40,44),(40,45)]:
   text.append(f'thing {{ x={x+xx}; y=-65; angle=90; type={kind}; skill1=true; skill2=true; skill3=true; skill4=true; skill5=true; single=true; coop=true; }}')
 wad=write_wad(b'PWAD',[(b'MAP01',b''),(b'TEXTMAP','\n'.join(text).encode()),(b'ENDMAP',b'')])
 target=C/'builds/crt-gallery.pk3';target.parent.mkdir(exist_ok=True)
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('maps/CRTTEST.wad',wad)
  z.writestr('MAPINFO','map CRTTEST "CRT material validation" { levelnum=230 nointermission }\ngameinfo { AddEventHandlers="CRTFixture" }')
  z.writestr('CVARINFO','user bool crt_debug = false;')
  if not packaged:
   z.writestr('gldefs/GLDEFS.crt',(ROOT/'tutnt/gldefs/GLDEFS.crt').read_bytes())
   z.writestr('shaders/crt/screen.fp',(ROOT/'tutnt/shaders/crt/screen.fp').read_bytes())
   z.writestr('zscript/UTNT_CRT.zc',(ROOT/'tutnt/zscript/UTNT_CRT.zc').read_bytes())
   for bright in (ROOT/'tutnt/materials/crt/brightmaps').glob('*.png'):z.writestr(bright.relative_to(ROOT/'tutnt').as_posix(),bright.read_bytes())
  z.writestr('ZSCRIPT','version "4.14"\n'+(ROOT/'tools/fixtures/crt/fixture.zc').read_text())
 return target,names
def map_capture(a,addon):
 from audit_texture_coverage import parse
 _,lumps=read_wad(ROOT/'tutnt/maps'/(a.mapname.lower()+'.wad'))
 g=parse(next(d for n,d in lumps if n.rstrip(b'\0')==b'TEXTMAP'))
 selected=[]
 for name in ['Q2COMP3','Q2COMP4','OCOMP','Q2COMP8']:
  for i,side in enumerate(g['sidedef']):
   found=False
   for part,key in [(0,'texturetop'),(1,'texturemiddle'),(2,'texturebottom')]:
    if side.get(key,'').strip('"').upper()==name:selected.append((i,part,name));found=True;break
   if found:break
 assert selected,a.mapname
 label=f'crt-map-{a.mapname}-r{a.renderer}'
 cmd='wait 240;screenblocks 12;UTNT_crtmotion false;freeze;'
 captures=[]
 for side,part,name in selected:
  rel=f'logs/{label}-{name}.png';captures.append(rel)
  cmd+=f'netevent crtmap {side} {part};wait 3;netevent crtmap {side} {part};wait 25;screenshot "{rel}";wait 3;'
 if a.mapname=='TNT03A1':
  rel=f'logs/{label}-reported.png';captures.append(rel)
  cmd+=f'netevent crtissue;wait 3;netevent crtissue;wait 25;screenshot "{rel}";wait 3;'
 cmd+='netevent crtassert;echo UTNT_TEST_END;wait 3;quit\n'
 settings=[('cl_capfps',True),('vid_scalemode',5),('vid_scale_customwidth',1280),('vid_scale_customheight',720),('vid_activeinbackground',True),('i_pauseinbackground',False),('use_mouse',False),('r_drawplayersprites',False),('con_notifytime',0),('gl_texture_filter',0)]
 started=time.time()
 r=run_case(ENGINE,Path('F:/DoomDev/DOOM2.WAD'),root=C,mod=a.mod,addon=addon,mapname=a.mapname,renderer=a.renderer,label=label,timeout=80,commands=cmd,settings=settings,quiet=True)
 r['captures']=captures;r['ok']=r['ok'] and r['assertions']==2 and all((C/p).is_file() and (C/p).stat().st_mtime>=started for p in captures)
 if r['ok'] and a.mapname=='TNT03A1':
  import numpy as np
  from PIL import Image
  display=np.asarray(Image.open(C/'logs'/f'{label}-reported.png').convert('RGB'),dtype=float)[180:250,760:890]
  # Track the reported display; its source now falls below the user-requested glow threshold.
  r['q2comp3_signal_luminance']=float((display@np.array([.2126,.7152,.0722])).mean())
 out=C/'validation/crt';out.mkdir(exist_ok=True);(out/(label+'.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
 if not r['ok']:print(Path(r['log']).read_text()[-5000:]);raise SystemExit(1)

def check_glass_alignment():
 # Q2COMP14: derive the dark aperture from source pixels, independently of CRT rectangles.
 import numpy as np
 from PIL import Image
 from build_organic_materials import patch_rgb
 palette=np.frombuffer((ROOT/'tutnt/PLAYPAL.pal').read_bytes()[:768],np.uint8).reshape(256,3)
 source=patch_rgb((ROOT/'tutnt/patches/Q2COMP14.lmp').read_bytes(),palette)
 glass=np.zeros(source.shape[:2],dtype=bool)
 glass[29:53,46:83]=np.all(source[29:53,46:83]==source[40,64],axis=2)
 bright=np.asarray(Image.open(ROOT/'tutnt/materials/crt/brightmaps/q2comp14.png').convert('RGB')).max(axis=2)>0
 assert not np.any(bright & ~glass), 'Q2COMP14 glass treatment spills onto the bezel'
 assert np.count_nonzero(bright & glass)>=.95*np.count_nonzero(glass), 'Q2COMP14 aperture is not covered'

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--renderer',default='1');p.add_argument('--mod',type=Path,default=C/'builds/tutnt-crt-test.pk3');p.add_argument('--batch',type=int,default=0);p.add_argument('--static',action='store_true');p.add_argument('--packaged',action='store_true',help='Test the package itself without current-source overrides');p.add_argument('--map',dest='mapname');a=p.parse_args()
 generate(check=True);check_glass_alignment();addon,names=fixture(a.packaged)
 if a.static:
  print(json.dumps({'ok':True,'materials':len(names),'gallery':str(addon)}));return
 if a.mapname:map_capture(a,addon);return
 label=f'crt-r{a.renderer}-b{a.batch}';cmd='wait 240;screenblocks 12;UTNT_crtmotion false;'
 captures=[]
 selected=range(a.batch*6,min((a.batch+1)*6,len(names)))
 for i in selected:
  for pose in ([0,1] if i in (0,4) else [0,3] if i==6 else [0]):
   suffix=f'{names[i]}-{pose}';rel=f'logs/{label}-{suffix}.png'
   cmd+=f'netevent crtpose {i} {pose};wait 3;netevent crtpose {i} {pose};wait 22;screenshot "{rel}";wait 3;';captures.append(rel)
 if a.batch==0:
  cmd+='netevent crtpose 0 0;wait 3;netevent crtpose 0 0;'
  for mode,setting in [('noreflect','UTNT_crtreflections false'),('off','UTNT_crt false'),('debug','UTNT_crt true;UTNT_crtreflections true;crt_debug true')]:
   rel=f'logs/{label}-{mode}.png';captures.append(rel);cmd+=f'{setting};wait 22;screenshot "{rel}";wait 3;'
  cmd+='crt_debug false;netevent crtback 1;wait 25;screenshot logs/'+label+'-changed-room.png;wait 3;UTNT_reducedfx true;wait 10;netevent crtassert;UTNT_reducedfx false;save crt-test;wait 8;load crt-test;wait 45;netevent crtassert;'
 if a.batch==0:
  cmd+='gl_lights false;UTNT_crtreflections false;'
  for name,light in [('dark',32),('bright',224)]:
   rel=f'logs/{label}-fullbright-{name}.png';captures.append(rel)
   cmd+=f'netevent crtlight {light};wait 15;screenshot "{rel}";wait 3;'
 cmd+='echo UTNT_TEST_END;wait 3;quit\n'
 if a.batch==0:captures.append('logs/'+label+'-changed-room.png')
 started=time.time()
 settings=[('cl_capfps',True),('vid_scalemode',5),('vid_scale_customwidth',1280),('vid_scale_customheight',720),('i_pauseinbackground',False),('vid_activeinbackground',True),('use_mouse',False),('use_joystick',False),('con_notifytime',0),('r_drawplayersprites',False),('gl_texture_filter',0)]
 result=run_case(ENGINE,Path('F:/DoomDev/DOOM2.WAD'),root=C,mod=a.mod,addon=addon,mapname='CRTTEST',renderer=a.renderer,label=label,timeout=100,commands=cmd,settings=settings,quiet=True)
 log=Path(result['log']).read_text()
 result['shader_errors']=[s for s in ['Failed to compile','Unable to load shader','Shader compilation failed','Unable to open','Unknown texture','Missing texture'] if s in log]
 result['captures']=captures;result['materials']=[names[i] for i in selected]
 result['ok']=result['ok'] and (a.batch!=0 or result['assertions']==4) and not result['shader_errors'] and all((C/p).exists() and (C/p).stat().st_mtime>=started for p in captures)
 if result['ok'] and a.batch==0:
  import numpy as np
  from PIL import Image
  images={n:np.asarray(Image.open(C/'logs'/f'{label}-{n}.png'),dtype=float) for n in ['debug','noreflect','off','changed-room']}
  pane=(slice(150,400),slice(460,800));housing=(slice(470,590),slice(500,780))
  metrics={'crt_delta':float(np.abs(images['noreflect']-images['off'])[pane].mean()),'room_change_delta':float(np.abs(images['changed-room']-images['debug'])[pane].mean()),'housing_delta':float(np.abs(images['debug']-images['off'])[housing].max())}
  dark=np.asarray(Image.open(C/'logs'/f'{label}-fullbright-dark.png'),dtype=float)
  bright=np.asarray(Image.open(C/'logs'/f'{label}-fullbright-bright.png'),dtype=float)
  metrics['fullbright_glass_delta']=float(np.abs(dark-bright)[220:310,540:710].max())
  metrics['lit_housing_delta']=float(np.abs(dark-bright)[housing].mean())
  result['pixels']=metrics
  result['ok']=metrics['crt_delta']>.5 and metrics['room_change_delta']>.2 and metrics['housing_delta']==0 and metrics['fullbright_glass_delta']==0 and metrics['lit_housing_delta']>1
 out=C/'validation/crt';out.mkdir(exist_ok=True);(out/(label+'.json')).write_text(json.dumps(result,indent=2))
 print(json.dumps(result,indent=2))
 if not result['ok']:print(log[-6500:]);raise SystemExit(1)
if __name__=='__main__':main()
