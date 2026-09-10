"""Build complete UTNT Unicode bitmap fonts from the mod's original artwork.

Standard library only. Existing shapes, widths, palette and offsets are retained;
new diacritics and ligatures are composed in the same pixel style. No system fonts.
"""
from dataclasses import dataclass
from pathlib import Path
import argparse, hashlib, json, struct, unicodedata, zlib
ROOT=Path(__file__).resolve().parent.parent
@dataclass
class Glyph:
    width:int
    height:int
    pixels:list
    left:int=0
    top:int=0
    def copy(self):return Glyph(self.width,self.height,self.pixels[:],self.left,self.top)

def read_patch(path):
    data=path.read_bytes();w,h,left,top=struct.unpack_from('<hhhh',data);pixels=[-1]*(w*h)
    for x in range(w):
        pos=struct.unpack_from('<I',data,8+x*4)[0]
        while data[pos]!=255:
            y,n=data[pos:pos+2];pos+=3
            for j in range(n):pixels[(y+j)*w+x]=data[pos+j]
            pos+=n+1
    return Glyph(w,h,pixels,left,top)

def read_fon2(path):
    data=path.read_bytes();assert data[:4]==b'FON2'
    height=struct.unpack_from('<H',data,4)[0];first,last,mono,shade,colors,flags=data[6:12]
    pos=12;kerning=0
    if flags&1:kerning=struct.unpack_from('<h',data,pos)[0];pos+=2
    widths=list(struct.unpack_from('<'+'H'*(1 if mono else last-first+1),data,pos));pos+=len(widths)*2
    if mono:widths*=last-first+1
    palette=[tuple(data[pos+i*3:pos+i*3+3]) for i in range(colors+1)];pos+=(colors+1)*3
    glyphs={}
    for code,width in zip(range(first,last+1),widths):
        if not width:continue
        pixels=[]
        while len(pixels)<width*height:
            run=data[pos];pos+=1
            if run<128:pixels.extend(data[pos:pos+run+1]);pos+=run+1
            elif run>128:pixels.extend([data[pos]]*(257-run));pos+=1
        if len(pixels)!=width*height:raise ValueError('Malformed FON2 run')
        glyphs[code]=Glyph(width,height,[i if i else -1 for i in pixels])
    return glyphs,palette,height,kerning

