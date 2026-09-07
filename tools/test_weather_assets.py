"""Reject multi-particle precipitation textures in the source tree or a built PK3."""
from pathlib import Path
import argparse,io,json,zipfile
from PIL import Image

ROOT=Path(__file__).resolve().parent.parent
PREFIX='graphics/utnt-weather/'
EXPECTED={'rain.png','snow0.png','snow1.png','snow2.png','ripple.png'}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mod',type=Path)
    args=parser.parse_args()
    if args.mod:
        with zipfile.ZipFile(args.mod) as z:
            data={n[len(PREFIX):]:z.read(n) for n in z.namelist() if n.startswith(PREFIX) and n.endswith('.png')}
    else:
        data={p.name:p.read_bytes() for p in (ROOT/'tutnt'/PREFIX).glob('*.png')}
    assert set(data)==EXPECTED,{'unexpected':sorted(set(data)-EXPECTED),'missing':sorted(EXPECTED-set(data))}
    result={}
    for name in sorted(EXPECTED-{'ripple.png'}):
        im=Image.open(io.BytesIO(data[name])).convert('RGBA')
        alpha=im.getchannel('A');points={(x,y) for y in range(im.height) for x in range(im.width) if alpha.getpixel((x,y))>32}
        components=0
        while points:
            components+=1;todo=[points.pop()]
            while todo:
                x,y=todo.pop()
                for dx in (-1,0,1):
                    for dy in (-1,0,1):
                        p=(x+dx,y+dy)
                        if p in points:points.remove(p);todo.append(p)
        assert components==1,(name,components)
        result[name]={'visible_components':components,'size':im.size}
    print(json.dumps({'ok':True,'precipitation':result,'asset_count':len(data)}))

if __name__=='__main__':main()
