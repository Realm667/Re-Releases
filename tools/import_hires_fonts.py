"""Import the authored font atlases into portable 2x glyph sources (Pillow).

The regular font builder is standard-library only and consumes the JSON outputs.
Atlas cells are ASCII 33..95, in eight columns; the final cell contains ß.
"""
from dataclasses import asdict
from pathlib import Path
import argparse, json
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
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font',choices=['bigfont','smallfont'])
    args=parser.parse_args()
    target=b.ROOT/'tools/font-sources/hires'
    big,bigpal,_,_=b.read_fon2(b.ROOT/'tools/font-sources/DBIGFONT.fon2')
    raw=(b.ROOT/'tools/font-sources/PLAYPAL.pal').read_bytes()
    smallpal=[tuple(raw[i:i+3]) for i in range(0,768,3)]
    small={int(p.stem[5:]):b.read_patch(p) for p in (b.ROOT/'tutnt/graphics/fonts').glob('STCFN*.lmp')}
    for name,original,oldpal in [('bigfont',big,bigpal),('smallfont',small,smallpal)]:
        if args.font and args.font!=name:continue
        atlas=unkey(Image.open(target/f'{name}-atlas.png'))
        palette=[];indices={};glyphs={}
        imported=dict(original)
        imported[0xdf]=b.extend(original,oldpal,name=='smallfont')[0xdf]
        for code,g in imported.items():
            canvas=Image.new('RGBA',(g.width*2,g.height*2))
            if 33<=code<=95 or code==0xdf:
                i=63 if code==0xdf else code-33;x=i%8;y=i//8
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
        palette=b.original_color_palette({int(c,16):b.Glyph(**g) for c,g in glyphs.items()},palette,original,oldpal)
        overrides={'00DF':glyphs.pop('00DF')}
        overrides['1E9E']=overrides['00DF']
        result={'version':1,'scale':2,'palette':palette,'glyphs':glyphs}
        if overrides:result['overrides']=overrides
        (target/f'{name}.json').write_text(json.dumps(result,separators=(',',':'))+'\n',encoding='utf-8')
        print(f'{name}: {len(glyphs)} source glyphs, {len(palette)} RGBA colors')


if __name__=='__main__':main()
