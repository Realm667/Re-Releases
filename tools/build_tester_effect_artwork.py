"""Reproduce stable shader frame samples and pack the selected poison sprite sheet.
Source artwork is retained under tools/artwork/tester-effects; no AI generation runs here.
"""
from pathlib import Path
import argparse,io,struct
from PIL import Image,PngImagePlugin
from build_custom_brightmaps import Artwork,png
ROOT=Path(__file__).resolve().parents[1]
def generate(root=ROOT,check=False,iwad=Path('F:/DoomDev/DOOM2.WAD')):
 ROOT=Path(root)
 art=Artwork(ROOT,iwad); outputs={}
 for name in ('FIRELAVA','FIRELAV2','FIRELAV3','FIREWALL','FIREWALA','FIREWALB'):
  outputs[ROOT/f'tutnt/materials/fire-surfaces/{name.lower()}.png']=png(art.image(name))
 sheet=Image.open(ROOT/'tools/artwork/tester-effects/poison-spores-source.png').convert('RGBA')
 assert sheet.size==(1536,1024)
 for i in range(8):
  x=(i%4)*384;y=(i//4)*512
  frame=sheet.crop((x,y,x+384,y+512)).resize((96,128),Image.Resampling.LANCZOS)
  info=PngImagePlugin.PngInfo();info.add(b'grAb',struct.pack('>ii',48,64));out=io.BytesIO()
  frame.save(out,format='PNG',pnginfo=info,optimize=True)
  outputs[ROOT/f'tutnt/sprites/projs/poison/UPZN{chr(65+i)}0.png']=out.getvalue()
 for path,data in outputs.items():
  if check:
   if not path.exists() or path.read_bytes()!=data:raise ValueError('Stale effect artwork: '+str(path))
  else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
 print(f'{len(outputs)} effect artwork files '+('verified' if check else 'written'))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');p.add_argument('--iwad',type=Path,default=Path('F:/DoomDev/DOOM2.WAD'));a=p.parse_args();generate(check=a.check,iwad=a.iwad)
