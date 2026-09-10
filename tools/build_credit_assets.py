"""Rebuild the private title font and approved Quake-Reliquiar frames (Pillow required).
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
# Rebuild the extended original and bright credit fonts together.
from build_localized_fonts import build as build_fonts
build_fonts()


def build_reliquiar_frames():
 """Render the exact variant-01 bevel, grain, inset and rivets at 2x resolution."""
 from PIL import ImageDraw
 def rgb(color):return tuple(bytes.fromhex(color.lstrip('#')))
 def blend(stops,t):
  for (a,ca),(b,cb) in zip(stops,stops[1:]):
   if t<=b:return tuple(round(x+(y-x)*(t-a)/(b-a)) for x,y in zip(rgb(ca),rgb(cb)))
  return rgb(stops[-1][1])
 for remaster in [False,True]:
  for shape,(w,h) in {'S':(328,74),'D':(286,74),'C':(530,140),'P':(328,164)}.items():
   scale=2;W,H=w*scale,h*scale
   im=Image.new('RGBA',(W,H));mask=Image.new('L',(W,H));draw=ImageDraw.Draw(mask)
   points=[(7,0),(w-7,0),(w,7),(w,h-7),(w-7,h),(7,h),(0,h-7),(0,7)]
   points=[(x*scale,y*scale) for x,y in points];draw.polygon(points,fill=255)
   colors=[(0,'#a9b7b8' if remaster else '#a3875d'),(.14,'#302920'),(.57,'#65533c'),(1,'#1b1714')]
   pixels=im.load()
   for yy in range(H):
    for xx in range(W):pixels[xx,yy]=blend(colors,(xx*w+yy*h)/(scale*(w*w+h*h)))+(255,)
   im.putalpha(mask);draw=ImageDraw.Draw(im);draw.line(points+[points[0]],fill='#17130f',width=4)
   overlay=Image.new('RGBA',im.size);d=ImageDraw.Draw(overlay)
   d.rectangle((10,10,W-11,H-11),fill=(7,8,7,199));im=Image.alpha_composite(im,overlay);draw=ImageDraw.Draw(im)
   edge='#536c71' if remaster else '#685033';accent='#b9c6c7' if remaster else '#bd9561'
   draw.rectangle((15,15,W-16,H-16),outline=edge,width=2)
   overlay=Image.new('RGBA',im.size);d=ImageDraw.Draw(overlay)
   for j in range(w//5):
    xx=10+(j*73)%(w-20);yy=1+j%3;color=rgb('#d8bc83' if j%2 else '#080806')+(31,)
    d.rectangle((xx*2,yy*2,(xx+2+j%5)*2-1,yy*2+1),fill=color)
   im=Image.alpha_composite(im,overlay);draw=ImageDraw.Draw(im)
   for xx in [6,w-10]:
    for yy in [7,h-11]:
     draw.rectangle((xx*2,yy*2,xx*2+5,yy*2+5),fill=accent)
     draw.rectangle((xx*2+2,yy*2+2,xx*2+3,yy*2+3),fill='#201912')
   draw.line((40,7,W-40,7),fill=accent,width=2)
   im.save(assets/(('UCRRS' if remaster else 'UCRRB')+shape+'.png'))

build_reliquiar_frames()