def bounds(glyph):
    points=[(i%glyph.width,i//glyph.width) for i,p in enumerate(glyph.pixels) if p>=0]
    if not points:return (0,0,0,0)
    return min(x for x,y in points),min(y for x,y in points),max(x for x,y in points)+1,max(y for x,y in points)+1

def crop(g):
    x,y,right,bottom=bounds(g)
    return Glyph(right-x,bottom-y,[g.pixels[j*g.width+i] for j in range(y,bottom) for i in range(x,right)])

def overlay(base,mark,x,y):
    # Expand upwards without moving the base glyph's baseline or horizontal advance.
    lo=min(0,y);hi=max(base.height,y+mark.height);width=max(base.width,x+mark.width)
    out=Glyph(width,hi-lo,[-1]*(width*(hi-lo)),base.left,base.top-lo)
    for glyph,dx,dy in ((base,0,-lo),(mark,x,y-lo)):
        for j in range(glyph.height):
            for i in range(glyph.width):
                value=glyph.pixels[j*glyph.width+i]
                if value>=0:out.pixels[(j+dy)*width+i+dx]=value
    return out

def mask(rows,palette,reference,scale=1,shadow=True):
    used=sorted(set(p for p in reference.pixels if p>=0),key=lambda p:sum(palette[p]))
    dark=used[max(0,len(used)//5)];mid=used[len(used)//2];light=used[-1]
    w=len(rows[0])*scale+(1 if shadow else 0);h=len(rows)*scale+(1 if shadow else 0)
    out=Glyph(w,h,[-1]*(w*h))
    points=[(x*scale+dx,y*scale+dy) for y,row in enumerate(rows) for x,c in enumerate(row) if c=='#' for dy in range(scale) for dx in range(scale)]
    if shadow:
        for x,y in points:out.pixels[(y+1)*w+x+1]=dark
    for x,y in points:out.pixels[y*w+x]=light if (x,y-1) not in points else mid
    return out

MARKS={
    '\u0300':['#.','.#'], '\u0301':['.#','#.'],
    '\u0302':['.#.','#.#'], '\u0308':['#.#'],
    '\u0303':['.##.','##.#'], '\u030a':['.#.','#.#','.#.'],
    '\u0327':['.#','#.'],
}

def extend(glyphs,palette,small):
    g={c:v.copy() for c,v in glyphs.items()}
    # STCFN121 is the legacy Doom pipe slot, not a lowercase y.
    if small and 121 in g:g[124]=g.pop(121)
    scale=1 if small else 2
    for char in 'ÀÁÂÃÄÅÇÈÉÊËÌÍÎÏÑÒÓÔÕÖÙÚÛÜÝŸ':
        decomposition=unicodedata.normalize('NFD',char);base=g[ord(decomposition[0])]
        mark=mask(MARKS[decomposition[1]],palette,base,scale,shadow=not small)
        # Small caps only have seven rows: a compact accent sits above the cap.
        left,top,right,bottom=bounds(base);x=max(0,(left+right-mark.width)//2)
        y=bottom if decomposition[1]=='\u0327' else top-mark.height-1
        g[ord(char)]=overlay(base,mark,x,y)
    for lig,left,right in [('Œ','O','E'),('Æ','A','E')]:
        a=g[ord(left)];b=g[ord(right)];g[ord(lig)]=overlay(a,b,max(1,a.width-(2 if small else 5)),0)
    sharp=mask(['.###..','#...#.','#..#..','#.##..','#...#.','#...#.','#.##..'],palette,g[ord('B')],scale)
    # Align the sharp-S cap with B, retaining a dedicated shape for German.
    top=bounds(g[ord('B')])[1];canvas=Glyph(sharp.width,max(g[ord('B')].height,top+sharp.height),[-1]*(sharp.width*max(g[ord('B')].height,top+sharp.height)))
    g[0x1e9e]=overlay(canvas,sharp,0,top);g[0xdf]=g[0x1e9e].copy()
    for code in list(g):
        char=chr(code);lower=char.lower()
        if len(lower)==1 and lower!=char:g[ord(lower)]=g[code].copy()
    for inv,base in [('¡','!'),('¿','?')]:
        a=g[ord(base)];g[ord(inv)]=Glyph(a.width,a.height,list(reversed(a.pixels)),a.left,a.top)
    for c,base in [('‘',"'"),('’',"'"),('“','"'),('”','"'),('„','"')]:
        original=g[ord(base)];mark=crop(original)
        if c in '‘“':mark.pixels=list(reversed(mark.pixels))
        y=bounds(g[ord('A')])[3]-mark.height if c=='„' else bounds(original)[1]
        canvas=Glyph(original.width,original.height,[-1]*(original.width*original.height),original.left,original.top)
        g[ord(c)]=overlay(canvas,mark,0,y)
    for c,base in [('«','<'),('»','>')]:
        a=g[ord(base)];g[ord(c)]=overlay(a,a,max(1,a.width//2),0)
    for c,base in [('–','-'),('—','-'),('−','-')]:
        a=g[ord(base)];g[ord(c)]=overlay(a,a,a.width-1 if c=='—' else max(1,a.width//2),0)
    a=g[ord('.')];g[0x2026]=overlay(overlay(a,a,a.width+1,0),a,2*(a.width+1),0)
    for c,base in [('{','('),('}',')'),('`',"'")]:
        if ord(c) not in g:g[ord(c)]=g[ord(base)].copy()
    if 124 not in g:
        a=g[ord('I')];g[124]=Glyph(2,a.height,[a.pixels[y*a.width+a.width//2+x] for y in range(a.height) for x in range(2)])
    g[ord('~')]=mask(MARKS['\u0303'],palette,g[ord('A')],scale)
    space=4 if small else glyphs[32].width
    for c in (' ','\u00a0','\u202f','\u2009'):g[ord(c)]=Glyph(space,1,[-1]*space)
    return g

def png(g,palette):
    def chunk(tag,data):return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data))
    rows=[]
    for y in range(g.height):
        row=bytearray([0])
        for p in g.pixels[y*g.width:(y+1)*g.width]:row.extend((*palette[p],255) if p>=0 else (0,0,0,0))
        rows.append(bytes(row))
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',g.width,g.height,8,6,0,0,0))+chunk(b'grAb',struct.pack('>ii',g.left,g.top))+chunk(b'IDAT',zlib.compress(b''.join(rows),9))+chunk(b'IEND',b'')

def outputs(root=ROOT):
    root=Path(root);raw=(root/'tools/font-sources/PLAYPAL.pal').read_bytes();smallpal=[tuple(raw[i:i+3]) for i in range(0,768,3)]
    small={int(p.stem[5:]):read_patch(p) for p in (root/'tutnt/graphics/fonts').glob('STCFN*.lmp')}
    big,palette,height,kern=read_fon2(root/'tools/font-sources/DBIGFONT.fon2')
    out={};manifest={'version':1,'fonts':{}}
    for name,source,pal,fh,kerning in [('smallfont',small,smallpal,11,0),('bigfont',big,palette,height,kern),('bigupper',big,palette,height,kern),('ucrbig',big,[tuple(min(255,round(v*1.8)) for v in color) for color in palette],height,kern)]:
        glyphs=extend(source,pal,name=='smallfont');records={}
        for code,glyph in sorted(glyphs.items()):
            rel=f'tutnt/fonts/{name}/{code:04X}.png';data=png(glyph,pal);out[rel]=data
            records[f'{code:04X}']={'sha256':hashlib.sha256(data).hexdigest(),'width':glyph.width,'height':glyph.height,'left':glyph.left,'top':glyph.top}
        info=f'FontHeight {fh}\nSpaceWidth {4 if name=="smallfont" else big[32].width}\nKerning {kerning}\n'
        out[f'tutnt/fonts/{name}/font.inf']=info.encode()
        manifest['fonts'][name]={'height':fh,'definition_sha256':hashlib.sha256(info.encode()).hexdigest(),'glyphs':records}
    out['tools/font-glyphs.json']=(json.dumps(manifest,indent=2)+'\n').encode()
    return out

def build(root=ROOT,check=False):
    root=Path(root);data=outputs(root);errors=[]
    for rel,value in data.items():
        path=root/rel
        if check:
            if not path.exists() or path.read_bytes()!=value:errors.append(rel)
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(value)
    if errors:raise ValueError('Font assets need rebuilding: '+', '.join(errors[:20]))
    return {'files':len(data),'fonts':4}
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');a=parser.parse_args()
    print(json.dumps(build(check=a.check)))
