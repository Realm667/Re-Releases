"""Decode original Doom patches with their captured PLAYPAL; recolor only rune ink.

No quantization or generated glyph artwork. Pillow writes truecolor RGBA PNGs.
The captured inputs make rebuilding independent of later PLAYPAL changes.
"""
from pathlib import Path
import struct,math,json,hashlib
from PIL import Image
R=Path(__file__).resolve().parent.parent
SOURCE=R/'tools/artwork/portal-runes/source'
RAMP=[(0.0,(48,8,1)),(.30,(156,42,4)),(.60,(245,101,10)),(.82,(255,158,30)),(1.0,(255,205,83))]
def decode(raw,palette):
 w,h,left,top=struct.unpack_from('<HHhh',raw)
 pixels=bytearray(w*h*4)
 for x in range(w):
  off=struct.unpack_from('<I',raw,8+4*x)[0];prev=-1
  while raw[off]!=255:
   y,n=raw[off],raw[off+1]
   if y<=prev:y+=prev
   prev=y
   for j,c in enumerate(raw[off+3:off+3+n]):
    if y+j<h:
     k=((y+j)*w+x)*4;pixels[k:k+4]=palette[c*3:c*3+3]+b'\xff'
   off+=n+4
 return Image.frombytes('RGBA',(w,h),bytes(pixels))
def ink(pixel):
 r,g,b,a=pixel
 return max(0,r-max(g,b))/255 if a and r>max(g,b)*1.8 else 0
def color(t):
 t=max(0,min(1,t))
 for (a,ca),(b,cb) in zip(RAMP,RAMP[1:]):
  if t<=b:return tuple(round(x+(y-x)*(t-a)/(b-a)) for x,y in zip(ca,cb))
 return RAMP[-1][1]
def main():
 palette=(SOURCE/'PLAYPAL.pal').read_bytes()[:768]
 dest=R/'tutnt/graphics/utnt-runes';dest.mkdir(parents=True,exist_ok=True)
 report={}
 for name in ['QRUNT61','QRUNT62','QRUNT63']:
  raw=(SOURCE/(name+'.lmp')).read_bytes();original=decode(raw,palette)
  original.save(SOURCE.parent/(name+'-decoded.png'))
  data=list(original.getdata());strength=[ink(c) for c in data];peak=max(strength) or 1
  rgba=[];bright=[]
  for i,(pixel,s) in enumerate(zip(data,strength)):
   x,y=i%original.width,i//original.width
   if name!='QRUNT61' and s>0:
    # Restore a continuous thermal ramp within the original mask; subtle spatial
    # modulation avoids reproducing the old palette's discrete color bands.
    # Narrow hot cores, orange edges: most of the glyph must not become flat
    # yellow merely because the source used one saturated red palette entry.
    distance=5.0
    for dy in range(-4,5):
     for dx in range(-4,5):
      nx,ny=x+dx,y+dy
      if nx<0 or nx>=original.width or ny<0 or ny>=original.height or not strength[ny*original.width+nx]:
       distance=min(distance,math.hypot(dx,dy))
    core=max(0,min(1,(distance-.8)/2.8))
    heat=max(0,min(1,(s/peak)**.8*(.50+.47*core)+.035*math.sin(x*.63+y*.27)))
    rgba.append(color(heat)+(pixel[3],))
   else:rgba.append(pixel)
   v=round(255*min(1,s*3.0));bright.append((v,v,v,255))
  result=Image.new('RGBA',original.size);result.putdata(rgba)
  target=R/'tutnt/textures'/(name+'.png');result.save(target)
  assert target.read_bytes()[25]==6,'PNG must be truecolor RGBA, not indexed'
  assert result.getchannel('A').tobytes()==original.getchannel('A').tobytes()
  assert all(a==b for a,b,s in zip(data,rgba,strength) if not s or name=='QRUNT61')
  if name!='QRUNT61':
   mask=Image.new('RGBA',original.size);mask.putdata(bright);mask.save(dest/(name+'-mask.png'))
  palette_colors={tuple(palette[i:i+3]) for i in range(0,768,3)}
  newcolors={p[:3] for p,s in zip(rgba,strength) if s and p[:3] not in palette_colors}
  report[name]={'size':original.size,'mode':result.mode,'original_sha256':hashlib.sha256(raw).hexdigest(),
   'recolored_pixels':sum(s>0 for s in strength) if name!='QRUNT61' else 0,'new_colors_outside_palette':len(newcolors)}
 (SOURCE.parent/'conversion.json').write_text(json.dumps({'palette_sha256':hashlib.sha256(palette).hexdigest(),'ramp':RAMP,'textures':report},indent=2)+'\n')
 print(json.dumps(report))
if __name__=='__main__':main()
