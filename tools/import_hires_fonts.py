"""Import the authored font atlases into portable 2x glyph sources (Pillow).

The regular font builder is standard-library only and consumes the JSON outputs.
Atlas cells are ASCII 33..95, in eight columns, with the last cell empty.
"""
from dataclasses import asdict
from pathlib import Path
import json
from PIL import Image
import build_localized_fonts as b


def unkey(image):
    """Extract coverage and remove magenta spill before resampling."""
    result=Image.new('RGBA',image.size)
    pixels=[]
    for r,g,blue in image.convert('RGB').getdata():
        alpha=255-max(0,min(r,blue)-g)
        if alpha<32:
            pixels.append((0,0,0,0))
        else:
            spill=255-alpha
            pixels.append((max(0,min(255,round((r-spill)*255/alpha))),
                           min(255,round(g*255/alpha)),
                           max(0,min(255,round((blue-spill)*255/alpha))),alpha))
    result.putdata(pixels)
    return result


def main():
    target=b.ROOT/'tools/font-sources/hires'
    big,bigpal,_,_=b.read_fon2(b.ROOT/'tools/font-sources/DBIGFONT.fon2')
    raw=(b.ROOT/'tools/font-sources/PLAYPAL.pal').read_bytes()
    smallpal=[tuple(raw[i:i+3]) for i in range(0,768,3)]
    small={int(p.stem[5:]):b.read_patch(p) for p in (b.ROOT/'tutnt/graphics/fonts').glob('STCFN*.lmp')}
    for name,original,oldpal in [('bigfont',big,bigpal),('smallfont',small,smallpal)]:
        atlas=unkey(Image.open(target/f'{name}-atlas.png'))
        palette=[];indices={};glyphs={}
        for code,g in original.items():
            canvas=Image.new('RGBA',(g.width*2,g.height*2))
            if 33<=code<=95:
                i=code-33;x=i%8;y=i//8
                cell=atlas.crop((round(x*atlas.width/8),round(y*atlas.height/8),
                                 round((x+1)*atlas.width/8),round((y+1)*atlas.height/8)))
                box=cell.getchannel('A').getbbox()
                if box is None:raise ValueError(f'{name}: blank atlas cell {code:04X}')
                left,top,right,bottom=b.bounds(g)
                glyph=cell.crop(box).resize(((right-left)*2,(bottom-top)*2),Image.Resampling.LANCZOS)
                canvas.paste(glyph,(left*2,top*2))
            else:
                image=Image.new('RGBA',(g.width,g.height))
                image.putdata([(*oldpal[p],255) if p>=0 else (0,0,0,0) for p in g.pixels])
                canvas=image.resize(canvas.size,Image.Resampling.NEAREST)
            pixels=[]
            for color in canvas.getdata():
                if color[3]<8:
                    pixels.append(-1);continue
                if color not in indices:
                    indices[color]=len(palette);palette.append(color)
                pixels.append(indices[color])
            glyphs[f'{code:04X}']=asdict(b.Glyph(canvas.width,canvas.height,pixels,g.left*2,g.top*2))
        (target/f'{name}.json').write_text(json.dumps({'version':1,'scale':2,'palette':palette,'glyphs':glyphs},separators=(',',':'))+'\n',encoding='utf-8')
        print(f'{name}: {len(glyphs)} source glyphs, {len(palette)} RGBA colors')


if __name__=='__main__':main()
