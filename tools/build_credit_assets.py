"""Rebuild private DBIGFONT palette and tiny credit shading textures (Pillow required).
Body, headings and controls use the existing Quake SMALLFONT directly.
"""
from pathlib import Path
from PIL import Image
T=Path(__file__).resolve().parent.parent/'tutnt'
assets=T/'graphics/credits';assets.mkdir(exist_ok=True)
def lerp(stops,x):
 for (a,va),(b,vb) in zip(stops,stops[1:]):
  if x<=b:return va+(vb-va)*(x-a)/(b-a)
 return stops[-1][1]
for name,size,stops in [('UCRSHADE',(256,1),[(0,.82),(.43,.82*.84),(.76,.18),(1,.10)]),('UCRVEIL',(1,256),[(0,.45),(.30,0),(.72,0),(1,.70)])]:
 image=Image.new('RGBA',size)
 for i in range(256):image.putpixel((i,0) if size[0]>1 else (0,i),(0,0,0,round(lerp(stops,i/255)*255)))
 image.save(assets/(name+'.png'))
# Native FON2 fonts: preserve DBIGFONT's artwork; only brighten its private palette.
big=bytearray((T/'DBIGFONT.fon2').read_bytes());p=12+(2 if big[11]&1 else 0);p+=2*(1 if big[8] else big[7]-big[6]+1)
for i in range(p,p+(big[10]+1)*3):big[i]=min(255,round(big[i]*1.8))
(T/'UCRBIG.fon2').write_bytes(big)
