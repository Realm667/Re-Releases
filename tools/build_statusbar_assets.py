"""Rebuild the tiny paletted status-bar patches; no imaging dependencies.

The gas cylinder follows the approved 8x7 pixel mockup. Fixed Doom palette
indices preserve PLAYPAL flashes and palette replacements at runtime.
The four original ammo miniatures and the stone are composed in TEXTURES.txt.
"""
import argparse
from pathlib import Path
import struct


def doom_patch(rows, colors):
    """Encode top-left-anchored column posts; '.' denotes transparency."""
    width, height = len(rows[0]), len(rows)
    assert all(len(row) == width for row in rows)
    posts, offsets = bytearray(), []
    for x in range(width):
        offsets.append(8 + 4 * width + len(posts))
        y = 0
        while y < height:
            if rows[y][x] == '.':
                y += 1
                continue
            start, column = y, bytearray()
            while y < height and rows[y][x] != '.':
                column.append(colors[rows[y][x]])
                y += 1
            posts.extend(bytes([start, len(column), 0]) + column + b'\0')
        posts.append(255)
    return struct.pack('<hhhh', width, height, 0, 0) + struct.pack('<'+'I'*width, *offsets) + posts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    target = args.root / 'tutnt/graphics/sbar'
    target.mkdir(parents=True, exist_ok=True)
    assets = {
        'UTNHGAS': (
            ['...ss...', '..shs...', '.dmmmd..', '.mlolmd.', '.mllomd.', '.dsssd..', '..ddd...'],
            {'s': 95, 'h': 87, 'd': 158, 'm': 69, 'l': 212, 'o': 65}),
        'UTNHADIV': (['ds'] * 24, {'d': 239, 's': 149}),
        'UTNHASLH': (['.s', '.s', 's.', 's.'], {'s': 95}),
    }
    for name, (rows, colors) in assets.items():
        data = doom_patch(rows, colors)
        path = target / (name + '.lmp')
        path.write_bytes(data)
        print(f'{name}: {len(rows[0])}x{len(rows)}, {len(data)} bytes')


if __name__ == '__main__':
    main()
