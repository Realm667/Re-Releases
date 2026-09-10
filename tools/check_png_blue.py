"""Verify reviewed PNG blue colors, unchanged pixels, alpha, offsets and PK3 bytes.

Source blobs are read from Git history, never from a mutable baseline directory.
Pillow and NumPy are used for lossless pixel comparisons. Historical invalid grAb
CRCs are normalized only in the in-memory decoder; file metadata stays untouched.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import struct
import subprocess
import zipfile
import zlib

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def chunks(raw):
    assert raw[:8] == b'\x89PNG\r\n\x1a\n'
    offset = 8
    while offset < len(raw):
        size = struct.unpack_from('>I', raw, offset)[0]
        assert offset + size + 12 <= len(raw)
        yield raw[offset+4:offset+8], raw[offset+8:offset+8+size], raw[offset:offset+12+size]
        offset += 12 + size
    assert offset == len(raw)


def decode(raw):
    normalized = raw[:8]
    for kind, data, block in chunks(raw):
        normalized += block[:-4] + struct.pack('>I', zlib.crc32(kind + data))
    result = Image.open(io.BytesIO(normalized))
    result.load()
    return result


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pk3', type=Path)
    parser.add_argument('--require-current-palette', action='store_true',
                        help='Also compare the locally active PLAYPAL blue entries.')
    args = parser.parse_args()
    fixture = json.loads((ROOT/'tools/fixtures/png-blue.json').read_text(encoding='utf-8'))
    if args.require_current_palette:
        palette = (ROOT/'tutnt/PLAYPAL.pal').read_bytes()
        for index, color in fixture['palette_blue'].items():
            index = int(index)
            assert list(palette[index*3:index*3+3]) == color, ('PLAYPAL changed', index)
    # One batch avoids launching hundreds of Git processes on Windows.
    request = ''.join(entry['source_blob']+'\n' for entry in fixture['assets']).encode()
    sources = io.BytesIO(subprocess.check_output(['git', 'cat-file', '--batch'], input=request, cwd=ROOT))
    archive = zipfile.ZipFile(args.pk3) if args.pk3 else None
    total = 0
    try:
        for entry in fixture['assets']:
            name = entry['path']
            header = sources.readline().split()
            assert len(header) == 3 and header[1] == b'blob', name
            original = sources.read(int(header[2]))
            assert sources.read(1) == b'\n'
            current = (ROOT/name).read_bytes()
            assert digest(original) == entry['source_sha256'], name
            assert digest(current) == entry['result_sha256'], name
            before, after = decode(original), decode(current)
            assert before.mode == after.mode == entry['mode'], name
            assert before.size == after.size, name
            a, b = np.array(before.convert('RGBA')), np.array(after.convert('RGBA'))
            assert np.array_equal(a[:, :, 3], b[:, :, 3]), ('alpha', name)
            changed = np.any(a[:, :, :3] != b[:, :, :3], axis=2)
            assert int(changed.sum()) == entry['pixels'], name
            assert not np.any(changed & (a[:, :, 3] == 0)), ('transparent pixels', name)
            assert not np.any(changed & ((a[:, :, 2] <= a[:, :, 0]) |
                                         (a[:, :, 2] <= a[:, :, 1]))), ('non-blue pixels', name)
            # Includes IHDR, grAb offsets, transparency keys and color profiles.
            mutable = b'PLTE' if before.mode == 'P' else b'IDAT'
            assert [block for kind, _, block in chunks(original) if kind != mutable] == [
                block for kind, _, block in chunks(current) if kind != mutable], ('metadata/index data', name)
            if before.mode == 'P':
                assert np.array_equal(np.array(before), np.array(after)), ('palette indices', name)
            if archive:
                assert archive.read(name.removeprefix('tutnt/')) == current, ('package', name)
            total += entry['pixels']
    finally:
        if archive:
            archive.close()
    print(json.dumps({'ok': True, 'assets': len(fixture['assets']), 'changed_blue_pixels': total,
                      'alpha_offsets_nonblue_unchanged': True, 'package_checked': bool(args.pk3)}))


if __name__ == '__main__':
    main()
