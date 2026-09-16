"""Exact-pixel PNG storage helpers. Keep Doom offsets, palettes and ancillary data."""
import io
import struct
import zlib
from pathlib import Path
from PIL import Image

SIGNATURE = b'\x89PNG\r\n\x1a\n'

def chunks(data):
    if not data.startswith(SIGNATURE):
        raise ValueError('Not a PNG')
    result = []
    pos = 8
    while pos + 12 <= len(data):
        size = struct.unpack_from('>I', data, pos)[0]
        end = pos + 12 + size
        if end > len(data):
            raise ValueError('Truncated PNG chunk')
        kind, payload = data[pos+4:pos+8], data[pos+8:end-4]
        crc = struct.unpack_from('>I', data, end-4)[0]
        result.append((kind, payload, crc == zlib.crc32(kind+payload) & 0xffffffff))
        pos = end
        if kind == b'IEND':
            if pos != len(data):
                raise ValueError('Trailing PNG data')
            return result
    raise ValueError('Missing IEND')

def encode(parts):
    return SIGNATURE + b''.join(struct.pack('>I', len(value)) + kind + value +
        struct.pack('>I', zlib.crc32(kind+value) & 0xffffffff) for kind, value in parts)

def normalized(data):
    """Repair container checksums in memory only, without changing any payload."""
    return encode((k,v) for k,v,_ in chunks(data))

def decoded(data):
    parts = chunks(data)
    if any(k == b'acTL' for k,_,_ in parts):
        raise ValueError('APNG requires frame-aware verification')
    header = parts[0][1]
    if header[8] == 16:
        raise ValueError('16-bit PNG requires full-depth verification')
    with Image.open(io.BytesIO(normalized(data))) as im:
        im.load()
        return im.size, im.convert('RGBA').tobytes(), im.tobytes() if im.mode == 'P' else None

def equivalent(original, candidate):
    a, b = chunks(original), chunks(candidate)
    # Pixel data, palette order, offsets, profiles, text and every private chunk
    # are retained. Only storage header, IDAT framing and checksums may change.
    ancillary = lambda cs: [(k,v) for k,v,_ in cs if k not in (b'IHDR',b'IDAT',b'IEND')]
    if ancillary(a) != ancillary(b):
        return False
    if a[0][1][:8] != b[0][1][:8]:
        return False
    return decoded(original) == decoded(candidate)

def preserve_png(path, generated):
    """An explicit generator retains an already smaller equivalent encoding."""
    path = Path(path)
    if path.suffix.lower() != '.png' or not path.is_file():
        return generated
    current = path.read_bytes()
    if len(current) < len(generated):
        try:
            if equivalent(generated, current):
                return current
        except (ValueError, OSError):
            pass
    return generated

def restore_chunks(original, candidate):
    """Reattach original metadata in original order; require identical palette."""
    before, after = chunks(original), chunks(candidate)
    ap = [v for k,v,_ in before if k == b'PLTE']
    bp = [v for k,v,_ in after if k == b'PLTE']
    if ap != bp:
        raise ValueError('Optimizer changed palette indices')
    header = next(v for k,v,_ in after if k == b'IHDR')
    data = b''.join(v for k,v,_ in after if k == b'IDAT')
    result = []; inserted = False
    for k,v,_ in before:
        if k == b'IHDR': v = header
        elif k == b'IDAT':
            if inserted: continue
            v = data; inserted = True
        result.append((k,v))
    return encode(result)


def save_png(image, path, **options):
    """Explicit authoring helper that keeps a smaller equivalent PNG on disk."""
    out = io.BytesIO()
    image.save(out, format="PNG", **options)
    path = Path(path)
    data = preserve_png(path, out.getvalue())
    if not path.exists() or path.read_bytes() != data:
        path.write_bytes(data)
