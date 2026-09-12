"""Export the approved sealed-skull menu selector at native and 2x resolution."""
import argparse
import struct
from pathlib import Path

import numpy as np
from PIL import Image, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/artwork/menu-skulls/pixel-source.png"
SIZE = (25, 19)
OFFSET = (5, -3)


def source_frames():
    sheet = Image.open(SOURCE).convert("RGBA")
    frames = []
    for left, right in ((0, sheet.width // 2), (sheet.width // 2, sheet.width)):
        frame = sheet.crop((left, 0, right, sheet.height))
        # Ignore faint extraction fringes when measuring the sprite.
        frame.putalpha(frame.getchannel("A").point(lambda a: 255 if a >= 128 else 0))
        box = frame.getbbox()
        if box is None:
            raise ValueError("Empty skull artwork")
        frames.append(frame.crop(box))
    return frames


def render(scale):
    dim, lit = source_frames()
    size = (SIZE[0] * scale, SIZE[1] * scale)
    dim.thumbnail(size, Image.Resampling.LANCZOS)
    lit = lit.resize(dim.size, Image.Resampling.LANCZOS)
    a, b = np.array(dim), np.array(lit)
    # Animation changes illumination only: keep the approved dim frame's
    # geometry and all non-emissive shading fixed in both frames.
    rgb = b[:, :, :3].astype(np.int16)
    glow = ((rgb[:, :, 0] > 140) & (rgb[:, :, 1] > 90)
            & (rgb[:, :, 2] * 2 < rgb[:, :, 1])
            & (rgb[:, :, 1] > a[:, :, 1].astype(np.int16) + 25))
    bright = a.copy()
    bright[glow, :3] = b[glow, :3]
    palette = Image.new("P", (1, 1))
    palette.putpalette((ROOT / "tutnt/PLAYPAL.pal").read_bytes()[:768])
    frames = []
    for pixels in (a, bright):
        canvas = Image.new("RGBA", size)
        canvas.paste(Image.fromarray(pixels),
                     ((size[0] - dim.width) // 2, (size[1] - dim.height) // 2))
        result = canvas.convert("RGB").quantize(
            palette=palette, dither=Image.Dither.NONE).convert("RGBA")
        result.putalpha(canvas.getchannel("A").point(lambda a: 255 if a >= 112 else 0))
        frames.append(result)
    return frames


def read_offsets(path):
    data = path.read_bytes()
    position = 8
    while position + 12 <= len(data):
        length = struct.unpack_from(">I", data, position)[0]
        if data[position + 4:position + 8] == b"grAb":
            return struct.unpack_from(">ii", data, position + 8)
        position += length + 12
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for scale, folder in ((1, "graphics/fonts"), (2, "hires/graphics")):
        frames = render(scale)
        assert frames[0].getchannel("A").tobytes() == frames[1].getchannel("A").tobytes()
        assert frames[0].tobytes() != frames[1].tobytes()
        offset = tuple(value * scale for value in OFFSET)
        for number, frame in enumerate(frames, 1):
            path = ROOT / "tutnt" / folder / f"M_SKULL{number}.png"
            if args.check:
                existing = Image.open(path)
                if (existing.size != frame.size
                        or existing.convert("RGBA").tobytes() != frame.tobytes()
                        or read_offsets(path) != offset):
                    raise SystemExit(f"{path} is stale; run tools/build_menu_skulls.py")
                print(f"{path.relative_to(ROOT)}: pixels, alpha and offsets verified")
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                metadata = PngImagePlugin.PngInfo()
                metadata.add(b"grAb", struct.pack(">ii", *offset))
                frame.save(path, pnginfo=metadata, optimize=True)
                print(path)


if __name__ == "__main__":
    main()
