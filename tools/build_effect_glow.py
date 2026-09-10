"""Reproduce the analytic halo sprite (and shader-free fallback) without artwork dependencies."""
from pathlib import Path
import argparse, math, struct, zlib

ROOT = Path(__file__).resolve().parent.parent


def sprite():
    def chunk(kind, data):
        return struct.pack('>I', len(data))+kind+data+struct.pack('>I', zlib.crc32(kind+data)&0xffffffff)
    raw = bytearray()
    for y in range(64):
        raw.append(0)
        for x in range(64):
            r2 = ((x+.5-32)/32)**2+((y+.5-32)/32)**2
            edge = max(0, min(1, (r2-.64)/.36))
            edge = 1-edge*edge*(3-2*edge)
            alpha = round(255*(.72*math.exp(-5.5*r2)+.28*math.exp(-18*r2))*edge)
            raw.extend((255,255,255,alpha))
    return (b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR', struct.pack('>IIBBBBB',64,64,8,6,0,0,0))
            +chunk(b'grAb', struct.pack('>ii',32,32))
            +chunk(b'IDAT', zlib.compress(bytes(raw),9))+chunk(b'IEND', b''))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    target = ROOT/'tutnt/sprites/effect-glow/UGLWA0.png'
    data = sprite()
    if args.check:
        if not target.is_file() or target.read_bytes()!=data:
            raise SystemExit('Halo sprite differs from its analytic source')
        print('Halo sprite matches its analytic source')
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
