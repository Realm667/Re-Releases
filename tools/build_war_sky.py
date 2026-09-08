"""Generate TNT04A's sky from the exact current caldera shaders and textures.
The shared panorama, terrain, exposure and cloud motion remain identical.
Run again after changing the caldera shaders. No new raster artwork required.
"""
from pathlib import Path
import argparse
ROOT=Path(__file__).resolve().parent.parent
def build(root):
 out=root/'tutnt';effect=Path(__file__).with_name('war-comets.glsl').read_text()
 gl=['skybox UWRSKY { '+' '.join('UWR'+f for f in 'NESWUD')+' }'];textures=[]
 for f in 'NESWUD':
  base=(out/f'shaders/caldera/sky-{f}.fp').read_text()
  anchor='mat.Base=vec4(color*mix(0.9,0.70,canopy)*0.985,1.0);'
  assert base.count(anchor)==1
  text=effect+'\n'+base.replace(anchor,'mat.Base=vec4(WarComets(color*mix(0.9,0.70,canopy)*0.985,r),1.0);')
  dest=out/f'shaders/caldera-war/sky-{f}.fp';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(text,newline='\n')
  gl.append(f'material texture UWR{f} {{ shader "shaders/caldera-war/sky-{f}.fp" texture cloudmap "graphics/caldera/panorama.png" }}')
  textures.append(f'Texture UWR{f}, 768, 768 {{ Patch "textures/UCH{f}.png", 0, 0 }}')
 (out/'GLDEFS.caldera-war').write_text('\n'.join(gl)+'\n',newline='\n')
 (out/'TEXTURES.caldera-war').write_text('\n'.join(textures)+'\n',newline='\n')
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);build(p.parse_args().root)
