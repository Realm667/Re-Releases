"""Render controlled base values to verify the CRT phosphor threshold in the engine."""
from pathlib import Path
import argparse,io,json,zipfile,time
import numpy as np
from PIL import Image
from test_crt_materials import ROOT,C,ENGINE,fixture
from check_engine import run_case

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--renderer',default='1');p.add_argument('--mod',type=Path,default=ROOT/'tutnt.pk3')
 p.add_argument('--packaged',action='store_true');a=p.parse_args()
 gallery,_=fixture(a.packaged)
 with zipfile.ZipFile(gallery) as z:entries={n:z.read(n) for n in z.namelist()}
 if a.packaged:
  with zipfile.ZipFile(a.mod) as z:
   shader=z.read('shaders/crt/screen.fp');bindings=z.read('gldefs/GLDEFS.crt')
 else:
  shader=(ROOT/'tutnt/shaders/crt/screen.fp').read_bytes();bindings=(ROOT/'tutnt/gldefs/GLDEFS.crt').read_bytes()
 assert b'CRT_PHOSPHOR_THRESHOLD = 0.25;' in shader
 entries['gldefs/GLDEFS.crt']=bindings.replace(b'CRT_BULGE = "0.0825"',b'CRT_BULGE = "0.0"')
 # Synthetic data, not a game-art replacement: two sub-threshold and two eligible bands.
 colors=[32,63,76,128];sample=Image.new('RGB',(64,64))
 for y in range(64):
  for x in range(64):
   v=colors[min(3,max(0,(x-2)//15))];sample.putpixel((x,y),(v,v,v))
 buf=io.BytesIO();sample.save(buf,format='PNG');entries['textures/Q2COMP4.png']=buf.getvalue()
 results=[];screens={}
 for mode in ['reference','threshold']:
  label=f'crt-threshold-r{a.renderer}-{mode}'
  entries['shaders/crt/screen.fp']=shader.replace(b'CRT_PHOSPHOR_THRESHOLD = 0.25;',b'CRT_PHOSPHOR_THRESHOLD = 1.1;') if mode=='reference' else shader
  addon=C/'builds'/(label+'.pk3')
  with zipfile.ZipFile(addon,'w',zipfile.ZIP_DEFLATED) as z:
   for name,data in entries.items():z.writestr(name,data)
  capture=C/'logs'/(label+'.png');started=time.time()
  commands=f'wait 240;screenblocks 12;UTNT_crtmotion false;UTNT_crtreflections false;gl_lights false;netevent crtpose 0 0;wait 3;netevent crtpose 0 0;wait 25;screenshot logs/{label}.png;echo UTNT_TEST_END;wait 3;quit'
  r=run_case(ENGINE,'F:/DoomDev/DOOM2.WAD',root=C,mod=a.mod,addon=addon,mapname='CRTTEST',renderer=a.renderer,label=label,commands=commands,timeout=70,quiet=True,settings=[('cl_capfps',True),('vid_scalemode',5),('vid_scale_customwidth',1280),('vid_scale_customheight',720),('vid_activeinbackground',True),('i_pauseinbackground',False),('use_mouse',False),('r_drawplayersprites',False),('con_notifytime',0),('gl_texture_filter',0)])
  r['ok']=r['ok'] and capture.is_file() and capture.stat().st_mtime>=started
  results.append(r)
  if not r['ok']:print(json.dumps(r));raise SystemExit(1)
  screens[mode]=np.asarray(Image.open(capture).convert('RGB'),dtype=float)
 delta=screens['threshold']-screens['reference']
 bands=[]
 for value,x in zip(colors,[480,585,690,795]):
  patch=delta[220:300,x-10:x+10]
  bands.append({'source':value/255,'max_absolute_change':float(abs(patch).max()),'mean_change':float(patch.mean())})
 housing=float(abs(delta)[470:590,500:780].max())
 dark_edge=float(abs(delta)[220:300,630:638].max())
 ok=all(r['ok'] for r in results) and all(b['max_absolute_change']==0 for b in bands[:2]) and all(b['mean_change']>2 for b in bands[2:]) and housing==0 and dark_edge==0
 out={'ok':ok,'renderer':a.renderer,'bands':bands,'housing_max_change':housing,'dark_edge_max_change':dark_edge,'runs':results}
 (C/'validation/crt').mkdir(parents=True,exist_ok=True)
 (C/'validation/crt'/f'threshold-r{a.renderer}.json').write_text(json.dumps(out,indent=2))
 print(json.dumps(out,indent=2))
 if not ok:raise SystemExit(1)
if __name__=='__main__':main()
